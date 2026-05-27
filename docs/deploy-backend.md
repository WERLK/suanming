# 🚀 后端托管部署指南

## ✅ 已完成的配置

我已经为您的项目创建了云端部署所需的配置文件：

1. ✅ `Procfile` - Render.com/Railway等平台使用的进程定义文件
2. ✅ `runtime.txt` - 指定Python版本（3.11.0）
3. ✅ `gunicorn_config.py` - 适配云端部署的Gunicorn配置
4. ✅ `render.yaml` - Render.com部署配置文件

---

## 🌐 推荐托管平台对比

| 平台 | 免费额度 | 优点 | 缺点 |
|------|---------|------|------|
| **Render.com** | ✅ 永久免费 | 简单易用、自动HTTPS、GitHub集成 | 冷启动慢（15分钟无请求会休眠） |
| **Railway.app** | ⚠️ $5免费额度/月 | 速度快、不休眠 | 免费额度用完后需付费 |
| **PythonAnywhere** | ✅ 有限免费 | 专门为Python设计 | 功能有限 |
| **Vercel** | ✅ 永久免费 | 超快部署、自动HTTPS | 不支持长时间运行的进程 |

**推荐：Render.com**（最适合您的项目）

---

## 🚀 方法一：部署到Render.com（推荐）

### 步骤1：注册Render.com账号
1. 访问：https://render.com/
2. 点击 **"Get Started for Free"**
3. 使用 **GitHub账号** 登录（推荐）

### 步骤2：创建Web Service
1. 登录后，点击 **"New +"** 按钮
2. 选择 **"Web Service"**
3. 连接你的GitHub仓库：`WERLK/suanming`
4. 选择分支：`main`

### 步骤3：配置部署设置
```
Name: suanming-fix  # 随便取一个名字
Environment: Python 3
Region: Oregon (US)  # 或选择 Singapore (Asia) 如果面向中国用户
Branch: main
Root Directory: ./  # 留空或填 ./
```

**Build Command（构建命令）：**
```bash
pip install -r requirements.txt
```

**Start Command（启动命令）：**
```bash
gunicorn -c gunicorn_config.py api.app:app
```

### 步骤4：高级设置（可选）
点击 **"Advanced"** 展开高级设置：

**环境变量（Environment Variables）：**
```
FLASK_ENV = production
PYTHONUNBUFFERED = true

# 可选：配置邮件服务（如果需要发送邮件）
SMTP_SERVER = smtp.qq.com
SMTP_PORT = 587
SMTP_EMAIL = your_email@qq.com
SMTP_PASSWORD = your_smtp_password
```

**免费计划设置：**
- ✅ 勾选 **"Free"** 计划
- ⚠️ 注意：免费计划15分钟无请求后会休眠，下次请求需要等待10-30秒唤醒

### 步骤5：创建Web Service
1. 滚动到页面底部
2. 点击 **"Create Web Service"** 按钮
3. 等待部署完成（通常需要2-5分钟）

### 步骤6：访问你的网站
部署完成后，Render会给你一个网址：
```
https://suanming-fix.onrender.com
```

点击这个链接，访问你的算命网站！

---

## 🚂 方法二：部署到Railway.app

### 步骤1：注册Railway账号
1. 访问：https://railway.app/
2. 点击 **"Start a Project"**
3. 使用 **GitHub账号** 登录

### 步骤2：创建新项目
1. 点击 **"Deploy a new service"**
2. 选择 **"Deploy from GitHub repo"**
3. 选择仓库：`WERLK/suanming`
4. 选择分支：`main`

### 步骤3：配置启动命令
**Settings → Deploy → Start Command：**
```bash
gunicorn -c gunicorn_config.py api.app:app
```

**Settings → Variables → 添加环境变量：**
```
FLASK_ENV = production
PYTHONUNBUFFERED = true
```

