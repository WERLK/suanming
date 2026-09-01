"""
可选迁移工具：JSON 文件存储 → SQLite（users.json 为例）。

背景：当前架构通过 Repository 层（app/repositories/）隔离存储实现，
JSON 存储可继续使用（数据路径与旧版完全兼容，零迁移成本）。
当用户量增长、需要事务/并发查询时，运行本脚本导入 SQLite，
再把 UserRepo 替换为 SQLite 实现即可（业务代码零改动）。

用法：
    python scripts/migrate_json_to_sqlite.py            # 迁移并校验
    python scripts/migrate_json_to_sqlite.py --dry-run  # 只检查不写入
"""
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'users.json')
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'users.db')


def load_users():
    if not os.path.exists(USERS_FILE):
        print(f'[错误] 未找到 {USERS_FILE}')
        sys.exit(1)
    with open(USERS_FILE, encoding='utf-8') as f:
        return json.load(f)


def migrate(dry_run=False):
    users = load_users()
    print(f'[读取] {len(users)} 个用户')

    if dry_run:
        # 数据体检：字段完整性
        required = ('id', 'username', 'password', 'create_time')
        problems = []
        for i, u in enumerate(users):
            for k in required:
                if k not in u:
                    problems.append(f'用户#{i}({u.get("username", "?")}) 缺字段 {k}')
        print(f'[体检] {"发现 " + str(len(problems)) + " 个问题" if problems else "字段完整 ✓"}')
        for p in problems[:10]:
            print(f'  - {p}')
        return

    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
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
    """)

    migrated = 0
    known = {'id', 'username', 'nickname', 'password', 'email', 'phone',
             'avatar', 'avatar_type', 'avatar_preset', 'birthday', 'gender',
             'create_time', 'last_login', 'status', 'vip_level', 'vip_expire'}
    for u in users:
        extra = {k: v for k, v in u.items() if k not in known}
        conn.execute(
            'INSERT OR REPLACE INTO users VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (u.get('id'), u.get('username'), u.get('nickname', ''),
             u.get('password', u.get('password_hash', '')), u.get('email', ''),
             u.get('phone', ''), u.get('avatar', ''), u.get('avatar_type', 'emoji'),
             u.get('avatar_preset', ''), u.get('birthday', ''), u.get('gender', ''),
             u.get('create_time'), u.get('last_login'), u.get('status', 'active'),
             u.get('vip_level', 'free'), u.get('vip_expire'),
             json.dumps(extra, ensure_ascii=False)))
        migrated += 1

    conn.commit()
    # 校验
    count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    conn.close()
    print(f'[写入] {migrated} 条 → {DB_FILE}')
    print(f'[校验] SQLite 中 {count} 个用户 {"✓ 一致" if count == migrated else "✗ 数量不一致！"}')
    print('')
    print('后续步骤：实现 app/repositories/user_repo_sqlite.py 并在工厂中替换，'
          '业务代码无需任何改动。')


if __name__ == '__main__':
    migrate(dry_run='--dry-run' in sys.argv)
