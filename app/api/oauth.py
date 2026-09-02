"""第三方登录：微信/QQ 简版登录 + OAuth 2.0（GitHub/微信/QQ）"""

from datetime import datetime

from flask import Blueprint, jsonify, make_response, request

from app.api.deps import load_users
from app.api.deps import save_users
from app.services.nickname import generate_random_avatar
from app.services.oauth_providers import _generate_oauth_username
from app.services.oauth_providers import create_oauth_state
from app.services.oauth_providers import get_enabled_providers
from app.services.oauth_providers import get_provider
from app.services.oauth_providers import verify_oauth_state
from app.services.security import generate_token

import random
import string


from app.api.deps import _ensure_linked_accounts, load_users, save_users

bp = Blueprint('oauth', __name__)

@bp.route('/api/wechat-login', methods=['POST'])
def wechat_login():
    """微信登录（已迁移到 OAuth 流程）"""
    return jsonify({'success': False, 'message': '请使用页面上的"微信登录"按钮进行扫码登录'}), 400

@bp.route('/api/qq-login', methods=['POST'])
def qq_login():
    """QQ登录（已迁移到 OAuth 流程）"""
    return jsonify({'success': False, 'message': '请使用页面上的"QQ登录"按钮进行授权登录'}), 400


# ========== OAuth 第三方登录 ==========

def _oauth_login_or_register(provider_key, oauth_info):
    """
    OAuth 统一登录/注册逻辑：
    1. 先按 linked_accounts 查找
    2. 再按邮箱匹配（自动合并）
    3. 否则创建新用户
    返回 (user_dict, is_new_user)
    """
    provider_uid = oauth_info['provider_uid']
    email = oauth_info.get('email', '').strip()
    nickname = oauth_info.get('nickname', '')
    avatar = oauth_info.get('avatar', '')

    users = load_users()

    # 1. 查找已绑定的用户
    for u in users:
        u = _ensure_linked_accounts(u)
        if u.get('linked_accounts', {}).get(provider_key) == provider_uid:
            return u, False

    # 2. 邮箱匹配（自动合并）—— 仅当邮箱已经 provider 验证通过才合并，
    #    防止攻击者用未验证邮箱接管他人账号
    if email and oauth_info.get('email_verified'):
        for u in users:
            if u.get('email', '').strip().lower() == email.lower():
                u = _ensure_linked_accounts(u)
                u['linked_accounts'][provider_key] = provider_uid
                save_users(users)
                return u, False

    # 3. 创建新用户
    uid = 'user_' + ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    username_base = _generate_oauth_username(provider_key, nickname)
    username = username_base
    counter = 1
    while any(u['username'] == username for u in users):
        username = f"{username_base}{counter}"
        counter += 1

    new_user = {
        'id': uid,
        'username': username,
        'nickname': nickname or username,
        'password': '',  # OAuth 用户无密码
        'email': email,
        'phone': '',
        'avatar': avatar,
        'avatar_type': 'custom' if avatar else 'emoji',
        'avatar_preset': '' if avatar else generate_random_avatar(),
        'birthday': '',
        'gender': '',
        'create_time': datetime.now().isoformat(),
        'last_login': datetime.now().isoformat(),
        'status': 'active',
        'vip_level': 'basic',
        'vip_expire': None,
        'ad_watch_count': 0,
        'ad_watch_date': '',
        'tutorial_shown': False,
        'linked_accounts': {provider_key: provider_uid},
    }
    users.append(new_user)
    save_users(users)
    return new_user, True


@bp.route('/api/oauth/status', methods=['GET'])
def oauth_status():
    """查询各平台 OAuth 启用状态"""
    return jsonify({'success': True, 'providers': get_enabled_providers()}), 200


@bp.route('/api/oauth/<provider>', methods=['GET'])
def oauth_authorize(provider):
    """发起 OAuth 授权：跳转到第三方平台授权页"""
    p = get_provider(provider)
    if not p:
        return jsonify({'success': False, 'message': f'不支持的登录平台: {provider}'}), 400
    if not p.is_enabled:
        return jsonify({'success': False, 'message': f'{p.PROVIDER_NAME}登录暂未开放，敬请期待'}), 400

    state = create_oauth_state(provider)
    auth_url = p.get_authorization_url(state)
    resp = make_response('', 302)
    resp.headers['Location'] = auth_url
    return resp


@bp.route('/api/oauth/<provider>/callback', methods=['GET'])
def oauth_callback(provider):
    """OAuth 回调处理：用 code 换 token → 获取用户信息 → 登录/注册 → 跳转首页"""
    p = get_provider(provider)
    if not p:
        return '<h3>不支持的登录平台</h3>', 400
    if not p.is_enabled:
        return f'<h3>{p.PROVIDER_NAME}登录暂未开放</h3>', 400

    # 验证 state（防 CSRF）
    state = request.args.get('state', '')
    if not verify_oauth_state(state):  # 返回条目或 None
        return '<script>alert("登录会话已过期，请重新登录");window.location.href="/login.html";</script>'

    # 处理错误（用户拒绝授权等）
    error = request.args.get('error', '')
    error_description = request.args.get('error_description', '')
    if error:
        # 安全加固：对第三方回调参数做 HTML 转义，阻断反射型 XSS
        import html as _html
        safe_desc = _html.escape(error_description or error)
        return f'<script>alert("授权失败: {safe_desc}");window.location.href="/login.html";</script>'

    code = request.args.get('code', '')
    if not code:
        return '<script>alert("授权失败：缺少授权码");window.location.href="/login.html";</script>'

    # 换 token
    token_data = p.exchange_code(code)
    if not token_data:
        return '<script>alert("换取访问令牌失败，请重试");window.location.href="/login.html";</script>'

    # 获取用户信息
    oauth_info = p.get_user_info(token_data)
    if not oauth_info:
        return '<script>alert("获取用户信息失败，请重试");window.location.href="/login.html";</script>'

    # 登录或注册
    user, is_new = _oauth_login_or_register(provider, oauth_info)

    # 更新最后登录时间
    users = load_users()
    for i, u in enumerate(users):
        if u['id'] == user['id']:
            users[i]['last_login'] = datetime.now().isoformat()
            break
    save_users(users)

    # 生成 JWT token
    token = generate_token(user['id'])

    # 设置 cookie 并跳转首页
    resp = make_response('', 302)
    resp.headers['Location'] = '/'
    resp.set_cookie('token', token, max_age=7*24*3600, httponly=True, samesite='Lax', secure=True)
    return resp