### 步骤4：部署
1. 点击 **"Deploy"** 按钮
2. 等待部署完成（1-3分钟）
3. 访问Railway给你的网址

**注意：** Railway提供$5免费额度/月，用完后需付费。

---

## 📁 项目文件结构（云端部署版）

```
suanming-fix/
├── api/
│   ├── app.py                # Flask主应用
│   ├── fortune_service.py    # 算命服务层
│   ├── fortune_routes.py    # API路由
│   └── ...
├── modules/                  # 221个算命模块
│   ├── bazi.html
│   ├── xingzuo.html
│   └── ...
├── css/
│   └── style.css
├── js/
│   └── fortune-api.js
├── index.html                # 首页
├── Procfile                  # ✅ 新增：Render/Railway进程定义
├── runtime.txt              # ✅ 新增：Python版本
├── render.yaml              # ✅ 新增：Render部署配置
├── gunicorn_config.py       # ✅ 已修改：适配云端部署
├── requirements.txt         # Python依赖
└── README.md
```

---

## 🔧 测试部署是否成功

### 1. 访问首页
```
https://suanming-fix.onrender.com  # Render.com
或
https://suanming-fix.up.railway.app  # Railway
```

应该看到你的算命网站首页！

### 2. 测试API端点
访问以下链接，检查API是否工作：

**健康检查：**
```
https://suanming-fix.onrender.com/api/fortune/health
```

**八字排盘API：**
```bash
curl -X POST https://suanming-fix.onrender.com/api/fortune/bazi \
  -H "Content-Type: application/json" \
  -d '{"name": "测试", "gender": "male", "birth_date": "1990-06-15", "birth_time": "午时"}'
```

**星座运势API：**
```
https://suanming-fix.onrender.com/api/fortune/xingzuo/daily?sign=aries
```

### 3. 检查日志
在Render.com或Railway控制台查看日志：
- ✅ 看到 `算命API蓝图已加载（/api/fortune/*）` 说明成功
- ❌ 如果报错，检查日志找出问题

---

## ⚠️ 常见问题

### 问题1：部署失败，提示"requirements.txt not found"
**原因：** 项目根目录没有`requirements.txt`文件

**解决方案：**
创建`requirements.txt`：
```bash
cd /workspace/suanming-fix
pip3 freeze > requirements.txt
git add requirements.txt
git commit -m "添加requirements.txt"
git push origin main
```

### 问题2：网站可以访问，但API调用失败
**原因：** 前端代码中的API地址还是`localhost:5000`

**解决方案：**
修改`js/fortune-api.js`，使用相对路径：
```javascript
// 修改前
const API_BASE = 'http://localhost:5000/api/fortune';

// 修改后
const API_BASE = '/api/fortune';  // 使用相对路径
```

### 问题3：Render.com免费计划休眠问题
**原因：** 15分钟无请求后，免费计划会休眠

**解决方案：**
1. **接受休眠**：首次请求会慢10-30秒，后续正常
2. **使用付费计划**：$7/月，永不休眠
3. **使用Ping服务**：使用UptimeRobot等免费服务，每15分钟Ping一次你的网站

---

## 📞 需要帮助？

如果您在部署过程中遇到问题，请告诉我：
1. 您选择哪个平台？（Render.com / Railway / 其他）
2. 卡在哪一步？
3. 错误信息是什么？

我会帮您解决问题！

---

## 🎉 部署成功后

### 你的网站将可以通过以下网址访问：
- **Render.com**: `https://suanming-fix.onrender.com`
- **Railway**: `https://suanming-fix.up.railway.app`

### 下一步：
1. ✅ 测试所有221个算命模块是否正常
2. ✅ 测试API端点是否返回正确数据
3. ✅ 配置自定义域名（可选）
4. ✅ 启用HTTPS（Render.com自动提供）

---

*更新时间：2026-05-27 19:25*
*推荐平台：Render.com（免费、简单、稳定）*
