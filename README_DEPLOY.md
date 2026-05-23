# 部署文档 - Flask 登录注册系统

## 📦 环境要求

- Python 3.8+
- pip3
- Git（可选，用于版本控制）

## 🚀 快速部署

### 1. 安装依赖

```bash
cd /workspace
pip3 install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
nano .env  # 编辑配置文件
```

**重要配置项：**
- `SECRET_KEY`: 改为随机字符串
- `JWT_SECRET_KEY`: 改为随机字符串
- 短信服务配置（阿里云或腾讯云，二选一）

### 3. 启动服务

```bash
# 方式 1: 使用部署脚本（推荐）
./deploy.sh start

# 方式 2: 直接使用 Gunicorn
gunicorn -c gunicorn_config.py api.app:app
```

### 4. 访问服务

浏览器访问: `http://你的服务器IP:5000`

## 🔄 热更新（不中断服务）

### 方法 1: 使用部署脚本

```bash
./deploy.sh reload
```

这会自动：
1. 向 Gunicorn 主进程发送 `SIGHUP` 信号
2. Gunicorn 启动新的工作进程
3. 等待旧的工作进程处理完当前请求后优雅关闭
4. **整个过程服务不中断**

### 方法 2: 自动热更新（开发环境推荐）

运行自动监听脚本，文件变化会自动触发热更新：

```bash
python3 auto_reload.py
```

特点：
- 监听 `.py`, `.html`, `.css`, `.js` 文件变化
- 自动发送 `SIGHUP` 信号触发热更新
- 2秒冷却时间，防止频繁重载
- 实时显示文件变化和热更新状态

### 方法 3: 手动发送信号

```bash
# 查看进程 PID
cat /workspace/logs/gunicorn.pid

# 发送 HUP 信号
kill -HUP $(cat /workspace/logs/gunicorn.pid)
```

## 📝 部署脚本使用说明

```bash
./deploy.sh start    # 启动服务
./deploy.sh stop     # 停止服务
./deploy.sh restart  # 重启服务（会短暂中断）
./deploy.sh reload   # 热更新（不中断服务）
./deploy.sh status   # 查看服务状态
./deploy.sh logs     # 查看日志
```

## 📊 服务管理

### 查看服务状态

```bash
./deploy.sh status
```

输出示例：
```
[INFO] 服务状态: 运行中 (PID: 12345)
[INFO] 进程信息:
UID   PID   PPID  C STIME TTY      TIME     CMD
root  12345 1     0 10:00 ?        00:00:00 gunicorn: master [api.app:app]
root  12346 12345 0 10:00 ?        00:00:00 gunicorn: worker [api.app:app]

[INFO] 端口监听:
tcp   0      0 0.0.0.0:5000    0.0.0.0:*    LISTEN    12345/python3
```

### 查看日志

```bash
# 实时查看日志
tail -f /workspace/logs/error.log
tail -f /workspace/logs/access.log

# 或使用部署脚本
./deploy.sh logs
```

## 🔧 生产环境配置建议

### 1. 使用 Nginx 反向代理

```nginx
# /etc/nginx/sites-available/flask-app
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass <INTERNAL_HOST_REDACTED>
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /workspace/static;
    }
}
```

### 2. 使用 Systemd 管理服务

创建服务文件 `/etc/systemd/system/flask-app.service`:

```ini
[Unit]
Description=Flask Login Register App
After=network.target

[Service]
Type=forking
User=root
WorkingDirectory=/workspace
ExecStart=/workspace/deploy.sh start
ExecStop=/workspace/deploy.sh stop
ExecReload=/workspace/deploy.sh reload
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl enable flask-app
sudo systemctl start flask-app
sudo systemctl status flask-app
```

### 3. 配置 HTTPS（使用 Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 4. 使用 Redis 存储会话

修改 `api/app.py`:

```python
from flask_session import Session
import redis

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('<DB_CONNECTION_REDACTED>
Session(app)
```

## 🐛 常见问题

### 1. 端口被占用

```bash
# 查看端口占用
sudo netstat -tlnp | grep :5000

# 杀死占用进程
kill -9 <PID>
```

### 2. 权限问题

```bash
# 确保日志目录可写
sudo chown -R $USER:$USER /workspace/logs
chmod 755 /workspace/logs
```

### 3. 依赖安装失败

```bash
# 使用国内镜像源
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 热更新不生效

检查：
- Gunicorn 是否正在运行: `./deploy.sh status`
- PID 文件是否存在: `cat /workspace/logs/gunicorn.pid`
- 文件修改是否保存

## 📞 技术支持

如遇问题，请查看日志文件：
- 错误日志: `/workspace/logs/error.log`
- 访问日志: `/workspace/logs/access.log`

## 🎯 性能优化

### Gunicorn 配置调优

编辑 `gunicorn_config.py`:

```python
# 根据 CPU 核心数调整工作进程
workers = multiprocessing.cpu_count() * 2 + 1

# 增加工作线程（适用于 I/O 密集型应用）
threads = 4

# 调整请求超时时间
timeout = 120

# 启用异步工作模式（需要安装 eventlet 或 gevent）
# worker_class = 'gevent'
# workers = 2
```

### 启用 Gzip 压缩

在 Nginx 配置中添加：

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
```

## 🔐 安全建议

1. **修改默认密钥**: 修改 `.env` 中的 `SECRET_KEY` 和 `JWT_SECRET_KEY`
2. **启用 HTTPS**: 使用 Let's Encrypt 免费证书
3. **配置防火墙**: 只开放 80/443 端口，5000 端口只对内部开放
4. **限制访问频率**: 在 `api/app.py` 中添加 rate limiting
5. **定期备份**: 备份数据库和用户数据

## 📚 目录结构

```
/workspace/
├── api/                    # 后端 API
│   ├── app.py             # 主应用
│   └── sms_extension.py   # 短信验证码扩展
├── logs/                  # 日志目录
├── static/                # 静态文件（如果有）
├── gunicorn_config.py     # Gunicorn 配置
├── deploy.sh              # 部署脚本
├── auto_reload.py         # 自动热更新脚本
├── requirements.txt       # Python 依赖
├── .env                   # 环境变量配置
└── README_DEPLOY.md      # 本文档
```
