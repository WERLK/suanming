# 玄机算命网 v2 重构报告

## 一、重构背景与目标

### 1.1 旧版痛点

| 问题 | 影响 |
|------|------|
| **api/app.py 3458 行** 单体文件，76 个路由 + 全部业务逻辑 | 任何修改都需全量回归，多人协作冲突极高 |
| **api/fortune_service.py 2745 行** 单体服务 | 算法逻辑无法独立测试、复用 |
| **双套用户系统并存**（app.py JSON + app_with_db.py SQLAlchemy） | 维护成本翻倍，app_with_db.py 为死代码 |
| **JWT 硬编码回退密钥** `xuanji_fortune_secret_key_2026!!` | 未设环境变量即生效，可伪造任意用户 Token |
| **验证码明文回传**（短信演示模式） | 未配置阿里云时，任意访客可获取验证码并伪造登录 |
| **analytics API 零鉴权** | 全部运营数据裸奔 |
| **OAuth state 存进程内存** | gunicorn 多 worker 下 CSRF 校验不可靠，重启即失效 |
| **vendor SDK 源码**（api/sdk/ 含旧版 urllib3） | 安全隐患，pip 升级无法覆盖 |
| **257 个模块页各含 184-520 行内嵌 CSS** | 前端体积膨胀，缓存失效 |
| **24 个部署脚本散落根目录** | 管理混乱 |

### 1.2 重构目标

1. **结构**：应用工厂 + Blueprint 分层，服务层与路由层分离；
2. **安全**：移除硬编码密钥、验证码不回传、analytics 加鉴权；
3. **性能**：前端公共样式提取，后端算法拆分独立缓存；
4. **兼容**：API 契约 100% 保留，前端 239 个页面零改动；
5. **可测**：引入 pytest 冒烟测试（24 项全部通过）。

---

## 二、新架构设计

### 2.1 目录结构

```
app/
├── __init__.py          # create_app() 工厂 + 请求追踪钩子
├── extensions.py        # limiter（避免循环导入）
├── repositories/        # 数据访问层（Repository 模式）
│   ├── json_store.py    # 带 fcntl 锁的通用 JSON 存储
│   ├── user_repo.py     # 用户/Token/验证码
│   └── oauth_state.py   # OAuth state 文件持久化
├── services/            # 业务逻辑层（零 Flask 依赖）
│   ├── fortune/         # 10 个独立算法模块
│   │   ├── cache.py
│   │   ├── clients.py   # 星座/塔罗 API 客户端
│   │   ├── bazi.py      # 八字排盘（667 行核心算法）
│   │   ├── shengxiao.py
│   │   ├── xingming.py
│   │   ├── heyun.py
│   │   ├── huangli.py
│   │   ├── jiemeng.py
│   │   ├── universal.py # 模块路由分发 + 降级生成
│   │   └── image.py     # 图片分析（面相/手相）
│   ├── security.py      # PBKDF2 + JWT
│   ├── vip.py           # 会员服务（原 api/vip_service.py）
│   ├── oauth_providers.py
│   ├── sms.py           # 阿里云短信（标准 pip 依赖）
│   ├── mailer.py
│   └── analytics_db.py  # SQLite WAL 分析库
└── api/                 # 路由层（9 个 Blueprint）
    ├── auth.py          # 11 路由
    ├── profile.py       # 13 路由
    ├── oauth.py         # 5 路由
    ├── vip.py           # 6 路由
    ├── content.py       # 19 路由
    ├── datasets.py      # 12 路由
    ├── system.py        # 10 路由
    ├── fortune.py       # 17 路由（原 fortune_routes.py）
    └── admin.py         # 10 路由（加鉴权）
```

### 2.2 核心设计决策

| 决策 | 理由 |
|------|------|
| **保留 JSON 文件存储，Repository 封装** | 数据路径与旧版完全兼容，零迁移成本；未来换 SQLite 只需替换 repository 实现 |
| **应用工厂模式** | 测试可注入 TestConfig（临时目录隔离），生产可 fail-fast 校验 |
| **验证码存储改为 CaptchaRepo（文件 + 锁）** | 多 worker 安全，且 TTL 清理内聚 |
| **OAuth state 改为 OAuthStateRepo** | 解决多 worker / 重启失效问题 |
| **JWT secret 移除硬编码回退** | `ProductionConfig.validate()` 启动时校验，缺失即拒绝 |
| **analytics 加 `X-Admin-Token` 鉴权** | 不配置 ADMIN_TOKEN 时接口整体禁用（503），避免裸奔上线 |

