"""
玄机算命网 - OAuth 第三方登录模块
支持: GitHub / 微信开放平台 / QQ互联

环境变量配置:
  GITHUB_CLIENT_ID       GitHub OAuth App Client ID
  GITHUB_CLIENT_SECRET   GitHub OAuth App Client Secret
  WECHAT_APP_ID          微信开放平台 AppID
  WECHAT_APP_SECRET      微信开放平台 AppSecret
  QQ_APP_ID              QQ互联 App ID
  QQ_APP_KEY             QQ互联 App Key
  SITE_URL               站点完整 URL (默认 http://localhost:5000)
"""

import os
import json
import time
import secrets
import hashlib
import hmac
from abc import ABC, abstractmethod
from urllib.parse import urlencode

import requests

# ── 配置 ────────────────────────────────────────────────────

SITE_URL = os.environ.get('SITE_URL', 'http://localhost:5000').rstrip('/')

# GitHub
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID', '')
GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET', '')
GITHUB_ENABLED = bool(GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET)

# 微信开放平台
WECHAT_APP_ID = os.environ.get('WECHAT_APP_ID', '')
WECHAT_APP_SECRET = os.environ.get('WECHAT_APP_SECRET', '')
WECHAT_ENABLED = bool(WECHAT_APP_ID and WECHAT_APP_SECRET)

# QQ互联
QQ_APP_ID = os.environ.get('QQ_APP_ID', '')
QQ_APP_KEY = os.environ.get('QQ_APP_KEY', '')
QQ_ENABLED = bool(QQ_APP_ID and QQ_APP_KEY)

PROVIDER_STATUS = {
    'github': GITHUB_ENABLED,
    'wechat': WECHAT_ENABLED,
    'qq': QQ_ENABLED,
}


# ── 工具函数 ────────────────────────────────────────────────

def _normalize_oauth_user_info(provider_key, raw):
    """将各平台返回的原始用户信息统一为标准格式"""
    info = {
        'provider': provider_key,
        'provider_uid': '',
        'nickname': '',
        'avatar': '',
        'email': '',
    }

    if provider_key == 'github':
        info['provider_uid'] = str(raw.get('id', ''))
        info['nickname'] = raw.get('login', '') or raw.get('name', '')
        info['avatar'] = raw.get('avatar_url', '')
        info['email'] = raw.get('email', '')

    elif provider_key == 'wechat':
        info['provider_uid'] = raw.get('unionid', '') or raw.get('openid', '')
        info['nickname'] = raw.get('nickname', '')
        info['avatar'] = raw.get('headimgurl', '')
        # 微信不直接返回邮箱

    elif provider_key == 'qq':
        info['provider_uid'] = raw.get('openid', '')
        info['nickname'] = raw.get('nickname', '')
        info['avatar'] = raw.get('figureurl_qq_2', '') or raw.get('figureurl_qq_1', '')
        # QQ 互联不返回邮箱

    return info


def _generate_oauth_username(provider_key, nickname):
    """生成 OAuth 用户的默认用户名"""
    prefix_map = {'github': 'gh', 'wechat': 'wx', 'qq': 'qq'}
    prefix = prefix_map.get(provider_key, 'oauth')

    # 清理昵称中的特殊字符，只保留字母数字下划线中文
    clean = ''.join(c for c in nickname if c.isalnum() or c == '_' or '\u4e00' <= c <= '\u9fff')
    if not clean:
        clean = prefix + '_user'

    return f"{prefix}_{clean}"


# ── OAuth State 管理 ────────────────────────────────────────

# 简单的内存存储（生产环境可改用 Redis）
_oauth_states = {}  # { state_token: {'expire': timestamp} }


def create_oauth_state():
    """创建 OAuth state 参数（防 CSRF），返回 state token"""
    token = secrets.token_urlsafe(32)
    _oauth_states[token] = {'expire': time.time() + 600}  # 10 分钟有效
    return token


def verify_oauth_state(state):
    """验证 OAuth state 参数，验证成功删除并返回 True"""
    entry = _oauth_states.pop(state, None)
    if not entry:
        return False
    if time.time() > entry['expire']:
        return False
    return True


