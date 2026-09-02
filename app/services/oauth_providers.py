"""
OAuth 第三方登录（GitHub / 微信开放平台 / QQ 互联）。

相对旧版 api/oauth.py 的变更：
1. state 不再存进程内存（多 worker/重启即失效），改由 OAuthStateRepo 文件持久化；
2. 平台启停状态动态读取环境变量（原为导入时固化的模块级常量）；
3. 环境变量名向后兼容（沿用 GITHUB_CLIENT_ID 等历史命名）。
"""
import os
import secrets
from abc import ABC, abstractmethod
from urllib.parse import urlencode

import requests

from app.repositories import OAuthStateRepo


# ── 配置（动态读取） ───────────────────────────────────────

def _env(*names, default=''):
    for n in names:
        v = os.environ.get(n, '')
        if v:
            return v
    return default


def _site_url():
    return _env('SITE_URL', default='http://localhost:5000').rstrip('/')


def get_provider_status():
    return {
        'github': bool(_env('OAUTH_GITHUB_CLIENT_ID', 'GITHUB_CLIENT_ID')
                       and _env('OAUTH_GITHUB_CLIENT_SECRET', 'GITHUB_CLIENT_SECRET')),
        'wechat': bool(_env('OAUTH_WECHAT_APPID', 'WECHAT_APP_ID')
                       and _env('OAUTH_WECHAT_SECRET', 'WECHAT_APP_SECRET')),
        'qq': bool(_env('OAUTH_QQ_APPID', 'QQ_APP_ID')
                   and _env('OAUTH_QQ_SECRET', 'QQ_APP_KEY')),
    }


# ── 工具函数 ──────────────────────────────────────────────

