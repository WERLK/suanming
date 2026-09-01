"""生产 WSGI 入口（gunicorn / PythonAnywhere）。

用法：
    gunicorn -c gunicorn_config.py wsgi:application
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# 密钥回退链与线上旧版保持一致（SECRET_KEY → JWT_SECRET → 旧默认值）：
# 保证未显式配置密钥的存量部署平滑升级，已有用户 token 不失效。
# 生产环境建议在 .env 或环境变量中显式配置强密钥。
if not (os.environ.get('SECRET_KEY') or os.environ.get('JWT_SECRET')):
    os.environ['SECRET_KEY'] = 'xuanji_fortune_secret_key_2026!!'

from app import create_app

application = create_app()
app = application
