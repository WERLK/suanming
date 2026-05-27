# 🚀 Render.com 部署详细指南（带截图说明）

## 📞 概述

本指南将带您在 **10 分钟内** 完成以下任务：
1. 注册 Render.com 账号
2. 连接 GitHub 仓库
3. 部署 Flask 后端
4. 测试 API 是否正常工作

---

## 🚀 步骤一：注册 Render.com 账号（2 分钟）

### 1.1 访问 Render.com

**打开浏览器，访问：**
```
https://render.com/
```

**应该看到：**
```
[截图说明]
- 页面顶部有 "Render" Logo
- 中间有大标题 "The Cloud Platform for Developers"
- 右上角有 "Get Started for Free" 按钮
```

---

### 1.2 点击 "Get Started for Free"

**操作：**
- 点击右上角的 **"Get Started for Free"** 按钮

**应该看到：**
```
[截图说明]
- 跳转到注册页面
- 有 "Sign up with Email" 和 "Sign up with GitHub" 两个选项
```

---

### 1.3 使用 GitHub 账号注册（推荐）

**操作：**
- 点击 **"Sign up with GitHub"** 按钮

**原因：**
- ✅ 一键授权，无需记住新密码
- ✅ 自动连接 GitHub 仓库（省去手动配置）
- ✅ 推送代码后自动部署

**应该看到：**
```
[截图说明]
- 跳转到 GitHub 授权页面
- 标题 "Authorize Render"
- 有 "Authorize" 按钮
```

---

### 1.4 授权 GitHub 访问

**操作：**
- 点击 **"Authorize"** 按钮

**应该看到：**
```
[截图说明]
- 跳回 Render.com 页面
- 显示 "Welcome to Render" 欢迎页面
- 有 "Create a New Web Service" 按钮
```

✅ **完成！** 您已成功注册 Render.com 账号并连接 GitHub！

---

## 🔧 步骤二：创建 Web Service（3 分钟）

### 2.1 点击 "Create a New Web Service"

**操作：**
- 在欢迎页面，点击 **"Create a New Web Service"** 按钮

**或者：**
- 登录后，点击右上角的 **"New +"** 按钮
- 在下拉菜单中选择 **"Web Service"**

**应该看到：**
```
[截图说明]
- 跳转到 "Create a Web Service" 页面
- 有 "Connect a repository" 区域
- 显示您的 GitHub 仓库列表
```

---

### 2.2 连接 GitHub 仓库

**操作：**
- 在仓库列表中，找到 `WERLK/suanming` 仓库
- 点击仓库名称

**如果没看到仓库：**
- 点击 **"Configure Account"** 按钮
- 授权 Render 访问您的 GitHub 仓库
- 回到此页面刷新

**应该看到：**
```
[截图说明]
- 仓库名称旁有绿色勾 ✅
- 下方显示 "Connected" 状态
- 跳转到 "Configure Web Service" 页面
```

---

### 2.3 配置 Web Service

**操作：** 填写以下字段

#### **基本信息**
```
Name: suanming-fix  # 随便取一个名字（会显示在网址中）
```

**注意：** Name 只能包含小写字母、数字和连字符 `-`

---

#### **环境配置**
```
Region: Oregon (US)  # 或选择 Singapore (Asia) 如果面向中国用户
Branch: main  # 选择 main 分支
Root Directory: ./  # 留空或填 ./
```

---

#### **构建和启动命令**
```
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn -c gunicorn_config.py api.app:app
```

**复制粘贴：**
```bash
# Build Command（构建命令）
pip install -r requirements.txt

# Start Command（启动命令）
gunicorn -c gunicorn_config.py api.app:app
```

---

#### **环境变量（可选）**

点击 **"Advanced"** 展开高级设置，添加以下环境变量：

```
Key: FLASK_ENV
Value: production

Key: PYTHONUNBUFFERED
Value: true
```

**如果需要邮件服务（可选）：**
```
Key: SMTP_SERVER
Value: smtp.qq.com

Key: SMTP_PORT
Value: 587

Key: SMTP_EMAIL
Value: your_email@qq.com  # 改成您的邮箱

Key: SMTP_PASSWORD
Value: your_smtp_password  # 改成您的 SMTP 密码
```

---

#### **免费计划设置**

**重要：** 确保选择 **"Free"** 计划

```
Instance Type: Free
```

**免费计划限制：**
- ⚠️ 15 分钟无请求后会休眠
- ⚠️ 下次请求需要等待 10-30 秒唤醒
- ✅ 每月 750 小时免费额度（足够一直运行）
- ✅ 自动 HTTPS（免费 SSL 证书）

---

### 2.4 创建 Web Service

