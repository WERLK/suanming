"""
应用工厂（Application Factory）。

替代旧版 api/app.py 的「模块级全局 app」模式：

    旧: from api.app import app          # 导入即创建，全局唯一
    新: from app import create_app       # 按需创建，配置可注入，测试友好

路由全部拆分为 Blueprint（见 app/api/），
业务逻辑沉入 services/，数据访问收敛到 repositories/。
"""
import os

from flask import Flask, jsonify, request
from flask_cors import CORS

from app.extensions import limiter
from app.repositories import CaptchaRepo, OAuthStateRepo, TokenRepo, UserRepo


def _register_repositories(app):
    """把仓储实例挂到 app.extensions，供 deps 层按请求访问。"""
    cfg = app.config
    app.extensions['user_repo'] = UserRepo(cfg['USERS_FILE'])
    app.extensions['token_repo'] = TokenRepo(cfg['TOKENS_FILE'])
    app.extensions['captcha_repo'] = CaptchaRepo(cfg['CAPTCHA_FILE'])
    app.extensions['oauth_state_repo'] = OAuthStateRepo(cfg['OAUTH_STATE_FILE'])


def _register_analytics_hooks(app):
    """页面/算命/VIP 行为追踪（原 app.py 的 before/after_request 钩子）。"""
    from app.services.analytics_db import (
        init_db, track_divination, track_session, track_vip,
    )
    from app.services.security import verify_token

    init_db()

    @app.before_request
    def before_request_track():
        path = request.path
        skip_prefixes = ('/static/', '/video/', '/css/', '/js/',
                         '/icon-', '/manifest', '/favicon')
        if any(path.startswith(p) for p in skip_prefixes):
            return
        if request.method == 'GET' and not path.startswith('/api/'):
            try:
                event_type = 'module_view' if path.startswith('/modules/') else 'page_view'
                track_session(
                    event_type=event_type,
                    page=path,
                    referrer=request.referrer or '',
                    client_ip=request.remote_addr or '',
                )
            except Exception:
                pass

    @app.after_request
    def after_request_track(response):
        path = request.path

        if path.startswith('/api/fortune/'):
            try:
                parts = path.split('/')
                module_id = parts[3] if len(parts) > 3 else ''
                module_names = {
                    'bazi': '八字排盘', 'ziwei': '紫微斗数', 'tarot': '塔罗牌',
                    'shengxiao': '生肖运势', 'xingming': '姓名测试',
                    'xingzuo': '星座运势', 'heyun': '合婚配对',
                    'jiemeng': '周公解梦', 'fengshui': '风水堪舆',
                    'huangli': '黄道吉日', 'liuyao': '六爻占卜',
                    'caishen': '财神方位', 'analyze': '智能分析',
                    'image-analyze': '智能分析',
                }
                module_name = module_names.get(module_id, module_id)
                token = (request.cookies.get('token')
                         or request.headers.get('Authorization', '').replace('Bearer ', ''))
                user_id = None
                if token:
                    try:
                        user_id = verify_token(token) or None
                    except Exception:
                        pass
                track_divination(
                    user_id=user_id,
                    module_name=module_name,
                    module_id=module_id,
                    is_logged_in=bool(user_id),
                    client_ip=request.remote_addr or '',
                    user_agent=request.headers.get('User-Agent', '')[:200],
                )
            except Exception:
                pass

        if path.startswith('/api/vip/'):
            try:
                vip_events = {
                    '/api/vip/watch-ad': ('ad_watch', '观看广告'),
                    '/api/vip/bottom-ad': ('bottom_ad', '底部广告'),
                    '/api/vip/checkin': ('checkin', '每日签到'),
                    '/api/vip/wheel': ('wheel', '转盘抽奖'),
                }
                evt = vip_events.get(path)
                if evt:
                    token = (request.cookies.get('token')
                             or request.headers.get('Authorization', '').replace('Bearer ', ''))
                    if token:
                        try:
                            uid = verify_token(token)
                            if uid:
                                track_vip(uid, evt[0], evt[1])
                        except Exception:
                            pass
            except Exception:
                pass

        return response


def create_app(config_object=None):
    """创建并配置 Flask 应用。"""
    if config_object is None:
        from config import get_config
        config_object = get_config()

    # 生产环境 fail-fast 校验（密钥缺失直接拒绝启动）
    validate = getattr(config_object, 'validate', None)
    if callable(validate):
        validate()

    project_root = config_object.PROJECT_ROOT
    app = Flask(
        __name__,
        static_folder=project_root,       # 静态资源仍从项目根目录提供（html/css/js/modules）
        static_url_path='',
        template_folder=os.path.join(project_root, 'templates'),
    )
    app.config.from_object(config_object)
    config_object.ensure_dirs()

    # 安全加固：CORS 仅允许本站域名，禁止任意来源跨域读取接口
    allowed_origins = os.environ.get(
        'ALLOWED_ORIGINS',
        'https://xuanjisuanming.top https://www.xuanjisuanming.top'
    ).split()
    CORS(app, resources={r'/api/*': {'origins': allowed_origins, 'supports_credentials': True}})
    limiter.storage_uri = app.config.get('RATELIMIT_STORAGE_URI', 'memory://')
    limiter.default_limits = [app.config.get('RATELIMIT_DEFAULT', '100 per minute')]
    limiter.init_app(app)

    _register_repositories(app)

    from app.api import register_blueprints
    register_blueprints(app)

    _register_analytics_hooks(app)

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': '接口不存在'}), 404
        return e

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'success': False, 'message': '服务器内部错误'}), 500

    return app
