# 玄机算命网 v2 — 重构版架构

> 基于 Flask 应用工厂 + Blueprint 分层架构，保留全部 221 个算命模块与 API 契约。

## 快速开始

```bash
# 1. 安装依赖（国内镜像）
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 配置环境变量（生产必须设置 SECRET_KEY）
cp .env.example .env
# 编辑 .env，至少填写 SECRET_KEY

# 3. 启动开发服务器
python run.py

# 4. 生产部署（gunicorn）
gunicorn -c gunicorn_config.py wsgi:application
```

## 架构概览

```
suanming-v2/
├── run.py              # 开发入口
├── wsgi.py             # 生产入口（gunicorn）
├── config.py           # 分环境配置（Dev / Production / Test）
├── requirements.txt
├── app/
│   ├── __init__.py     # create_app() 应用工厂
│   ├── extensions.py   # Flask-Limiter 等扩展
│   ├── repositories/   # 数据访问层（JSON 文件 + 锁，可换 SQLite）
│   ├── services/       # 业务逻辑层（无 Flask 依赖）
│   │   ├── fortune/    # 八字/生肖/星座/塔罗/黄历/解梦/紫微/智能分析
│   │   ├── security.py # 密码哈希 + JWT
│   │   ├── vip.py      # VIP 会员服务
│   │   ├── oauth_providers.py  # GitHub/微信/QQ 登录
│   │   └── ...
│   ├── api/            # 路由层（Blueprint）
│   │   ├── auth.py     # 验证码/短信/注册/登录/密码重置
│   │   ├── profile.py  # 资料/实名/头像/通知/隐私
│   │   ├── fortune.py  # /api/fortune/* 算命核心 API
│   │   ├── vip.py      # VIP 会员路由
│   │   ├── oauth.py    # 第三方登录
│   │   ├── content.py  # 收藏/分享/报告/历史/联系人/帮助
│   │   ├── datasets.py # 自定义数据集与分类
│   │   ├── system.py   # 健康检查/版本/下载代理
│   │   ├── admin.py    # 分析 API（带令牌鉴权）
│   │   └── deps.py     # 统一鉴权/响应/数据访问
│   └── admin/
│       └── analytics.py
├── modules/            # 221 个算命模块 HTML 页面
├── js/                 # 前端 JS（fortune-api.js / main.js 等）
├── css/                # 样式 + module-common-*.css（公共样式提取）
├── scripts/
│   ├── deploy_switch.sh          # 生产切换脚本
│   ├── slim_modules.py           # 前端模块页瘦身
│   ├── sync_module_list.py       # 模块清单同步
│   └── migrate_json_to_sqlite.py # 数据迁移（可选）
└── tests/
    └── test_smoke.py   # 冒烟测试（24 项全部通过）
```

## 关键改进

| 维度 | 旧版（v1.16.x） | 新版（v2） |
|------|----------------|-----------|
| **入口** | `api/app.py` 3458 行单体 | 应用工厂 + 8 个 Blueprint |
| **算命服务** | `api/fortune_service.py` 2745 行 | 10 个独立模块（bazi/shengxiao/…） |
| **数据访问** | 文件操作散落各处 | `repositories/` 统一封装 + 文件锁 |
| **鉴权** | 7 处重复手写 token 解析 | `@require_auth` 装饰器 + `g.current_user` |
| **安全** | JWT 硬编码回退密钥 | 生产启动 fail-fast 校验 |
| **短信** | 演示模式明文回传验证码 | 默认不回传，需 `SMS_DEMO_MODE=1` |
| **分析 API** | 完全无鉴权 | `X-Admin-Token` 令牌校验 |
| **OAuth state** | 进程内存（重启失效） | 文件持久化（多 worker 安全） |
| **依赖** | vendor SDK 源码（api/sdk/） | 标准 pip 依赖 |
| **前端** | 257 页每页内嵌重复 CSS | 提取 4 个公共 CSS（减少 268KB） |

## API 契约

所有前端接口保持不变。例如：

- `POST /api/fortune/bazi` — 八字排盘
- `GET /api/fortune/xingzuo/daily?sign=aries` — 星座日运
- `POST /api/register` / `POST /api/login` — 注册/登录
- `GET /api/vip/status` — VIP 状态

完整契约见 `tests/test_smoke.py`（24 项端到端测试）。

## 部署

```bash
# 在阿里云 ECS 项目根目录
bash scripts/deploy_switch.sh
```

脚本会自动：安装依赖 → 数据目录自检 → 应用自检 → 冒烟测试 → 平滑重启。

回滚：`mv wsgi.py.legacy.bak wsgi.py && systemctl restart suanming`

## 测试

```bash
# 全部冒烟测试（24 项）
python3 -m pytest tests/test_smoke.py -v

# 算命服务包独立测试
python3 -c "
from app.services.fortune import bazi_calc, xingming_calc
print(bazi_calc.calc_full('张三', 'male', '1990-05-15', '14:30'))
print(xingming_calc.analyze('张三'))
"
```

## 联系方式

- 开发者：WorkBuddy AI Agent
- 项目：玄机算命网（xuanjisuanming.top）
- 声明：仅供学习研究，禁止用于非法用途