def _normalize_oauth_user_info(provider_key, raw, email_verified=False):
    info = {
        'provider': provider_key,
        'provider_uid': '',
        'nickname': '',
        'avatar': '',
        'email': '',
        'email_verified': bool(email_verified),  # 安全：标记邮箱是否经 provider 验证
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
    elif provider_key == 'qq':
        info['provider_uid'] = raw.get('openid', '')
        info['nickname'] = raw.get('nickname', '')
        info['avatar'] = raw.get('figureurl_qq_2', '') or raw.get('figureurl_qq_1', '')
    return info


def _generate_oauth_username(provider_key, nickname):
    prefix_map = {'github': 'gh', 'wechat': 'wx', 'qq': 'qq'}
    prefix = prefix_map.get(provider_key, 'oauth')
    clean = ''.join(c for c in nickname
                    if c.isalnum() or c == '_' or '\u4e00' <= c <= '\u9fff')
    if not clean:
        clean = prefix + '_user'
    return f"{prefix}_{clean}"


# ── OAuth State（文件持久化，多 worker 安全） ─────────────

def _state_repo() -> OAuthStateRepo:
    from flask import current_app
    return current_app.extensions['oauth_state_repo']


def create_oauth_state(provider, redirect=''):
    token = secrets.token_urlsafe(32)
    _state_repo().save(token, provider, redirect)
    return token


def verify_oauth_state(state):
    """校验并一次性消费 state，成功返回条目 dict，失败返回 None。"""
    return _state_repo().pop(state)


# ── Provider 抽象与实现 ───────────────────────────────────

class OAuthProvider(ABC):
    PROVIDER_KEY: str = ''
    PROVIDER_NAME: str = ''

    @abstractmethod
    def get_authorization_url(self, state: str) -> str: ...

    @abstractmethod
    def exchange_code(self, code: str) -> dict | None: ...

    @abstractmethod
    def get_user_info(self, token_data: dict) -> dict | None: ...

    @property
    def is_enabled(self) -> bool:
        return get_provider_status().get(self.PROVIDER_KEY, False)


class GitHubProvider(OAuthProvider):
    PROVIDER_KEY = 'github'
    PROVIDER_NAME = 'GitHub'

    AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
    TOKEN_URL = 'https://github.com/login/oauth/access_token'
    USER_API = 'https://api.github.com/user'
    EMAILS_API = 'https://api.github.com/user/emails'

    def _client_id(self):
        return _env('OAUTH_GITHUB_CLIENT_ID', 'GITHUB_CLIENT_ID')

    def _client_secret(self):
        return _env('OAUTH_GITHUB_CLIENT_SECRET', 'GITHUB_CLIENT_SECRET')

    def get_authorization_url(self, state: str) -> str:
        params = {
            'client_id': self._client_id(),
            'redirect_uri': f'{_site_url()}/api/oauth/github/callback',
            'scope': 'read:user user:email',
            'state': state,
        }
        return f'{self.AUTHORIZE_URL}?{urlencode(params)}'

    def exchange_code(self, code: str) -> dict | None:
        resp = requests.post(
            self.TOKEN_URL,
            headers={'Accept': 'application/json'},
            data={
                'client_id': self._client_id(),
                'client_secret': self._client_secret(),
                'code': code,
                'redirect_uri': f'{_site_url()}/api/oauth/github/callback',
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

        resp = requests.get(self.USER_API, headers=headers, timeout=15)
        if resp.status_code != 200:
            return None
        raw = resp.json()

        email = raw.get('email', '')
        verified = False
        if not email:
            try:
                emails_resp = requests.get(self.EMAILS_API, headers=headers, timeout=15)
                if emails_resp.status_code == 200:
                    emails = emails_resp.json()
                    # 安全：优先选已验证的邮箱，绝不拿未验证邮箱去自动合并账号
                    verified_list = [e for e in emails if e.get('verified')]
                    primary = next((e for e in emails if e.get('primary')), None)
                    chosen = (verified_list[0] if verified_list
                              else (primary or (emails[0] if emails else None)))
                    if chosen:
                        email = chosen.get('email', '')
                        verified = bool(chosen.get('verified'))
            except Exception:
                pass
        else:
            # raw.email 直接来自 /user（通常已验证），保守标记为已验证
            verified = True
        raw['email'] = email
        raw['email_verified'] = verified
        return _normalize_oauth_user_info('github', raw, email_verified=verified)


class WeChatProvider(OAuthProvider):
    PROVIDER_KEY = 'wechat'
    PROVIDER_NAME = '微信'

    AUTHORIZE_URL = 'https://open.weixin.qq.com/connect/qrconnect'
    TOKEN_URL = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    USER_INFO_URL = 'https://api.weixin.qq.com/sns/userinfo'

    def _appid(self):
        return _env('OAUTH_WECHAT_APPID', 'WECHAT_APP_ID')

    def _secret(self):
        return _env('OAUTH_WECHAT_SECRET', 'WECHAT_APP_SECRET')

    def get_authorization_url(self, state: str) -> str:
        params = {
            'appid': self._appid(),
            'redirect_uri': f'{_site_url()}/api/oauth/wechat/callback',
            'response_type': 'code',
            'scope': 'snsapi_login',
            'state': state,
        }
        return f'{self.AUTHORIZE_URL}?{urlencode(params)}#wechat_redirect'

    def exchange_code(self, code: str) -> dict | None:
        resp = requests.get(
            self.TOKEN_URL,
            params={
                'appid': self._appid(),
                'secret': self._secret(),
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
        data['openid'] = token_data.get('openid', data.get('openid', ''))
        data['unionid'] = token_data.get('unionid', data.get('unionid', ''))
        return _normalize_oauth_user_info('wechat', data)


class QQProvider(OAuthProvider):
    PROVIDER_KEY = 'qq'
    PROVIDER_NAME = 'QQ'

    AUTHORIZE_URL = 'https://graph.qq.com/oauth2.0/authorize'
    TOKEN_URL = 'https://graph.qq.com/oauth2.0/token'
    OPENID_URL = 'https://graph.qq.com/oauth2.0/me'
    USER_INFO_URL = 'https://graph.qq.com/user/get_user_info'

    def _appid(self):
        return _env('OAUTH_QQ_APPID', 'QQ_APP_ID')

    def _key(self):
        return _env('OAUTH_QQ_SECRET', 'QQ_APP_KEY')

    def get_authorization_url(self, state: str) -> str:
        params = {
            'response_type': 'code',
            'client_id': self._appid(),
            'redirect_uri': f'{_site_url()}/api/oauth/qq/callback',
            'scope': 'get_user_info',
            'state': state,
        }
        return f'{self.AUTHORIZE_URL}?{urlencode(params)}'

    def exchange_code(self, code: str) -> dict | None:
        resp = requests.get(
            self.TOKEN_URL,
            params={
                'grant_type': 'authorization_code',
                'client_id': self._appid(),
                'client_secret': self._key(),
                'code': code,
                'redirect_uri': f'{_site_url()}/api/oauth/qq/callback',
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

        resp = requests.get(
            self.USER_INFO_URL,
            params={
                'access_token': access_token,
                'oauth_consumer_key': self._appid(),
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


PROVIDERS: dict = {
    'github': GitHubProvider(),
    'wechat': WeChatProvider(),
    'qq': QQProvider(),
}


def get_provider(provider_key: str):
    return PROVIDERS.get(provider_key)


def get_enabled_providers() -> dict:
    return {k: v for k, v in get_provider_status().items() if v}
