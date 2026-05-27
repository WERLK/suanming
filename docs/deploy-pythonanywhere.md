# PythonAnywhere 部署配置

## 项目信息
- **应用名称:** suanming-fix
- **Python 版本:** 3.11
- **启动文件:** api/app.py
- **依赖文件:** requirements.txt

## 部署步骤

### 1. 注册账号
- 访问 https://www.pythonanywhere.com/
- 使用邮箱注册（免费计划）

### 2. 上传代码
- 方式一：通过 Git（推荐）
  ```bash
  # 在 PythonAnywhere 控制台中
  git clone https://github.com/WERLK/suanming.git
  ```
- 方式二：手动上传 ZIP 文件

### 3. 配置 Web 应用
- 进入 "Web" 标签
- 点击 "Add a new web app"
- 选择：
  - Python version: 3.11
  - Framework: Flask
  - Configuration file: `/api/app.py`

### 4. 安装依赖
- 打开 "Consoles" → "Bash console"
- 执行：
  ```bash
  cd ~/suanming-fix
  pip3.11 install --user -r requirements.txt
  ```

### 5. 启动应用
- 进入 "Web" 标签
- 点击 "Reload" 按钮

## 注意事项
- **免费计划限制:**
  - 应用 1 小时无访问后会休眠
  - 下次访问需要等待 10-20 秒唤醒
  - 每天最多 1000 次请求
  
- **数据库:** 可以使用 SQLite（文件数据库）
- **静态文件:** 需要通过 WhiteNoise 或类似工具配置

## 访问地址
- 部署成功后，您的应用将可以通过以下地址访问：
  ```
  https://<your-username>.pythonanywhere.com/suanming-fix/
  ```

## 故障排除
- 查看错误日志：`~/suanming-fix/error.log`
- 查看访问日志：`~/suanming-fix/access.log`
- 在 Consoles 中手动测试：`python3.11 api/app.py`
