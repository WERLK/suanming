# 兼容垫片包（legacy entry shim）
# 旧自动更新守护进程以 api.app:app 入口启动 gunicorn，本包将其桥接到新架构。
# 详见 api/app.py 说明；待新版守护进程（auto_update_daemon.py v2）接管后可移除。
