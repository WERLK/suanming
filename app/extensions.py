"""
Flask 扩展实例集中管理。

扩展在此创建、在 create_app() 中 init_app()，
避免「扩展反向导入 app」造成的循环依赖。
"""
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=['100 per minute'],
        storage_uri='memory://',
    )
except ImportError:
    # flask-limiter 未安装时降级为 no-op：限流功能停用，但不阻断应用启动。
    # 生产环境 pip 装上 flask-limiter 后重启即自动恢复限流。
    class _NoopLimiter:
        storage_uri = 'memory://'
        default_limits = []

        def limit(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator

        def init_app(self, app):
            pass

    limiter = _NoopLimiter()
