"""
玄机算命网 - VIP 会员服务层 (v1.8.2)
从 app.py 提取所有 VIP 业务逻辑，消除 6 处代码重复。
"""
import fcntl
import json
import os
import random
from datetime import datetime, timedelta


# ═══════════════════════════════════════════
#  常量
# ═══════════════════════════════════════════
VIP_LEVELS = {
    'free':      {'name': '免费用户', 'color': '#888',    'max_daily_ads': 3},
    'basic':     {'name': '基础会员', 'color': '#4caf50', 'max_daily_ads': 5},
    'permanent': {'name': '永久会员', 'color': '#ffd700', 'max_daily_ads': 10},
}

AD_REWARD_HOURS = 2
BONUS_AD_THRESHOLD = 20
BONUS_MIN_HOURS = 24
BONUS_MAX_HOURS = 168
WHEEL_PRIZES = [
    (25, 'vip_hours', 1, '1小时VIP会员'),
    (20, 'vip_hours', 2, '2小时VIP会员'),
    (20, 'points',    5, '5积分'),
    (15, 'points',   10, '10积分'),
    (10, 'ad_credit', 1, '免广卡x1'),
    (5,  'ad_credit', 3, '免广卡x3'),
    (3,  'vip_hours',24, '24小时VIP会员'),
    (2,  'points',   50, '50积分'),
]


# ═══════════════════════════════════════════
#  VipService — 接受 users 列表 + 文件路径
# ═══════════════════════════════════════════

