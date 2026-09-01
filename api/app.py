"""
兼容垫片（legacy entry shim）—— 旧入口 api.app:app → 新架构桥接。

背景：
    v2.0 重构删除了旧单体 api/ 目录，标准入口改为 wsgi:application。
    但线上仍在运行的旧版 auto_update_daemon.py 以 `api.app:app` 启动
    gunicorn，且其更新流程包含「确保 api/__init__.py 存在」的补丁逻辑。
    本垫片让旧 daemon 无需任何手动干预即可自动完成架构切换：
    拉取 → 检查 api/__init__.py（存在，跳过创建）→ 以 api.app:app 重启
    → 本模块导入新架构 → 新代码上线。

密钥回退链与旧版（api/app.py 第 35 行）完全一致：
    SECRET_KEY → JWT_SECRET → 'xuanji_fortune_secret_key_2026!!'
    保证线上已有用户 token 不失效。

移除时机：
    新版守护进程（auto_update_daemon.py v2，入口自动检测）接管后，
    本文件可在后续版本删除。
"""
import os
import sys

# 密钥回退：与旧版行为一致（环境变量优先，兜底旧默认值，保持登录态）
if not (os.environ.get('SECRET_KEY') or os.environ.get('JWT_SECRET')):
    os.environ['SECRET_KEY'] = 'xuanji_fortune_secret_key_2026!!'

# 项目根目录加入 sys.path（旧 api/ 是包内相对导入风格，垫片在子目录）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402

# 兼容旧入口的三种写法：api.app:app / api.app:application / from api.app import app
app = create_app()
application = app
