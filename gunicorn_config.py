# Gunicorn 配置文件
import os
import multiprocessing

# 自动检测项目根目录（本文件所在目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
accesslog = os.path.join(BASE_DIR, 'logs', 'access.log')

# 错误日志文件
errorlog = os.path.join(BASE_DIR, 'logs', 'error.log')

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
    os.path.join(BASE_DIR, 'api', 'app.py'),
    os.path.join(BASE_DIR, 'api', 'sms_extension.py'),
    os.path.join(BASE_DIR, 'index.html'),
    os.path.join(BASE_DIR, 'login.html'),
    os.path.join(BASE_DIR, 'register.html'),
    os.path.join(BASE_DIR, 'profile.html'),
    os.path.join(BASE_DIR, 'more.html'),
    os.path.join(BASE_DIR, 'forgot-password.html'),
    os.path.join(BASE_DIR, 'reset-password.html'),
    os.path.join(BASE_DIR, 'css', 'style.css'),
    os.path.join(BASE_DIR, 'js', 'main.js'),
    os.path.join(BASE_DIR, 'modules', 'bazi.html'),
    os.path.join(BASE_DIR, 'modules', 'xingzuo.html'),
    os.path.join(BASE_DIR, 'modules', 'tarot.html'),
    os.path.join(BASE_DIR, 'modules', 'shengxiao.html'),
    os.path.join(BASE_DIR, 'modules', 'fengshui.html'),
    os.path.join(BASE_DIR, 'modules', 'ziwei.html'),
]

# 环境变量
raw_env = [
    'FLASK_ENV=production',
    'PYTHONUNBUFFERED=true'
]