class VipService:
    def __init__(self, users_file):
        self._file = users_file

    def load(self):
        with open(self._file, 'r', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                return json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    def save(self, users):
        with open(self._file, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                f.truncate()
                json.dump(users, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    # ─── 工具方法 ───

    @staticmethod
    def _today():
        return datetime.now().strftime('%Y-%m-%d')

    @staticmethod
    def _parse_dt(val):
        if not val:
            return None
        if isinstance(val, datetime):
            return val
        try:
            return datetime.fromisoformat(val)
        except (ValueError, TypeError):
            pass
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d %H:%M:%S', '%Y/%m/%d'):
            try:
                return datetime.strptime(val, fmt)
            except (ValueError, TypeError):
                pass
        return None

    @staticmethod
    def _find_index(users, user_id):
        for i, u in enumerate(users):
            if u['id'] == user_id:
                return i
        return None

    @staticmethod
    def ensure_fields(user):
        defaults = {
            'vip_level': 'free', 'vip_expire': None,
            'ad_watch_count': 0, 'ad_watch_date': '',
            'total_ad_count': 0, 'points': 0,
            'last_checkin': '', 'checkin_streak': 0,
            'wheel_spins_today': 0, 'wheel_date': '',
            'last_login_reward_date': '',
            'bottom_ad_count': 0, 'bottom_ad_date': '',
        }
        for k, v in defaults.items():
            if k not in user:
                user[k] = v
        return user

    @staticmethod
    def check_vip_expiry(user):
        vip_expire = user.get('vip_expire')
        if not vip_expire:
            return False
        expire_dt = VipService._parse_dt(vip_expire)
        if expire_dt is None:
            user['vip_expire'] = None
            return True
        if expire_dt < datetime.now():
            user['vip_level'] = 'free'
            user['vip_expire'] = None
            return True
        return False

    @staticmethod
    def compute_remaining(expire_str):
        expire_dt = VipService._parse_dt(expire_str)
        if not expire_dt:
            return None
        remaining = expire_dt - datetime.now()
        if remaining.total_seconds() <= 0:
            return None
        h = int(remaining.total_seconds() // 3600)
        m = int((remaining.total_seconds() % 3600) // 60)
        return f'{h}小时{m}分钟'

    @staticmethod
    def add_vip_hours(user, hours):
        now = datetime.now()
        cur = user.get('vip_expire')
        expire = VipService._parse_dt(cur) if cur else None
        if expire is None or expire < now:
            expire = now
        user['vip_expire'] = (expire + timedelta(hours=hours)).isoformat()
        user['vip_level'] = 'basic'

    @staticmethod
    def add_ad_count(user, count_field, date_field):
        today = VipService._today()
        if user.get(date_field, '') == today:
            user[count_field] += 1
        else:
            user[count_field] = 1
            user[date_field] = today

    @staticmethod
    def check_milestone(total_ads):
        if total_ads > 0 and total_ads % BONUS_AD_THRESHOLD == 0:
            return True, random.randint(BONUS_MIN_HOURS, BONUS_MAX_HOURS)
        return False, 0

    @staticmethod
    def apply_milestone(user, total_ads):
        triggered, bonus_hours = VipService.check_milestone(total_ads)
        if triggered:
            VipService.add_vip_hours(user, bonus_hours)
        return triggered, bonus_hours

    @staticmethod
    def add_points(user, amount):
        user['points'] = user.get('points', 0) + amount

    # ─── 端点方法 ───

    def get_status(self, user, users):
        self.ensure_fields(user)
        changed = self.check_vip_expiry(user)
        if changed:
            self.save(users)

        level = user.get('vip_level', 'free')
        info = VIP_LEVELS.get(level, VIP_LEVELS['free'])
        today = self._today()

        return {'success': True,
            'vip_level': level, 'vip_level_name': info['name'],
            'vip_expire': user.get('vip_expire'),
            'vip_remaining': self.compute_remaining(user.get('vip_expire')),
            'ad_watch_count': user.get('ad_watch_count', 0),
            'ad_watch_date': user.get('ad_watch_date', ''),
            'today_ads': user.get('ad_watch_count', 0) if user.get('ad_watch_date') == today else 0,
            'max_daily_ads': info['max_daily_ads'],
            'ad_reward_hours': AD_REWARD_HOURS,
            'total_ad_count': user.get('total_ad_count', 0),
            'bonus_threshold': BONUS_AD_THRESHOLD,
            'bottom_ad_count': user.get('bottom_ad_count', 0),
            'bottom_ad_date': user.get('bottom_ad_date', ''),
            'bottom_today_ads': user.get('bottom_ad_count', 0) if user.get('bottom_ad_date') == today else 0,
            'points': user.get('points', 0),
            'checkin_streak': user.get('checkin_streak', 0),
            'last_checkin': user.get('last_checkin', ''),
            'today_checked_in': user.get('last_checkin', '') == today,
            'wheel_spins_remaining': max(0, 5 - (user.get('wheel_spins_today', 0) if user.get('wheel_date') == today else 0)),
        }

    def watch_ad(self, user, users, ad_type='personal'):
        self.ensure_fields(user)
        idx = self._find_index(users, user['id'])
        today = self._today()
        count_field = 'ad_watch_count' if ad_type == 'personal' else 'bottom_ad_count'
        date_field = 'ad_watch_date' if ad_type == 'personal' else 'bottom_ad_date'

        today_ads = user.get(count_field, 0) if user.get(date_field) == today else 0
        max_ads = VIP_LEVELS[user.get('vip_level', 'free')]['max_daily_ads']

        if today_ads >= max_ads:
            label = '广告' if ad_type == 'personal' else '底部广告'
            return {'success': False, 'message': f'今日{label}次数已达上限（{max_ads}次），明天再来吧'}, 400

        total_ad_count = user.get('total_ad_count', 0) + 1
        users[idx]['total_ad_count'] = total_ad_count
        self.add_ad_count(users[idx], count_field, date_field)

        milestone, bonus = self.check_milestone(total_ad_count)
        reward_hours = bonus if milestone else AD_REWARD_HOURS
        self.add_vip_hours(users[idx], reward_hours)

        self.save(users)
        remaining = self.compute_remaining(users[idx]['vip_expire'])

        if milestone:
            return {'success': True, 'milestone': True,
                'message': f'🎉 里程碑奖励！累计观看{total_ad_count}次广告，获得随机{bonus//24}天VIP会员！',
                'vip_level': 'basic', 'vip_level_name': '基础会员',
                'vip_remaining': remaining, 'vip_expire': users[idx]['vip_expire'],
                'today_ads': users[idx][count_field], 'max_daily_ads': max_ads,
                'total_ad_count': total_ad_count, 'bonus_threshold': BONUS_AD_THRESHOLD,
                'bonus_hours': bonus}, 200
        else:
            next_ms = ((total_ad_count // BONUS_AD_THRESHOLD) + 1) * BONUS_AD_THRESHOLD
            return {'success': True,
                'message': f'广告观看完成！会员时长已延长{AD_REWARD_HOURS}小时（累计{total_ad_count}次，距里程碑还差{next_ms - total_ad_count}次）',
                'vip_level': 'basic', 'vip_level_name': '基础会员',
                'vip_remaining': remaining, 'vip_expire': users[idx]['vip_expire'],
                'today_ads': users[idx][count_field], 'max_daily_ads': max_ads,
                'total_ad_count': total_ad_count, 'bonus_threshold': BONUS_AD_THRESHOLD,
                'next_milestone': next_ms}, 200

    def do_checkin(self, user, users):
        self.ensure_fields(user)
        idx = self._find_index(users, user['id'])
        today = self._today()

        if user.get('last_checkin', '') == today:
            return {'success': False, 'message': '今日已签到，明天再来吧'}, 400

        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        streak = user.get('checkin_streak', 0) + 1 if user.get('last_checkin', '') == yesterday else 1

        users[idx]['checkin_streak'] = streak
        users[idx]['last_checkin'] = today

        bonus = min(streak - 1, 10) * 2
        earned = 10 + bonus
        self.add_points(users[idx], earned)
        self.add_vip_hours(users[idx], AD_REWARD_HOURS)

        self.save(users)
        return {'success': True,
            'message': f'签到成功！获得 {earned} 积分 + {AD_REWARD_HOURS}小时会员',
            'points_earned': earned, 'total_points': users[idx]['points'],
            'streak': streak, 'vip_extended': AD_REWARD_HOURS}, 200

    def do_redeem(self, user, users, redeem_type):
        self.ensure_fields(user)
        idx = self._find_index(users, user['id'])

        opts = {
            'ad1':  {'points': 20,  'label': '免广卡x1',   'action': 'add_ad'},
            'vip3': {'points': 50,  'label': '3小时会员',  'action': 'extend_vip', 'hours': 3},
            'vip24':{'points': 200, 'label': '24小时会员', 'action': 'extend_vip', 'hours': 24},
            'permanent': {'points': 500, 'label': '永久会员', 'action': 'unlock_permanent'},
        }
        if redeem_type not in opts:
            return {'success': False, 'message': '无效的兑换类型'}, 400

        opt = opts[redeem_type]
        if user.get('points', 0) < opt['points']:
            return {'success': False, 'message': f'积分不足，需要 {opt["points"]} 积分'}, 400

        users[idx]['points'] = user['points'] - opt['points']
        msg = ''

        if opt['action'] == 'add_ad':
            users[idx]['total_ad_count'] = user.get('total_ad_count', 0) + 1
            new_total = users[idx]['total_ad_count']
            msg = '兑换成功！获得免广卡x1'
            triggered, bonus = self.apply_milestone(users[idx], new_total)
            if triggered:
                msg += f'，并触发里程碑奖励：+{bonus//24}天VIP！'

        elif opt['action'] == 'extend_vip':
            self.add_vip_hours(users[idx], opt['hours'])
            msg = f'兑换成功！获得 {opt["hours"]} 小时会员'

        elif opt['action'] == 'unlock_permanent':
            users[idx]['vip_level'] = 'permanent'
            users[idx]['vip_expire'] = None
            msg = '兑换成功！已解锁永久会员'

        self.save(users)
        return {'success': True, 'message': msg,
            'remaining_points': users[idx]['points'],
            'vip_level': users[idx]['vip_level']}, 200

    def do_wheel(self, user, users):
        self.ensure_fields(user)
        idx = self._find_index(users, user['id'])
        today = self._today()

        spins = user.get('wheel_spins_today', 0) if user.get('wheel_date', '') == today else 0
        if spins >= 5:
            return {'success': False, 'message': '今日转盘次数已用完（5次）'}, 400

        if user.get('wheel_date', '') == today:
            users[idx]['wheel_spins_today'] = spins + 1
        else:
            users[idx]['wheel_spins_today'] = 1
            users[idx]['wheel_date'] = today

        roll = random.random() * 100
        cumulative = 0
        prize_type = prize_value = prize_name = None
        prize_index = 0
        for i, (pct, ptype, pval, pname) in enumerate(WHEEL_PRIZES):
            cumulative += pct
            if roll < cumulative:
                prize_type, prize_value, prize_name, prize_index = ptype, pval, pname, i
                break

        if prize_type == 'points':
            self.add_points(users[idx], prize_value)
        elif prize_type == 'vip_hours':
            self.add_vip_hours(users[idx], prize_value)
        elif prize_type == 'ad_credit':
            users[idx]['total_ad_count'] = user.get('total_ad_count', 0) + prize_value
            self.apply_milestone(users[idx], users[idx]['total_ad_count'])

        self.save(users)

        remaining = max(0, 5 - users[idx]['wheel_spins_today'])
        return {'success': True,
            'message': f'🎉 恭喜获得 {prize_name}！',
            'prize_type': prize_type, 'prize_value': prize_value,
            'prize_name': prize_name, 'prize_index': prize_index,
            'remaining_spins': remaining,
            'total_points': users[idx].get('points', 0),
            'vip_level': users[idx]['vip_level']}, 200