**操作：**
- 滚动到页面底部
- 点击 **"Create Web Service"** 按钮

**应该看到：**
```
[截图说明]
- 跳转到 Web Service 详情页面
- 显示 "Deploying..." 状态和进度条
- 下方有实时日志输出
```

✅ **完成！** 您的 Web Service 已开始部署！

---

## ⏳ 步骤三：等待部署完成（2-5 分钟）

### 3.1 查看部署日志

**应该看到：**
```
[截图说明]
- 日志中显示 "==> Building..."
- 然后显示 "==> Starting..."
- 最后显示 "==> Your service is live 🎉"
```

**常见日志输出：**
```
==> Building...
running pip install -r requirements.txt
...
==> Starting...
running gunicorn -c gunicorn_config.py api.app:app
...
==> Your service is live 🎉
```

---

### 3.2 等待部署完成

**时间：** 通常需要 **2-5 分钟**

**进度：**
```
[截图说明]
- 顶部状态从 "Build in progress" → "Live"
- 有绿色勾 ✅ 表示部署成功
- 显示 "Your service is live at https://suanming-fix.onrender.com"
```

---

### 3.3 获取您的网站网址

**操作：** 复制 Render 给您的网址

**格式：**
```
https://<your-service-name>.onrender.com
```

**示例：**
```
https://suanming-fix.onrender.com
```

✅ **完成！** 您已成功部署 Flask 后端！

---

## 🔍 步骤四：测试部署是否成功（2 分钟）

### 4.1 访问首页

**操作：** 在浏览器中打开您的网址

**示例：**
```
https://suanming-fix.onrender.com
```

**应该看到：**
```
[截图说明]
- 您的算命网站首页
- 221 个算命模块链接
- 页面加载正常，无错误
```

---

### 4.2 测试健康检查 API

**操作：** 在浏览器中打开以下网址

**格式：**
```
https://<your-service-name>.onrender.com/api/fortune/health
```

**示例：**
```
https://suanming-fix.onrender.com/api/fortune/health
```

**应该看到：**
```json
{
  "success": true,
  "message": "",
  "data": {
    "status": "ok",
    "cache_stats": {
      "size": 0,
      "hits": 0,
      "misses": 0,
      "hit_rate": "0.0%",
      "sets": 0,
      "deletes": 0
    },
    "timestamp": 1716812345.678
  },
  "meta": {
    "source": "realtime",
    "module_type": "health"
  }
}
```

✅ **如果看到这个 JSON，说明 API 工作正常！**

---

### 4.3 测试八字排盘 API

**操作：** 使用 curl 或 Postman 测试

**命令：**
```bash
curl -X POST https://suanming-fix.onrender.com/api/fortune/bazi \
  -H "Content-Type: application/json" \
  -d '{"name": "测试", "gender": "male", "birth_date": "1990-06-15", "birth_time": "午时"}'
```

**应该看到：**
```json
{
  "success": true,
  "message": "",
  "data": {
    "name": "测试",
    "gender": "male",
    "birth_date": "1990-06-15",
    "birth_time": 12,
    "pillars": [...],
    "day_master": "庚"
  },
  "meta": {
    "source": "realtime",
    "module_type": "bazi"
  }
}
```

✅ **如果看到这个 JSON，说明八字排盘 API 工作正常！**

---

### 4.4 测试星座运势 API

**操作：** 在浏览器中打开以下网址

**格式：**
```
https://<your-service-name>.onrender.com/api/fortune/xingzuo/daily?sign=aries
```

**示例：**
```
https://suanming-fix.onrender.com/api/fortune/xingzuo/daily?sign=aries
```

**应该看到：**
```json
{
  "success": true,
  "message": "",
  "data": {
    "sign": "aries",
    "date": "2026-05-27",
    "horoscope": "Today is a good day for..."
  },
  "meta": {
    "source": "realtime",
    "module_type": "xingzuo_daily"
  }
}
```

✅ **如果看到这个 JSON，说明星座运势 API 工作正常！**

---

### 4.5 检查日志

**操作：** 在 Render.com 控制台查看日志

**步骤：**
1. 登录 Render.com
2. 点击您的 Web Service（`suanming-fix`）
3. 点击 **"Logs"** 标签

**应该看到：**
```
[截图说明]
- 显示最近的请求日志
- 有 "[INFO] API 成功: /api/fortune/health (source=realtime)" 等日志
- 无错误日志（红色）
```

✅ **如果没有错误日志，说明一切正常！**

---

## 🎉 完成！

**恭喜！您已成功完成以下任务：**
1. ✅ 注册 Render.com 账号
2. ✅ 连接 GitHub 仓库
3. ✅ 部署 Flask 后端
4. ✅ 测试 API 是否正常工作