# ── OAuth Provider 基类 ─────────────────────────────────────

class OAuthProvider(ABC):
    """OAuth 2.0 Provider 抽象基类"""

    PROVIDER_KEY: str = ''       # github | wechat | qq
    PROVIDER_NAME: str = ''      # GitHub | 微信 | QQ

    @abstractmethod
    def get_authorization_url(self, state: str) -> str:
        """返回第三方授权页面 URL"""
        ...

    @abstractmethod
    def exchange_code(self, code: str) -> dict | None:
        """用 authorization code 换取 access_token，返回 token 相关字典"""
        ...

    @abstractmethod
    def get_user_info(self, token_data: dict) -> dict | None:
        """用 token_data 获取用户信息，返回标准化的用户信息字典"""
        ...

    @property
    def is_enabled(self) -> bool:
        return PROVIDER_STATUS.get(self.PROVIDER_KEY, False)


# ── GitHub Provider ─────────────────────────────────────────

class GitHubProvider(OAuthProvider):
    PROVIDER_KEY = 'github'
    PROVIDER_NAME = 'GitHub'

    AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
    TOKEN_URL = 'https://github.com/login/oauth/access_token'
    USER_API = 'https://api.github.com/user'
    EMAILS_API = 'https://api.github.com/user/emails'

    def get_authorization_url(self, state: str) -> str:
        params = {
            'client_id': GITHUB_CLIENT_ID,
            'redirect_uri': f'{SITE_URL}/api/oauth/github/callback',
            'scope': 'read:user user:email',
            'state': state,
        }
        return f'{self.AUTHORIZE_URL}?{urlencode(params)}'

    def exchange_code(self, code: str) -> dict | None:
        resp = requests.post(
            self.TOKEN_URL,
            headers={'Accept': 'application/json'},
            data={
                'client_id': GITHUB_CLIENT_ID,
                'client_secret': GITHUB_CLIENT_SECRET,
                'code': code,
                'redirect_uri': f'{SITE_URL}/api/oauth/github/callback',
            },
            timeout=15,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        if 'error' in data:
            return None
        return {'access_token': data.get('access_token', '')}

    def get_user_info(self, token_data: dict) -> dict | None:
        access_token = token_data.get('access_token', '')
        headers = {'Authorization': f'Bearer {access_token}', 'Accept': 'application/json'}

        # 获取用户基本信息
        resp = requests.get(self.USER_API, headers=headers, timeout=15)
        if resp.status_code != 200:
            return None
        raw = resp.json()

        # GitHub 的 email 可能在 user 对象中为 null（设为 private 时），需要单独请求
        email = raw.get('email', '')
        if not email:
            try:
                emails_resp = requests.get(self.EMAILS_API, headers=headers, timeout=15)
                if emails_resp.status_code == 200:
                    emails = emails_resp.json()
                    primary = next((e for e in emails if e.get('primary')), None)
                    verified = next((e for e in emails if e.get('verified')), None)
                    chosen = primary or verified or (emails[0] if emails else None)
                    if chosen:
                        email = chosen.get('email', '')
            except Exception:
                pass

        raw['email'] = email
        return _normalize_oauth_user_info('github', raw)


# ── 微信开放平台 Provider ───────────────────────────────────

class WeChatProvider(OAuthProvider):
    """微信开放平台 网站应用 登录 (QR Connect)"""

    PROVIDER_KEY = 'wechat'
    PROVIDER_NAME = '微信'

    AUTHORIZE_URL = 'https://open.weixin.qq.com/connect/qrconnect'
    TOKEN_URL = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    USER_INFO_URL = 'https://api.weixin.qq.com/sns/userinfo'

    def get_authorization_url(self, state: str) -> str:
        params = {
            'appid': WECHAT_APP_ID,
            'redirect_uri': f'{SITE_URL}/api/oauth/wechat/callback',
            'response_type': 'code',
            'scope': 'snsapi_login',
            'state': state,
        }
        # 微信需要在 URL 末尾加 #wechat_redirect
        return f'{self.AUTHORIZE_URL}?{urlencode(params)}#wechat_redirect'

    def exchange_code(self, code: str) -> dict | None:
        resp = requests.get(
            self.TOKEN_URL,
            params={
                'appid': WECHAT_APP_ID,
                'secret': WECHAT_APP_SECRET,
                'code': code,
                'grant_type': 'authorization_code',
            },
            timeout=15,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        if 'errcode' in data:
            return None
        return {
            'access_token': data.get('access_token', ''),
            'refresh_token': data.get('refresh_token', ''),
            'openid': data.get('openid', ''),
            'unionid': data.get('unionid', ''),
        }

    def get_user_info(self, token_data: dict) -> dict | None:
        resp = requests.get(
            self.USER_INFO_URL,
            params={
                'access_token': token_data.get('access_token', ''),
                'openid': token_data.get('openid', ''),
            },
            timeout=15,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        if 'errcode' in data:
            return None
        # 补上 openid / unionid
        data['openid'] = token_data.get('openid', data.get('openid', ''))
        data['unionid'] = token_data.get('unionid', data.get('unionid', ''))
        return _normalize_oauth_user_info('wechat', data)


# ── QQ 互联 Provider ───────────────────────────────────────

class QQProvider(OAuthProvider):
    """QQ互联 OAuth 2.0"""

    PROVIDER_KEY = 'qq'
    PROVIDER_NAME = 'QQ'

    AUTHORIZE_URL = 'https://graph.qq.com/oauth2.0/authorize'
    TOKEN_URL = 'https://graph.qq.com/oauth2.0/token'
    OPENID_URL = 'https://graph.qq.com/oauth2.0/me'
    USER_INFO_URL = 'https://graph.qq.com/user/get_user_info'

    def get_authorization_url(self, state: str) -> str:
        params = {
            'response_type': 'code',
            'client_id': QQ_APP_ID,
            'redirect_uri': f'{SITE_URL}/api/oauth/qq/callback',
            'scope': 'get_user_info',
            'state': state,
        }
        return f'{self.AUTHORIZE_URL}?{urlencode(params)}'

    def exchange_code(self, code: str) -> dict | None:
        resp = requests.get(
            self.TOKEN_URL,
            params={
                'grant_type': 'authorization_code',
                'client_id': QQ_APP_ID,
                'client_secret': QQ_APP_KEY,
                'code': code,
                'redirect_uri': f'{SITE_URL}/api/oauth/qq/callback',
                'fmt': 'json',
            },
            timeout=15,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        if 'error' in data:
            return None
        return {'access_token': data.get('access_token', '')}

    def get_user_info(self, token_data: dict) -> dict | None:
        access_token = token_data.get('access_token', '')

        # 第一步：获取 openid
        resp = requests.get(
            self.OPENID_URL,
            params={'access_token': access_token, 'fmt': 'json'},
            timeout=15,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        if 'error' in data:
            return None
        openid = data.get('openid', '')

        # 第二步：用 openid + access_token + appid 获取用户信息
        resp = requests.get(
            self.USER_INFO_URL,
            params={
                'access_token': access_token,
                'oauth_consumer_key': QQ_APP_ID,
                'openid': openid,
            },
            timeout=15,
        )
        if resp.status_code != 200:
            return None
        user_data = resp.json()
        if user_data.get('ret') != 0:
            return None

        user_data['openid'] = openid
        return _normalize_oauth_user_info('qq', user_data)


# ── Provider 注册表 ─────────────────────────────────────────

PROVIDERS: dict[str, OAuthProvider] = {
    'github': GitHubProvider(),
    'wechat': WeChatProvider(),
    'qq': QQProvider(),
}


def get_provider(provider_key: str) -> OAuthProvider | None:
    """获取指定平台 Provider 实例"""
    return PROVIDERS.get(provider_key)


def get_enabled_providers() -> dict:
    """返回所有已启用的平台"""
    return {k: v for k, v in PROVIDER_STATUS.items() if v}
