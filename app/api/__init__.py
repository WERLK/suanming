"""蓝图统一注册。新增业务域时在此追加一行即可。"""
from app.api.admin import analytics_bp
from app.api.auth import bp as auth_bp
from app.api.content import bp as content_bp
from app.api.datasets import bp as datasets_bp
from app.api.fortune import fortune_bp
from app.api.oauth import bp as oauth_bp
from app.api.profile import bp as profile_bp
from app.api.system import bp as system_bp
from app.api.vip import bp as vip_bp


def register_blueprints(app):
    app.register_blueprint(system_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(vip_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(datasets_bp)
    app.register_blueprint(fortune_bp, url_prefix='/api/fortune')
    app.register_blueprint(analytics_bp, url_prefix='/api/admin/analytics')
