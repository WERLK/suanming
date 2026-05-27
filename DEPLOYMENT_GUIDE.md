# 玄机算命网 - 个人中心完整功能部署指南

## 📋 功能完成清单

### ✅ 已完成的个人中心功能

#### 1. **头像上传（带自动审核）**
- ✅ 前端：`profile.html` 和 `edit-profile.html` 头像上传功能
- ✅ 后端 API：`POST /api/avatar/upload`
- ✅ 自动审核模块：`api/avatar_audit.py`（基于全网头像审核规则）
- ✅ 审核规则：文件大小、格式、尺寸、内容（皮肤色调、血腥色调、纯色块）

#### 2. **编辑资料**
- ✅ 前端：`edit-profile.html`（专门页面）
- ✅ 后端 API：`PUT /api/profile`
- ✅ 可编辑字段：用户名、手机号、邮箱、生日、性别

#### 3. **会员 VIP 系统**
- ✅ 前端：`profile.html` 会员卡片展示
- ✅ 后端 API：`/api/vip/status`、`/api/vip/watch-ad`
- ✅ 功能：看广告赚时长（每次 2 小时）

#### 4. **算命历史**
- ✅ 前端：`history.html`
- ✅ 后端 API：`/api/divination-history`

#### 5. **我的收藏**
- ✅ 前端：`favorites.html`
- ✅ 后端 API：`/api/favorites` (GET/POST/DELETE)
- ✅ 数据存储：`data/favorites.json`

#### 6. **分享记录**
- ✅ 前端：`shares.html`
- ✅ 后端 API：`/api/shares` (GET/POST)
- ✅ 数据存储：`data/shares.json`

#### 7. **我的报告**
- ✅ 前端：`reports.html`（含查看详情、删除功能）
- ✅ 后端 API：`/api/reports` (GET/POST/DELETE)
- ✅ 数据存储：`data/reports.json`

#### 8. **通知设置**
- ✅ 前端：`notifications.html`（开关式设置）
- ✅ 后端 API：`/api/notifications/settings` (GET/PUT)
- ✅ 设置项：推送通知、邮件通知、短信通知、每日运势、VIP 到期、系统通知
- ✅ 数据存储：`data/notifications.json`

#### 9. **隐私设置**
- ✅ 前端：`privacy.html`（开关式设置）
- ✅ 后端 API：`/api/privacy/settings` (GET/PUT)
- ✅ 设置项：个人资料公开、算命记录公开、允许被搜索、显示在线状态
- ✅ 数据存储：`data/privacy.json`

#### 10. **帮助中心**
- ✅ 前端：`help.html`（折叠式常见问题）
- ✅ 后端 API：`/api/help/<topic>`
- ✅ 预设问题：注册、登录、算命准确性、VIP、头像、联系客服

#### 11. **关于我们**
- ✅ 前端：`about.html`
- ✅ 后端 API：`/api/about`
- ✅ 内容：网站简介、联系方式、ICP 信息、法律信息

---

## 📂 新增/修改的文件清单

### **新增文件（11 个）**

| 文件路径 | 说明 |
|---------|------|
| `api/avatar_audit.py` | 头像自动审核模块 |
| `version.json` | 版本信息配置文件 |
| `update_version.sh` | 版本更新脚本 |
| `test_features.sh` | 功能测试脚本 |
| `VERSION_AND_AVATAR_FEATURES.md` | 功能说明文档 |
| `favorites.html` | 我的收藏页面 |
| `shares.html` | 分享记录页面 |
| `reports.html` | 我的报告页面 |
| `notifications.html` | 通知设置页面 |
| `privacy.html` | 隐私设置页面 |
| `help.html` | 帮助中心页面 |
| `about.html` | 关于我们页面 |
| `edit-profile.html` | 编辑资料页面 |

### **修改文件（4 个）**

| 文件路径 | 修改内容 |
|---------|----------|
| `api/app.py` | 添加健康检查、版本信息、头像上传、收藏、分享、报告、通知设置、隐私设置、帮助中心、关于我们等所有 API 接口 |
| `remote_update.sh` | 修改超时时间为 300 秒 |
| `profile.html` | 完善所有菜单项跳转链接（移除"开发中"提示） |
| `index.html` | 添加页脚版本号显示 |

---

## 🚀 部署步骤

### **步骤 1：提交代码到 GitHub**

