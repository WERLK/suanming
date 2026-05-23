# Gunicorn 配置文件
import multiprocessing

# 绑定 IP 和端口
bind = "0.0.0.0:5000"

# 工作进程数
workers = multiprocessing.cpu_count() * 2 + 1

# 工作模式
worker_class = 'sync'

# 每个工作进程的线程数
threads = 2

# 请求超时时间（秒）
timeout = 60

# 优雅重启超时时间
graceful_timeout = 10

# Keep-alive 时间
keepalive = 5

# 访问日志文件
accesslog = '/workspace/logs/access.log'

# 错误日志文件
errorlog = '/workspace/logs/error.log'

# 日志级别
loglevel = 'info'

# 进程名称
proc_name = 'flask-app'

# 是否后台运行
daemon = False

# 最大请求数（达到后重启工作进程，防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50

# 热更新配置
reload = True  # 启用自动重载
reload_extra_files = [
    '/workspace/api/app.py',
    '/workspace/api/sms_extension.py',
    '/workspace/login.html',
    '/workspace/register.html',
    '/workspace/forgot-password.html',
    '/workspace/reset-password.html'
]

# 环境变量
raw_env = [
    'FLASK_ENV=production',
    'PYTHONUNBUFFERED=true'
]
