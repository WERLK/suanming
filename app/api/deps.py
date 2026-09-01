"""
API 层公共依赖（Dependency）。

职责：
1. 提供与旧 api/app.py 同名同签名的数据访问函数（load_users / save_users /
   验证码存取 / Token 存取），使迁移自旧代码的路由函数体零改动；
2. 提供统一的 @require_auth 装饰器与 g.current_user（旧代码在 7 处路由
   重复手写 token 解析，新代码一律使用本装饰器）；
3. 提供 _vip_service() 工厂（旧代码每请求 VipService(USERS_FILE) 实例化）。
"""
import functools

from flask import current_app, g, jsonify, request

from app.repositories import CaptchaRepo, TokenRepo, UserRepo
from app.services.security import verify_token
from app.services.vip import VipService


# ---------- 仓储访问（从应用扩展容器获取，随 app 生命周期） ----------

def user_repo() -> UserRepo:
    return current_app.extensions['user_repo']


def token_repo() -> TokenRepo:
    return current_app.extensions['token_repo']


def captcha_repo() -> CaptchaRepo:
    return current_app.extensions['captcha_repo']


def users_file():
    return current_app.config['USERS_FILE']


def _vip_service():
    return VipService(current_app.config['USERS_FILE'])


# ---------- 用户数据（旧签名兼容） ----------

def load_users():
    return user_repo().all()


def save_users(users):
    user_repo().save(users)


# ---------- 重置 Token（旧签名兼容） ----------

def load_tokens():
    return token_repo().all()


def save_tokens(tokens):
    token_repo().save(tokens)


# ---------- 验证码存取（旧签名兼容） ----------

def _get_captcha_entry(captcha_id):
    return captcha_repo().get(captcha_id)


def _set_captcha_entry(captcha_id, entry):
    captcha_repo().set(captcha_id, entry)


def _delete_captcha_entry(captcha_id):
    captcha_repo().delete(captcha_id)


# ---------- 鉴权 ----------

def get_token_from_request():
    """从 Cookie 或 Authorization 头提取 JWT。"""
    return (request.cookies.get('token')
            or request.headers.get('Authorization', '').replace('Bearer ', ''))


def get_current_user_id():
    """返回当前登录用户 id（未登录返回 None）。"""
    if hasattr(g, 'current_user_id'):
        return g.current_user_id
    token = get_token_from_request()
    return verify_token(token) if token else None


def get_current_user():
    """返回当前登录用户完整 dict（未登录返回 None）。"""
    uid = get_current_user_id()
    if not uid:
        return None
    for u in load_users():
        if u.get('id') == uid or u.get('user_id') == uid:
            return u
    return None


def require_auth(f):
    """登录态校验装饰器：未登录返回 401，成功将 user 挂到 g.current_user。"""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': '登录已过期，请重新登录'}), 401
        g.current_user_id = user_id
        g.current_user = get_current_user()
        if g.current_user is None:
            return jsonify({'success': False, 'message': '用户不存在'}), 401
        return f(*args, **kwargs)

    return wrapper


# ---------- 用户字段兜底（数据迁移友好：老用户缺字段时自动补全） ----------

def _get_today():
    from datetime import datetime as _dt
    return _dt.now().strftime('%Y-%m-%d')


def _safe_parse_datetime(date_str):
    """安全解析日期时间字符串，支持 ISO 及常见格式。"""
    from datetime import datetime as _dt
    if not date_str:
        return None
    if isinstance(date_str, _dt):
        return date_str
    try:
        return _dt.fromisoformat(date_str)
    except (ValueError, TypeError):
        pass
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d %H:%M:%S', '%Y/%m/%d'):
        try:
            return _dt.strptime(date_str, fmt)
        except (ValueError, TypeError):
            pass
    return None


def _get_auth_user():
    """获取当前登录用户，返回 (user, users) 或 None。

    兼容旧签名：优先 Authorization 头，Cookie 兜底。
    """
    header_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    cookie_token = request.cookies.get('token')
    user_id = None
    if header_token:
        user_id = verify_token(header_token)
    if not user_id and cookie_token:
        user_id = verify_token(cookie_token)
    if not user_id:
        return None
    users = load_users()
    for u in users:
        if u.get('id') == user_id or u.get('user_id') == user_id:
            return u, users
    return None


def _ensure_vip_fields(user):
    defaults = {
        'vip_level': 'free', 'vip_expire': None, 'ad_watch_count': 0,
        'ad_watch_date': '', 'total_ad_count': 0, 'points': 0,
        'last_checkin': '', 'checkin_streak': 0, 'wheel_spins_today': 0,
        'wheel_date': '', 'last_login_reward_date': '',
        'bottom_ad_count': 0, 'bottom_ad_date': '',
    }
    for k, v in defaults.items():
        if k not in user:
            user[k] = v
    return user


def _ensure_realname_fields(user):
    defaults = {
        'real_name': '', 'id_number_hash': '', 'id_last4': '',
        'id_verified': False, 'id_region': '', 'id_region_code': '',
        'verify_time': '', 'idcard_image': '',
        'idcard_image_front': '', 'idcard_image_back': '',
        'idcard_upload_time': '',
    }
    for k, v in defaults.items():
        if k not in user:
            user[k] = v
    return user


def _ensure_tutorial_field(user):
    if 'tutorial_shown' not in user:
        user['tutorial_shown'] = False
    return user


def _ensure_linked_accounts(user):
    if 'linked_accounts' not in user:
        user['linked_accounts'] = {}
    return user
