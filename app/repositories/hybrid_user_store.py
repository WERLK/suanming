"""
并存式用户存储：JSON（存量老用户） + SQLite（新用户）。

设计动机：
    历史版本将用户存在 data/users.json（JsonStore/UserRepo）。
    现需"建一个数据库存用户名密码"，要求：
      - 存量老用户继续留在 users.json，不迁移；
      - 新注册用户写入 SQLite（data/users.db）；
      - 注册/登录/资料/VIP 等业务代码零改动（它们只依赖 load_users/save_users）。

方案：
    HybridUserRepo 同时持有 json 用户表 + sqlite 用户表，对外暴露与
    原 UserRepo 完全一致的接口（all/save/find/find_by_login/add/mutate）。
      - all():           返回 JSON用户 + SQLite用户 的合并列表；
      - save(users):     按每条记录的归属标记(_src)拆回两个存储，
                         JSON 部分只写 JSON、SQLite 部分只写 SQLite，
                         新用户(两库都不存在的 id)默认写入 SQLite。
      - find/find_by_login: 在合并列表上查找。
      - add(user):       追加，默认归属 SQLite。
      - mutate(user_id): 按 id 精确定位并原地修改（自动路由回原库）。

归属标记 _src：
    仅在内存中附加，用于 save() 拆分时路由；绝不写入任何磁盘存储。
    _src 取值: 'json' | 'sqlite' | 'new'(两库均无, 新注册)
"""
import json
import os
import sqlite3
import threading

from . import JsonStore  # 复用带文件锁的 JSON 实现

