"""
数据访问层（Repository 模式）。

统一封装 JSON 文件存储：带 fcntl 文件锁的原子读写、惰性初始化。
上层（services / api）不直接触碰文件路径，未来切换 SQLite/MySQL
只需替换本包实现，业务代码零改动。
"""
import fcntl
import json
import os
import threading
from datetime import datetime


class JsonStore:
    """带文件锁的 JSON 存储（支持多 worker 并发）。"""

    def __init__(self, path, default):
        self.path = path
        self.default = default
        self._local_lock = threading.Lock()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            self._write(default)

    # ---------- 基础读写 ----------

    def _read(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    return json.load(f)
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except (FileNotFoundError, json.JSONDecodeError):
            return json.loads(json.dumps(self.default))

    def _write(self, data):
        """原子写：先写临时文件再 rename，避免 truncate 过程中崩溃导致数据丢失。"""
        tmp = self.path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        os.replace(tmp, self.path)

    # ---------- 对外 API ----------

    def load(self):
        with self._local_lock:
            return self._read()

    def save(self, data):
        with self._local_lock:
            self._write(data)

    def update(self, fn):
        """读-改-写原子操作：fn(data) -> data（回调内修改后返回）。"""
        with self._local_lock:
            data = self._read()
            data = fn(data)
            if data is not None:
                self._write(data)
            return data


class UserRepo:
    """用户表（users.json）。"""

    def __init__(self, path):
        self.store = JsonStore(path, default=[])

    def all(self):
        return self.store.load()

    def save(self, users):
        self.store.save(users)

    def find(self, **filters):
        """按字段查找第一个匹配用户，例如 find(username='foo')。"""
        for u in self.all():
            if all(u.get(k) == v for k, v in filters.items()):
                return u
        return None

    def find_by_login(self, login):
        """用户名 / 邮箱 / 手机号任一匹配。"""
        for u in self.all():
            if login in (u.get('username'), u.get('email'), u.get('phone')):
                return u
        return None

    def add(self, user):
        def _add(users):
            users.append(user)
            return users
        self.store.update(_add)

    def mutate(self, user_id, fn):
        """定位用户并原地修改，返回更新后的用户（或 None）。"""
        result = {}

        def _mutate(users):
            for u in users:
                if u.get('user_id') == user_id:
                    fn(u)
                    result['user'] = u
                    return users
            result['user'] = None
            return users

        self.store.update(_mutate)
        return result.get('user')


class TokenRepo:
    """密码重置 Token 表（tokens.json）。"""

    def __init__(self, path):
        self.store = JsonStore(path, default={})

    def all(self):
        return self.store.load()

    def get(self, token):
        return self.all().get(token)

    def set(self, token, payload):
        def _set(data):
            data[token] = payload
            return data
        self.store.update(_set)

    def delete(self, token):
        def _del(data):
            data.pop(token, None)
            return data
        self.store.update(_del)

    def purge_expired(self, ttl_hours=2):
        now = datetime.now().isoformat()

        def _purge(data):
            return {k: v for k, v in data.items()
                    if v.get('expire_time', '') > now}
        return self.store.update(_purge)


class CaptchaRepo:
    """验证码存储（captcha_store.json），带 TTL 清理。"""

    def __init__(self, path):
        self.store = JsonStore(path, default={})

    @staticmethod
    def _expired(entry):
        return datetime.now().isoformat() > entry.get('expire_time', '')

    def get(self, captcha_id):
        entry = None

        def _get(data):
            nonlocal entry
            e = data.get(captcha_id)
            if e is None:
                return data
            if self._expired(e):
                data.pop(captcha_id, None)
                return data
            entry = e
            return data

        self.store.update(_get)  # 顺带清理过期项
        return entry

    def set(self, captcha_id, entry):
        def _set(data):
            now = datetime.now().isoformat()
            data = {k: v for k, v in data.items()
                    if v.get('expire_time', '') > now}
            data[captcha_id] = entry
            return data
        self.store.update(_set)

    def delete(self, captcha_id):
        def _del(data):
            data.pop(captcha_id, None)
            return data
        self.store.update(_del)


class OAuthStateRepo:
    """OAuth state 持久化存储。

    原实现使用进程内存字典，多 worker / 重启即失效，
    存在 CSRF 校验不可靠问题；此处改为文件存储 + TTL。
    """

    TTL_SECONDS = 600

    def __init__(self, path):
        self.store = JsonStore(path, default={})

    def save(self, state, provider, redirect):
        import time
        def _set(data):
            now = time.time()
            data = {k: v for k, v in data.items()
                    if v.get('expire_ts', 0) > now}
            data[state] = {
                'provider': provider,
                'redirect': redirect,
                'expire_ts': now + self.TTL_SECONDS,
            }
            return data
        self.store.update(_set)

    def pop(self, state):
        """校验并一次性消费 state。"""
        import time
        found = {}

        def _pop(data):
            now = time.time()
            data = {k: v for k, v in data.items()
                    if v.get('expire_ts', 0) > now}
            entry = data.pop(state, None)
            if entry:
                found['entry'] = entry
            return data

        self.store.update(_pop)
        return found.get('entry')
