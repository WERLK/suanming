"""
兼容垫片（legacy entry shim）—— 旧入口 api.app:app → 新架构桥接。

背景：
    v2.0 重构删除了旧单体 api/ 目录，标准入口改为 wsgi:application。
    本垫片让仍以 `api.app:app` 启动的旧 daemon 自动桥接到新架构。

安全加固：
    不再提供硬编码回退密钥。SECRET_KEY 必须来自环境变量，
    缺失时由 config.ProductionConfig.validate() fail-fast 拒绝启动，
    杜绝密钥公开导致的伪造 token 风险。

移除时机：
    新版守护进程（auto_update_daemon.py v2，入口自动检测）接管后，
    本文件可在后续版本删除。
"""
import os
import sys

# 项目根目录加入 sys.path（旧 api/ 是包内相对导入风格，垫片在子目录）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402

# 兼容旧入口的三种写法：api.app:app / api.app:application / from api.app import app
app = create_app()
application = app
