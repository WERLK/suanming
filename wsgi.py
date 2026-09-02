"""生产 WSGI 入口（gunicorn / PythonAnywhere）。

用法：
    gunicorn -c gunicorn_config.py wsgi:application
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# 安全加固：不再提供硬编码回退密钥。
# SECRET_KEY 必须由环境变量提供，缺失时由 config.ProductionConfig.validate()
# 触发 fail-fast，拒绝以默认密钥启动，杜绝密钥被公开导致的伪造 token 风险。

from app import create_app

application = create_app()
app = application
