"""
Flask 扩展实例集中管理。

扩展在此创建、在 create_app() 中 init_app()，
避免「扩展反向导入 app」造成的循环依赖。
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=['100 per minute'],
    storage_uri='memory://',
)
