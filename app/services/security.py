"""
安全服务：密码哈希（PBKDF2）与 JWT 签发/校验。

密钥一律来自应用配置（环境变量），不再有硬编码回退。
"""
import hashlib
import random
import string
from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app


# ---------- 密码 ----------

def hash_password(password, salt=None):
    if salt is None:
        salt = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    password_hash = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000
    ).hex()
    return f"{salt}${password_hash}"


def verify_password(password, hashed):
    try:
        salt, _ = hashed.split('$')
    except (ValueError, AttributeError):
        return False
    return hash_password(password, salt) == hashed


# ---------- JWT ----------

def _secret():
    """优先取请求上下文中的配置，其次取环境变量。"""
    try:
        return current_app.config['SECRET_KEY']
    except RuntimeError:
        import os
        return os.environ.get('SECRET_KEY') or os.environ.get('JWT_SECRET', '')


def generate_token(user_id, days=None):
    days = days or current_app.config.get('JWT_EXPIRE_DAYS', 7)
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(days=days),
    }
    return jwt.encode(payload, _secret(), algorithm='HS256')


def verify_token(token):
    try:
        payload = jwt.decode(token, _secret(), algorithms=['HS256'])
        return payload['user_id']
    except Exception:
        return None