```bash
cd /workspace/suanming-fix

# 添加所有文件
git add .

# 提交（使用详细的提交信息）
git commit -m "feat: 完成个人中心所有功能

✨ 新增功能：
- 头像上传（带自动审核，基于全网审核规则）
- 我的收藏（添加/查看/取消收藏）
- 分享记录（记录分享到各平台的历史）
- 我的报告（保存/查看/删除算命报告）
- 通知设置（推送/邮件/短信/每日运势/VIP到期/系统通知）
- 隐私设置（资料公开/算命公开/允许搜索/在线状态）
- 帮助中心（折叠式常见问题）
- 关于我们（网站简介/联系方式/ICP信息）

🔧 功能改进：
- 修改脚本超时到 5 分钟（300 秒）
- 添加 /api/health 健康检查端点
- 添加 /api/version 版本信息接口
- 在 index.html 页脚显示版本号
- 完善 profile.html 所有菜单项（移除开发中提示）

📝 文档更新：
- 添加 VERSION_AND_AVATAR_FEATURES.md 功能说明
- 添加 DEPLOYMENT_GUIDE.md 部署指南
- 添加 test_features.sh 功能测试脚本
- 添加 update_version.sh 版本更新脚本

🔒 安全改进：
- 头像自动审核（防止违规图片上传）
- 用户数据隔离（每个用户只能访问自己的数据）
- API 权限验证（所有接口都需要登录 token）"

# 推送到 GitHub
git push origin main
```

### **步骤 2：在服务器上拉取更新**

```bash
# SSH 登录服务器
ssh root@你的服务器IP

# 进入项目目录
cd /root/suanming

# 拉取最新代码
git pull origin main

# 创建必要的数据文件（如果不存在）
mkdir -p data
touch data/favorites.json
touch data/shares.json
touch data/reports.json
touch data/notifications.json
touch data/privacy.json

# 初始化 JSON 文件内容（如果为空）
echo '{}' > data/favorites.json
echo '{}' > data/shares.json
echo '{}' > data/reports.json
echo '{}' > data/notifications.json
echo '{}' > data/privacy.json

# 设置文件权限
chmod 644 data/*.json

# 创建头像上传目录
mkdir -p static/avatars
chmod 755 static/avatars

# 停止旧进程
pkill -f gunicorn
sleep 5

# 启动新进程（带 300 秒超时）
cd /root/suanming/api
nohup gunicorn -w 4 -t 300 -b 0.0.0.0:5000 app:app > /root/suanming/logs/gunicorn.log 2>&1 &

# 检查服务状态
cd /root/suanming
python3 backend_check.py
```

### **步骤 3：验证功能**

```bash
# 1. 检查健康检查
curl http://localhost:5000/api/health

# 预期返回：
# {
#   "status": "ok",
#   "timestamp": "2026-05-27T22:10:00",
#   "service": "xuanji-fortune",
#   "version": "1.0.0",
#   "build_time": "2026-05-27T21:50:00Z",
#   "database": "connected"
# }

# 2. 检查版本信息
curl http://localhost:5000/api/version

# 预期返回：
# {
#   "success": true,
#   "version": {
#     "version": "1.0.0",
#     "build_time": "2026-05-27T21:50:00Z",
#     "git_commit": "abc1234",
#     "author": "玄机算命网",
#     "description": "动态版本管理配置文件"
#   }
# }

# 3. 测试头像上传（需要登录 token）
# 先登录获取 token
TOKEN="你的登录token"

# 上传头像
curl -X POST http://localhost:5000/api/avatar/upload \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"image": "base64编码的图片数据"}'

# 4. 测试收藏功能
curl -X GET http://localhost:5000/api/favorites \
  -H "Authorization: Bearer $TOKEN"

# 5. 测试通知设置
curl -X GET http://localhost:5000/api/notifications/settings \
  -H "Authorization: Bearer $TOKEN"
```

### **步骤 4：前端验证**

1. **打开浏览器，访问你的网站**
   - 首页：`http://你的域名或IP/`
   - 个人中心：`http://你的域名或IP/profile.html`

2. **测试头像上传**
   - 进入个人中心
   - 点击头像区域
   - 选择图片文件（JPG/PNG，< 2MB）
   - 系统自动审核并上传
   - 头像立即更新

3. **测试编辑资料**
   - 点击"编辑资料"
   - 修改用户名/手机号/邮箱/生日/性别
   - 点击"保存资料"
   - 页面自动跳转回个人中心，信息已更新