---

## 🌐 下一步：连接前端和后端

### 5.1 修改前端 JS 中的 API 地址

**当前状态：** 前端 JS 会自动检测并使用 Render.com 地址

**我们已经修改了 `js/fortune-api.js`：**
```javascript
function getAPIBaseURL() {
    // 1. 如果是本地开发环境
    if (location.hostname === 'localhost' || location.hostname === '127.0.0.1') {
        return 'http://localhost:5000';
    }
    
    // 2. 如果前端在 GitHub Pages，后端在 Render.com
    if (location.hostname.endsWith('github.io')) {
        return 'https://suanming-fix.onrender.com';  // ← 改成您的 Render.com 网址
    }
    
    // 3. 同域名部署
    return '';
}
```

**您需要做的：**
- 将 `suanming-fix.onrender.com` 改成您实际的 Render.com 网址

---

### 5.2 推送代码到 GitHub

**操作：**
```bash
cd /workspace/suanming-fix
git add js/fortune-api.js
git commit -m "修改前端API地址指向Render.com"
git push origin main
```

**等待 1-2 分钟，让 GitHub Pages 更新。**

---

### 5.3 测试前端是否正常调用后端

**操作：**
1. 访问您的 GitHub Pages 网站：
   ```
   https://werkln.github.io/suanming/
   ```

2. 点击任意一个算命模块（如 "八字排盘"）

3. 填写信息，点击 "开始分析"

4. 应该看到：
   - Loading 动画（"正在连接大数据平台..."）
   - 然后显示分析结果
   - 数据来源标识（绿色 = 实时，蓝色 = 缓存，橙色 = 本地）

✅ **如果看到分析结果，说明前端已成功调用后端 API！**

---

## 🚨 常见问题

### 问题 1：部署失败，提示 "requirements.txt not found"

**原因：** 项目根目录没有 `requirements.txt` 文件

**解决方案：**
```bash
cd /workspace/suanming-fix
pip3 freeze > requirements.txt
git add requirements.txt
git commit -m "添加requirements.txt"
git push origin main
```

**然后：**
- 在 Render.com 控制台
- 点击 **"Manual Deploy"** → **"Deploy latest commit"**

---

### 问题 2：网站可以访问，但 API 调用失败

**原因：** 前端 JS 中的 API 地址还是 `localhost:5000`

**解决方案：**
1. 修改 `js/fortune-api.js` 中的 `getAPIBaseURL()` 函数
2. 将 `suanming-fix.onrender.com` 改成您实际的 Render.com 网址
3. 推送到 GitHub

---

### 问题 3：Render.com 免费计划休眠问题

**原因：** 15 分钟无请求后，免费计划会休眠

**解决方案：**
1. **接受休眠**：首次请求会慢 10-30 秒，后续正常
2. **使用付费计划**：$7/月，永不休眠
3. **使用 Ping 服务**：使用 UptimeRobot 等免费服务，每 15 分钟 Ping 一次您的网站

**UptimeRobot 配置：**
```
URL: https://suanming-fix.onrender.com/api/fortune/health
Monitoring Interval: 15 minutes
```

---

### 问题 4：CORS 跨域错误

**原因：** 前端（`github.io`）调用后端（`onrender.com`）会跨域

**解决方案：**
- ✅ 我们已经在 `api/app.py` 中添加了 `flask-cors`：
  ```python
  from flask_cors import CORS
  CORS(app)
  ```

- 如果您还是遇到 CORS 错误，请在 Render.com 的环境变量中添加：
  ```
  Key: CORS_ENABLED
  Value: true
  ```

---

## 📞 需要帮助？

如果您在部署过程中遇到问题，请告诉我：
1. 您卡在哪一步？
2. 错误信息是什么？
3. 您看到的现象是什么？

我会帮您解决问题！

---

## 🎊 总结

**您已经完成：**
1. ✅ 注册 Render.com 账号
2. ✅ 连接 GitHub 仓库
3. ✅ 部署 Flask 后端
4. ✅ 测试 API 是否正常工作
5. ✅ 连接前端和后端

**您的网站现在可以通过以下网址访问：**
- **前端（GitHub Pages）**：`https://werkln.github.io/suanming/`
- **后端（Render.com）**：`https://suanming-fix.onrender.com/`

**下一步：**
- 测试所有 221 个算命模块是否正常
- 配置自定义域名（可选）
- 启用 UptimeRobot 防止休眠（可选）

---

*更新时间：2026-05-27 19:35*
*预计完成时间：10 分钟*
*难度：⭐（非常简单）*
