# Gunicorn 配置文件（云端部署适配版）
import os
import multiprocessing

# 自动检测项目根目录（本文件所在目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 绑定 IP 和端口（云端部署使用环境变量 PORT）
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"

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

# 访问日志（云端部署输出到标准输出）
accesslog = '-'  # 输出到 stdout

# 错误日志（云端部署输出到标准错误）
errorlog = '-'  # 输出到 stderr

# 日志级别
loglevel = 'info'

# 进程名称
proc_name = 'flask-app'

# 是否后台运行（云端部署必须为 False）
daemon = False

# 最大请求数（达到后重启工作进程，防止内存泄漏）
max_requests = 1000
max_requests_jitter = 50

# 热更新配置（云端部署建议关闭）
reload = False  # 云端部署关闭自动重载

# 环境变量
raw_env = [
    'FLASK_ENV=production',
    'PYTHONUNBUFFERED=true'
]