4. **测试会员系统**
   - 点击"看广告赚时长"
   - 等待 5 秒广告倒计时
   - 点击"领取奖励"
   - VIP 时长增加 2 小时

5. **测试其他功能**
   - 我的收藏：添加/查看/取消收藏
   - 分享记录：查看分享历史
   - 我的报告：保存/查看/删除报告
   - 通知设置：切换各种通知开关
   - 隐私设置：切换各种隐私开关
   - 帮助中心：点击问题查看答案
   - 关于我们：查看网站信息

---

## 📝 数据存储说明

所有用户数据存储在 `data/` 目录下，采用 **JSON 文件存储**（暂不使用数据库）：

| 文件 | 说明 | 数据结构 |
|------|------|------------|
| `users.json` | 用户账号信息 | `{id, username, password, email, phone, avatar, vip_level, vip_expire, ...}` |
| `tokens.json` | 密码重置 token | `{"token": {user_id, expire_time}}` |
| `favorites.json` | 用户收藏 | `{"user_id": [{module_id, module_name, add_time}]}` |
| `shares.json` | 分享记录 | `{"user_id": [{module_id, module_name, platform, share_time}]}` |
| `reports.json` | 算命报告 | `{"user_id": [{id, module_id, module_name, input_data, result_data, save_time}]}` |
| `notifications.json` | 通知设置 | `{"user_id": {push_enabled, email_enabled, sms_enabled, ...}}` |
| `privacy.json` | 隐私设置 | `{"user_id": {profile_public, fortune_public, allow_search, ...}}` |
| `divination_history.json` | 算命历史 | `{"user_id": [{module_id, module_name, input_data, result_data, create_time}]}` |

**优点：**
- 简单易维护（不需要数据库服务器）
- 适合小型应用（用户量 < 1000）
- 可以直接编辑文件查看数据

**缺点：**
- 性能较低（每次读写都要加载整个文件）
- 不支持并发写入（可能导致数据丢失）
- 不支持复杂查询

**未来改进：**
- 当用户量 > 1000 时，迁移到 SQLite 或 MySQL
- 使用 SQLAlchemy ORM 管理数据库
- 添加数据库迁移脚本

---

## ⚠️ 注意事项

### 1. **强制更新命令**
根据你的要求：**只有在你明确要求时，我才会提供强制更新命令**。

如果你需要强制更新命令（绕过 Git pull，直接重置到最新版本），请告诉我，我会生成类似这样的命令：
```bash
cd /root/suanming
git fetch origin
git reset --hard origin/main
pkill -f gunicorn
cd api && nohup gunicorn -w 4 -t 300 -b 0.0.0.0:5000 app:app > ../logs/gunicorn.log 2>&1 &
```

### 2. **头像审核准确性**
当前的自动审核是基于 **规则** 的（颜色分布、皮肤色调检测），可能无法识别所有违规内容。

**建议：**
- 定期人工抽查上传的头像
- 未来可以接入腾讯云/百度AI的内容审核API（更准确）
- 允许用户举报违规头像

### 3. **版本号管理**
每次提交代码前，建议运行 `update_version.sh` 更新版本号：
```bash
cd /workspace/suanming-fix
chmod +x update_version.sh
./update_version.sh
# 选择：1) 修订号 +1  2) 次版本号 +1  3) 主版本号 +1  4) 自定义
```

### 4. **数据备份**
建议定期备份 `data/` 目录：
```bash
# 每天凌晨 2 点备份
0 2 * * * cd /root/suanming && tar -czf /backup/suanming-data-$(date +\%Y\%m\%d).tar.gz data/
```

### 5. **日志查看**
如果遇到问题，查看 Gunicorn 日志：
```bash
tail -f /root/suanming/logs/gunicorn.log
```

---

## 📞 技术支持

如遇问题，请检查：
1. **服务状态**：`python3 backend_check.py`
2. **健康检查**：`curl http://localhost:5000/api/health`
3. **版本信息**：`curl http://localhost:5000/api/version`
4. **日志文件**：`tail -f /root/suanming/logs/gunicorn.log`
5. **数据文件**：`ls -lh /root/suanming/data/`

---

**最后更新时间：** 2026-05-27  
**作者：** 玄机算命网技术团队  
**版本：** v1.0.0