---

## 三、安全修复清单

| 漏洞 | 旧版表现 | 新版修复 |
|------|---------|---------|
| JWT 硬编码密钥 | `SECRET_KEY = os.environ.get('JWT_SECRET', 'xuanji_fortune_secret_key_2026!!')` | 生产环境无 SECRET_KEY 直接 `RuntimeError` 拒绝启动 |
| 短信验证码明文回传 | 演示模式 `code: sms_code` 返回给前端 | 默认 `code: None`；仅 `SMS_DEMO_MODE=1` 时回传 |
| analytics API 无鉴权 | 任何人均可 GET /api/admin/analytics/overview | 需 `X-Admin-Token` 头匹配环境变量 |
| OAuth state 内存存储 | gunicorn 4 worker 各有一份字典，重启清空 | 文件持久化 + TTL，pop 消费（一次性） |
| vendor SDK 旧版 urllib3 | api/sdk/ 内嵌 aliyunsdkcore 2.16.0 | 删除 vendor，改用 pip 标准包 |

---

## 四、前端优化

### 4.1 模块页瘦身

- **分析**：257 个模块页共 17524 行内嵌 CSS，其中 **204 页共享完全相同的 60 行样式块**；
- **提取**：4 个公共 CSS 文件（module-common-1~4.css）；
- **效果**：240 页已瘦身，源码减少 **268 KB**；浏览器缓存后实际传输量节省更大。

### 4.2 module_list.json 同步

- 旧版：根目录 + modules/ 下各有一份，且与 257 个实际文件脱节（缺 53 条）；
- 新版：`scripts/sync_module_list.py` 以根目录为唯一真源，自动补登缺失条目。

---

## 五、数据迁移路径

### 5.1 零迁移方案（推荐）

新版数据文件路径与旧版完全一致（`data/users.json`、`data/tokens.json` 等），
直接替换代码即可上线，无需任何数据迁移。

### 5.2 JSON → SQLite（未来演进）

```bash
python scripts/migrate_json_to_sqlite.py --dry-run   # 体检
python scripts/migrate_json_to_sqlite.py             # 导入 SQLite
```

导入后实现 `app/repositories/user_repo_sqlite.py` 并在工厂中替换，
业务代码（services / api）零改动。

---

## 六、测试与验证

### 6.1 冒烟测试（24 项全部通过）

覆盖：健康检查、注册/登录/鉴权、验证码、八字/姓名/生肖/黄历/塔罗、
收藏/联系人/历史、VIP 状态/签到、管理端鉴权、OAuth 状态。

```bash
python3 -m pytest tests/test_smoke.py -v
# 24 passed, 11 warnings in 5.98s
```

### 6.2 浏览器验证

- 塔罗页：深色星空背景、金色标题、布局正常；
- 八字页：表单完整、样式一致；
- 公共 CSS 缓存命中 200。

---

## 七、部署切换

```bash
# 在阿里云 ECS 项目根目录
bash scripts/deploy_switch.sh
```

脚本流程：
1. 校验 SECRET_KEY（fail-fast）
2. 备份旧 wsgi.py
3. pip 安装依赖（清华镜像）
4. 数据目录自检
5. 应用自检 + 冒烟测试
6. gunicorn HUP 平滑重启

回滚：`mv wsgi.py.legacy.bak wsgi.py && systemctl restart suanming`

---

## 八、遗留与后续

| 事项 | 说明 |
|------|------|
| **flask-limiter 内存存储** | 单 worker 足够；多 worker 建议切 Redis（RATELIMIT_STORAGE_URI） |
| **fortune_routes 手写限流** | 保留（带响应头逻辑），与 flask-limiter 并存，未来可统一 |
| **模块页 script 去重** | script 重复度低（241 种不同内容），暂不做激进提取 |
| **SQLAlchemy models.py** | 已删除 app_with_db.py，models.py 保留为 SQLite 迁移参考 |
| **admin/analytics.html** | 仍为纯静态页，未来可接入带鉴权的 /api/admin/analytics |

---

*报告生成时间：2026-09-01*
*重构执行：WorkBuddy AI Agent*
