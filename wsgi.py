"""生产 WSGI 入口（gunicorn / PythonAnywhere）。

用法：
    gunicorn -c gunicorn_config.py wsgi:application
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import create_app

application = create_app()
app = application