# SQLite users 表字段（与 scripts/migrate_json_to_sqlite.py 的 schema 保持一致）
_SQLITE_COLUMNS = [
    'id', 'username', 'nickname', 'password', 'email', 'phone',
    'avatar', 'avatar_type', 'avatar_preset', 'birthday', 'gender',
    'create_time', 'last_login', 'status', 'vip_level', 'vip_expire',
]
# 上述之外的自定义字段统一进 extra（JSON 文本）
_KNOWN = set(_SQLITE_COLUMNS)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            TEXT PRIMARY KEY,
    username      TEXT UNIQUE NOT NULL,
    nickname      TEXT DEFAULT '',
    password      TEXT NOT NULL,
    email         TEXT DEFAULT '',
    phone         TEXT DEFAULT '',
    avatar        TEXT DEFAULT '',
    avatar_type   TEXT DEFAULT 'emoji',
    avatar_preset TEXT DEFAULT '',
    birthday      TEXT DEFAULT '',
    gender        TEXT DEFAULT '',
    create_time   TEXT,
    last_login    TEXT,
    status        TEXT DEFAULT 'active',
    vip_level     TEXT DEFAULT 'free',
    vip_expire    TEXT,
    extra         TEXT DEFAULT '{}'
)
"""


def _row_to_user(row):
    """SQLite 行 -> 用户 dict（展开 extra 中的自定义字段）。"""
    if row is None:
        return None
    col_names = ['id', 'username', 'nickname', 'password', 'email', 'phone',
                 'avatar', 'avatar_type', 'avatar_preset', 'birthday', 'gender',
                 'create_time', 'last_login', 'status', 'vip_level', 'vip_expire']
    user = dict(zip(col_names, row[:16]))
    extra_raw = row[16] if len(row) > 16 else '{}'
    try:
        extra = json.loads(extra_raw or '{}')
    except (json.JSONDecodeError, TypeError):
        extra = {}
    if isinstance(extra, dict):
        user.update(extra)
    # 移除 SQLite 特有/内部键
    for k in ('_src', 'extra'):
        user.pop(k, None)
    return user


def _user_to_row(user):
    """用户 dict -> SQLite 行（自定义字段压入 extra）。"""
    u = dict(user)
    u.pop('_src', None)
    u.pop('extra', None)
    known_vals = [u.get(c, '' if c not in ('id', 'username', 'password') else None)
                  for c in _SQLITE_COLUMNS]
    # password 不能为空
    known_vals[3] = known_vals[3] if known_vals[3] else ''
    extra = {k: v for k, v in u.items() if k not in _KNOWN}
    return tuple(known_vals) + (json.dumps(extra, ensure_ascii=False),)


class SqliteUserTable:
    """SQLite users 表封装（带简单线程锁）。"""

    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._lock = threading.Lock()
        self._ensure_schema()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_schema(self):
        with self._lock:
            conn = self._connect()
            try:
                conn.execute(_SCHEMA)
                conn.commit()
            finally:
                conn.close()

    def load_all(self):
        """返回所有用户 list[dict]。"""
        with self._lock:
            conn = self._connect()
            try:
                rows = conn.execute('SELECT * FROM users').fetchall()
                return [_row_to_user(r) for r in rows]
            finally:
                conn.close()

    def ids(self):
        with self._lock:
            conn = self._connect()
            try:
                return {r['id'] for r in conn.execute('SELECT id FROM users')}
            finally:
                conn.close()

    def usernames(self):
        with self._lock:
            conn = self._connect()
            try:
                return {r['username'] for r in conn.execute('SELECT username FROM users')}
            finally:
                conn.close()

    def replace_all(self, users):
        """整表替换（仅用于来自 SQLite 归属的用户集合）。"""
        with self._lock:
            conn = self._connect()
            try:
                conn.execute('DELETE FROM users')
                for u in users:
                    conn.execute(
                        'INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        _user_to_row(u))
                conn.commit()
            finally:
                conn.close()

    def upsert(self, user):
        with self._lock:
            conn = self._connect()
            try:
                conn.execute(
                    'INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    _user_to_row(user))
                conn.commit()
            finally:
                conn.close()

    def update_by_id(self, user_id, user):
        with self._lock:
            conn = self._connect()
            try:
                conn.execute(
                    'UPDATE users SET username=?,nickname=?,password=?,email=?,phone=?,'
                    'avatar=?,avatar_type=?,avatar_preset=?,birthday=?,gender=?,'
                    'create_time=?,last_login=?,status=?,vip_level=?,vip_expire=?,extra=? '
                    'WHERE id=?',
                    tuple(_user_to_row(user))[1:] + (user_id,))
                conn.commit()
            finally:
                conn.close()

    def delete(self, user_id):
        with self._lock:
            conn = self._connect()
            try:
                conn.execute('DELETE FROM users WHERE id=?', (user_id,))
                conn.commit()
            finally:
                conn.close()


class HybridUserRepo:
    """JSON(存量) + SQLite(新) 并存用户仓储，接口与 UserRepo 一致。"""

    def __init__(self, json_path, sqlite_path):
        self.json_store = JsonStore(json_path, default=[])
        self.sqlite = SqliteUserTable(sqlite_path)

    # ---------- 内部：归属路由 ----------

    def _source_of(self, user_id):
        """返回 user_id 所属存储: 'json' | 'sqlite' | 'new'"""
        if any(u.get('id') == user_id for u in self.json_store.load()):
            return 'json'
        if user_id in self.sqlite.ids():
            return 'sqlite'
        return 'new'

    def _annotate(self, users):
        """内存附加 _src 归属标记（不落盘）。"""
        for u in users:
            u['_src'] = self._source_of(u.get('id'))
        return users

    # ---------- 对外 API（与 UserRepo 一致） ----------

    def all(self):
        """合并列表：JSON 存量用户 + SQLite 新用户。"""
        json_users = self.json_store.load()
        sqlite_users = self.sqlite.load_all()
        merged = json_users + sqlite_users
        return self._annotate(merged)

    def save(self, users):
        """按 _src 拆回两存储；新用户(_src='new')写入 SQLite。

        注意：业务代码传入的是"合并后整表"。为不互相覆盖，
        这里只把标记为 json 的用户写回 JSON、标记为 sqlite 的写回 SQLite，
        _src='new'（全新用户）并入 SQLite。
        """
        # 深拷贝，避免污染调用方对象上的 _src
        copies = [dict(u) for u in users]

        json_part = [u for u in copies if u.get('_src') == 'json']
        # 归属 SQLite：来自 sqlite 的用户、全新用户('new')、以及
        # 业务代码新建时未带 _src 标记的用户(None) —— 一律视为新用户归入 SQLite。
        sqlite_part = [u for u in copies
                       if u.get('_src') in ('sqlite', 'new', None)]

        # 清理标记再落盘
        for u in json_part:
            u.pop('_src', None)
        for u in sqlite_part:
            u.pop('_src', None)

        if json_part:
            # JSON：仅覆盖属于 json 的存量用户（保留 SQLite 用户在 json 中不存在）
            old_json = self.json_store.load()
            old_ids = {u['id'] for u in old_json}
            merged_json = []
            for old in old_json:
                upd = next((n for n in json_part if n.get('id') == old.get('id')), None)
                merged_json.append(upd if upd is not None else old)
            # 追加任何原本不在 json 里、但带 json 标记的用户（理论上无）
            have = {u['id'] for u in merged_json}
            for n in json_part:
                if n.get('id') not in have:
                    merged_json.append(n)
            self.json_store.save(merged_json)

        if sqlite_part:
            # SQLite：整表替换为该归属用户集合（不存在并发源数据问题）
            self.sqlite.replace_all(sqlite_part)

    def find(self, **filters):
        for u in self.all():
            if all(u.get(k) == v for k, v in filters.items()):
                return u
        return None

    def find_by_login(self, login):
        for u in self.all():
            if login in (u.get('username'), u.get('email'), u.get('phone')):
                return u
        return None

    def add(self, user):
        """追加一个新用户（默认归属 SQLite）。"""
        user = dict(user)
        user.pop('_src', None)
        self.sqlite.upsert(user)

    def mutate(self, user_id, fn):
        """定位用户并原地修改（按 id 路由回原库），返回更新后的用户或 None。"""
        found = {'user': None}
        src = self._source_of(user_id)

        if src == 'json':
            def _mutate(users):
                for u in users:
                    if u.get('id') == user_id:
                        fn(u)
                        found['user'] = dict(u)
                        return users
                return users
            self.json_store.update(_mutate)
        else:  # sqlite 或 new
            # 读取该用户做修改
            target = None
            for u in self.sqlite.load_all():
                if u.get('id') == user_id:
                    target = dict(u)
                    break
            if target is not None:
                fn(target)
                found['user'] = dict(target)
                self.sqlite.update_by_id(user_id, target)
            else:
                # 全新：仍需有该对象才能 mutate，此处回 None
                found['user'] = None

        return found.get('user')


# 兼容引用：导出原名，避免破坏现有 import
UserRepo = HybridUserRepo
