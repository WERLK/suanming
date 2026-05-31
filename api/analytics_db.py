"""
用户行为分析数据库
SQLite + WAL 模式，与业务 JSON 并行运行，互不干扰
"""
import sqlite3
import os
import time
import json
from datetime import datetime, timedelta
from threading import Lock

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
DB_PATH = os.path.join(DATA_DIR, 'analytics.db')

_write_lock = Lock()


def get_db():
    """获取数据库连接（WAL 模式，允许多读一写）"""
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-8000")
    return conn


def init_db():
    """建表（幂等）"""
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS user_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            username TEXT,
            gender TEXT DEFAULT '',
            birth_year INTEGER,
            birth_month INTEGER,
            birth_day INTEGER,
            vip_level TEXT DEFAULT 'basic',
            is_new_user INTEGER DEFAULT 0,
            id_region TEXT DEFAULT '',
            is_verified INTEGER DEFAULT 0,
            snapshot_time TIMESTAMP DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_snap_user ON user_snapshots(user_id, snapshot_time);

        CREATE TABLE IF NOT EXISTS divination_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            module_name TEXT NOT NULL,
            module_id TEXT NOT NULL,
            is_logged_in INTEGER DEFAULT 0,
            client_ip TEXT DEFAULT '',
            user_agent TEXT DEFAULT '',
            request_data TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_div_module ON divination_events(module_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_div_user ON divination_events(user_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_div_time ON divination_events(created_at);

        CREATE TABLE IF NOT EXISTS session_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            event_type TEXT NOT NULL,
            page TEXT DEFAULT '',
            referrer TEXT DEFAULT '',
            client_ip TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_sess_user ON session_events(user_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_sess_type ON session_events(event_type, created_at);

        CREATE TABLE IF NOT EXISTS vip_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            detail TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_vip_user ON vip_events(user_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_vip_type ON vip_events(event_type, created_at);

        CREATE TABLE IF NOT EXISTS hourly_stats (
            hour TEXT NOT NULL,
            module_name TEXT NOT NULL,
            total_count INTEGER DEFAULT 0,
            logged_in_count INTEGER DEFAULT 0,
            unique_users INTEGER DEFAULT 0,
            PRIMARY KEY (hour, module_name)
        );
    """)
    conn.commit()
    conn.close()


# ==================== 写入函数 ====================

def snapshot_user(user_id, username='', gender='', birth_str='',
                  vip_level='basic', is_new=False, id_region='', is_verified=False):
    """用户快照：登录/注册/更新资料时调用"""
    try:
        birth_year = birth_month = birth_day = None
        if birth_str and len(birth_str) >= 4:
            try:
                parts = birth_str.replace('-', '/').replace('.', '/').split('/')
                if len(parts) >= 1:
                    birth_year = int(parts[0])
                if len(parts) >= 2:
                    birth_month = int(parts[1])
                if len(parts) >= 3:
                    birth_day = int(parts[2])
            except ValueError:
                pass

        with _write_lock:
            conn = get_db()
            conn.execute("""
                INSERT INTO user_snapshots (user_id, username, gender,
                    birth_year, birth_month, birth_day, vip_level, is_new_user,
                    id_region, is_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, username, gender, birth_year, birth_month, birth_day,
                  vip_level, 1 if is_new else 0, id_region or '',
                  1 if is_verified else 0))
            conn.commit()
            conn.close()
    except Exception:
        pass  # 静默失败，不影响主业务


def track_divination(user_id=None, module_name='', module_id='',
                     is_logged_in=False, client_ip='', user_agent='',
                     request_data=''):
    """记录算命事件"""
    try:
        if request_data and isinstance(request_data, dict):
            request_data = json.dumps(request_data, ensure_ascii=False,
                                      default=str)[:500]
        elif not isinstance(request_data, str):
            request_data = str(request_data)[:500]

        with _write_lock:
            conn = get_db()
            conn.execute("""
                INSERT INTO divination_events
                    (user_id, module_name, module_id, is_logged_in,
                     client_ip, user_agent, request_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id or None, module_name, module_id,
                  1 if is_logged_in else 0, client_ip or '', user_agent or '',
                  request_data or ''))
            conn.commit()
            conn.close()
    except Exception:
        pass


def track_session(user_id=None, event_type='page_view', page='',
                  referrer='', client_ip=''):
    """记录会话事件"""
    try:
        with _write_lock:
            conn = get_db()
            conn.execute("""
                INSERT INTO session_events (user_id, event_type, page, referrer, client_ip)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id or None, event_type, page or '', referrer or '', client_ip or ''))
            conn.commit()
            conn.close()
    except Exception:
        pass


def track_vip(user_id, event_type, detail=''):
    """记录 VIP 行为：ad_watch / checkin / wheel / bottom_ad"""
    try:
        with _write_lock:
            conn = get_db()
            conn.execute("""
                INSERT INTO vip_events (user_id, event_type, detail)
                VALUES (?, ?, ?)
            """, (user_id, event_type, detail or ''))
            conn.commit()
            conn.close()
    except Exception:
        pass


# ==================== 查询函数 ====================

def get_overview():
    """总览数据"""
    conn = get_db()
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    week_ago = (now - timedelta(days=7)).strftime('%Y-%m-%d')
    month_ago = (now - timedelta(days=30)).strftime('%Y-%m-%d')

    total_users = conn.execute(
        "SELECT COUNT(DISTINCT user_id) FROM user_snapshots").fetchone()[0]
    today_div = conn.execute(
        "SELECT COUNT(*) FROM divination_events WHERE date(created_at)=?", (today,)).fetchone()[0]
    week_div = conn.execute(
        "SELECT COUNT(*) FROM divination_events WHERE date(created_at)>=?", (week_ago,)).fetchone()[0]
    month_div = conn.execute(
        "SELECT COUNT(*) FROM divination_events WHERE date(created_at)>=?", (month_ago,)).fetchone()[0]
    today_users = conn.execute(
        "SELECT COUNT(DISTINCT user_id) FROM divination_events WHERE date(created_at)=? AND is_logged_in=1",
        (today,)).fetchone()[0]
    today_anon = today_div - today_users
    conn.close()
    return {
        'total_users': total_users, 'today': today_div,
        'week': week_div, 'month': month_div,
        'today_logged_in': today_users, 'today_anonymous': today_anon,
        'title': '玄机算命数据分析'
    }


def get_module_stats(days=30):
    """各模块使用排行"""
    conn = get_db()
    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    rows = conn.execute("""
        SELECT module_name, module_id, COUNT(*) as cnt,
               SUM(is_logged_in) as logged,
               COUNT(DISTINCT user_id) as unique_users
        FROM divination_events
        WHERE date(created_at) >= ?
        GROUP BY module_id
        ORDER BY cnt DESC
    """, (cutoff,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_daily_stats(days=30):
    """按天统计"""
    conn = get_db()
    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    rows = conn.execute("""
        SELECT date(created_at) as day, COUNT(*) as count
        FROM divination_events
        WHERE date(created_at) >= ?
        GROUP BY day ORDER BY day
    """, (cutoff,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_hourly_stats(days=7):
    """按小时统计"""
    conn = get_db()
    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    rows = conn.execute("""
        SELECT strftime('%H', created_at) as hour, COUNT(*) as count
        FROM divination_events
        WHERE date(created_at) >= ?
        GROUP BY hour ORDER BY hour
    """, (cutoff,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_profile_stats():
    """用户画像统计"""
    conn = get_db()
    # 性别分布（取每个用户最新快照）
    gender = conn.execute("""
        SELECT gender, COUNT(*) as cnt FROM (
            SELECT user_id, gender FROM user_snapshots
            GROUP BY user_id HAVING MAX(snapshot_time)
        ) WHERE gender != '' GROUP BY gender
    """).fetchall()

    # VIP 分布
    vip = conn.execute("""
        SELECT vip_level, COUNT(DISTINCT user_id) as cnt
        FROM user_snapshots GROUP BY vip_level
    """).fetchall()

    # 年龄段分布
    now_year = datetime.now().year
    age_groups = {'0-18': 0, '19-25': 0, '26-35': 0, '36-50': 0, '50+': 0, '未知': 0}
    ages = conn.execute("""
        SELECT birth_year FROM user_snapshots
        WHERE birth_year IS NOT NULL AND birth_year > 1900
        GROUP BY user_id
    """).fetchall()
    for r in ages:
        age = now_year - r[0]
        if age <= 18: age_groups['0-18'] += 1
        elif age <= 25: age_groups['19-25'] += 1
        elif age <= 35: age_groups['26-35'] += 1
        elif age <= 50: age_groups['36-50'] += 1
        else: age_groups['50+'] += 1
    # 未知
    unknown = conn.execute(
        "SELECT COUNT(DISTINCT user_id) FROM user_snapshots WHERE birth_year IS NULL OR birth_year < 1900"
    ).fetchone()[0]
    age_groups['未知'] = unknown

    conn.close()
    return {
        'gender': [dict(r) for r in gender],
        'vip': [dict(r) for r in vip],
        'age': [{'group': k, 'count': v} for k, v in age_groups.items()]
    }


def get_vip_stats(days=30):
    """VIP 行为统计"""
    conn = get_db()
    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    rows = conn.execute("""
        SELECT event_type, COUNT(*) as cnt, COUNT(DISTINCT user_id) as users
        FROM vip_events
        WHERE date(created_at) >= ?
        GROUP BY event_type ORDER BY cnt DESC
    """, (cutoff,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_page_stats(days=7):
    """页面访问排行"""
    conn = get_db()
    cutoff = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    rows = conn.execute("""
        SELECT page, COUNT(*) as cnt
        FROM session_events
        WHERE event_type='page_view' AND date(created_at) >= ?
        GROUP BY page ORDER BY cnt DESC LIMIT 20
    """, (cutoff,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_region_stats():
    """地区分布统计（从用户快照）"""
    conn = get_db()
    rows = conn.execute("""
        SELECT id_region as region, COUNT(DISTINCT user_id) as users
        FROM user_snapshots
        WHERE id_region != ''
        GROUP BY id_region ORDER BY users DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_verified_count():
    """已认证用户数"""
    conn = get_db()
    total = conn.execute(
        "SELECT COUNT(DISTINCT user_id) FROM user_snapshots").fetchone()[0]
    verified = conn.execute(
        "SELECT COUNT(DISTINCT user_id) FROM user_snapshots WHERE is_verified=1").fetchone()[0]
    conn.close()
    return {'total': total, 'verified': verified}


def aggregate_hourly():
    """聚合小时统计（可定时调用）"""
    try:
        with _write_lock:
            conn = get_db()
            now = datetime.now()
            hour_key = now.strftime('%Y-%m-%d %H:00')
            conn.execute("""
                INSERT OR REPLACE INTO hourly_stats (hour, module_name, total_count, logged_in_count, unique_users)
                SELECT ? as hour, module_name,
                       COUNT(*) as total_count,
                       SUM(is_logged_in) as logged_in_count,
                       COUNT(DISTINCT user_id) as unique_users
                FROM divination_events
                WHERE strftime('%Y-%m-%d %H:00', created_at) = ?
                GROUP BY module_name
            """, (hour_key, hour_key))
            conn.commit()
            conn.close()
    except Exception:
        pass


# 初始化（模块加载时运行）
try:
    init_db()
    print(f"[分析] SQLite 数据库已初始化: {DB_PATH}")
except Exception as e:
    print(f"[分析] 数据库初始化失败: {e}")
