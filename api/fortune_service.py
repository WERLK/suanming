"""
算命网站后端核心服务层
包含：缓存、外部API客户端、八字排盘、生肖运势、姓名五格、合婚配对、黄历、解梦、通用分析、图片分析

优化说明：
1. 添加详细日志记录
2. 优化错误处理和降级策略
3. 改进缓存机制（添加统计功能）
4. 添加性能监控
"""

import hashlib
import json
import math
import random
import time
from datetime import datetime, timedelta
from functools import wraps

import requests

# 简单日志记录函数
def log_info(msg):
    """信息日志"""
    print(f"[INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}")

def log_error(msg):
    """错误日志"""
    print(f"[ERROR] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}")

def log_debug(msg):
    """调试日志"""
    print(f"[DEBUG] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}")

def log_warning(msg):
    """警告日志"""
    print(f"[WARNING] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}")

# ============================================================
# 1. 缓存层 FortuneCache
# ============================================================

class FortuneCache:
    """内存字典缓存，支持 TTL 和统计"""

    def __init__(self):
        self._cache = {}
        self._stats = {'hits': 0, 'misses': 0, 'sets': 0, 'deletes': 0}

    def get(self, key):
        """返回缓存值或 None，并记录命中率"""
        entry = self._cache.get(key)
        if entry is None:
            self._stats['misses'] += 1
            log_debug(f"缓存未命中: {key}")
            return None
        if time.time() > entry['expire']:
            del self._cache[key]
            self._stats['misses'] += 1
            self._stats['deletes'] += 1
            log_debug(f"缓存已过期: {key}")
            return None
        self._stats['hits'] += 1
        log_debug(f"缓存命中: {key}")
        return entry['value']

    def set(self, key, value, ttl=3600):
        """设置缓存，默认 TTL 1小时"""
        self._cache[key] = {
            'value': value,
            'expire': time.time() + ttl
        }
        self._stats['sets'] += 1
        log_debug(f"缓存设置: {key} (TTL={ttl}s)")

    def clear_expired(self):
        """清理过期缓存"""
        now = time.time()
        expired_keys = [k for k, v in self._cache.items() if now > v['expire']]
        for k in expired_keys:
            del self._cache[k]
            self._stats['deletes'] += 1
        if expired_keys:
            log_info(f"清理了 {len(expired_keys)} 个过期缓存")

    def get_stats(self):
        """返回缓存统计信息"""
        total = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total * 100) if total > 0 else 0
        return {
            'size': len(self._cache),
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'hit_rate': f"{hit_rate:.1f}%",
            'sets': self._stats['sets'],
            'deletes': self._stats['deletes']
        }


# ============================================================
# 2. 外部API客户端 HoroscopeAPIClient
# ============================================================

class HoroscopeAPIClient:
    """星座运势 API 客户端（带重试机制和降级）"""

    BASE_URL = "https://freehoroscopeapi.com/api/v1"
    TIMEOUT = 5
    MAX_RETRIES = 2

    @classmethod
    def _request(cls, path, params=None):
        """发起HTTP请求，带重试机制"""
        for attempt in range(cls.MAX_RETRIES + 1):
            try:
                log_debug(f"API请求: {cls.BASE_URL}{path} (尝试 {attempt + 1})")
                resp = requests.get(
                    f"{cls.BASE_URL}{path}",
                    params=params,
                    timeout=cls.TIMEOUT
                )
                resp.raise_for_status()
                data = resp.json()
                log_info(f"API请求成功: {path}")
                return data
            except requests.exceptions.Timeout:
                log_error(f"API请求超时: {path} (尝试 {attempt + 1})")
                if attempt < cls.MAX_RETRIES:
                    time.sleep(1)  # 等待1秒后重试
                else:
                    return None
            except requests.exceptions.RequestException as e:
                log_error(f"API请求失败: {path} - {str(e)}")
                if attempt < cls.MAX_RETRIES:
                    time.sleep(1)
                else:
                    return None
            except Exception as e:
                log_error(f"未知错误: {path} - {str(e)}")
                return None
        return None

    @classmethod
    def get_daily(cls, sign):
        """GET /get-horoscope/daily?sign=aries"""
        return cls._request("/get-horoscope/daily", {"sign": sign})

    @classmethod
    def get_weekly(cls, sign):
        """GET /get-horoscope/weekly?sign=scorpio"""
        return cls._request("/get-horoscope/weekly", {"sign": sign})

    @classmethod
    def get_monthly(cls, sign):
        """GET /get-horoscope/monthly?sign=scorpio"""
        return cls._request("/get-horoscope/monthly", {"sign": sign})


# ============================================================
# 3. 外部API客户端 TarotAPIClient
# ============================================================

class TarotAPIClient:
    """塔罗牌 API 客户端"""

    BASE_URL = "https://freehoroscopeapi.com/api/v1"
    TIMEOUT = 5

    @classmethod
    def _request(cls, path, params=None):
        try:
            resp = requests.get(
                f"{cls.BASE_URL}{path}",
                params=params,
                timeout=cls.TIMEOUT
            )
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    @classmethod
    def get_all_cards(cls):
        """GET /tarot/cards"""
        return cls._request("/tarot/cards")

    @classmethod
    def get_major_cards(cls):
        """GET /tarot/cards/major"""
        return cls._request("/tarot/cards/major")

    @classmethod
    def get_minor_cards(cls):
        """GET /tarot/cards/minor"""
        return cls._request("/tarot/cards/minor")

    @classmethod
    def draw_random(cls, n=3):
        """GET /tarot/cards/random?n=3"""
        return cls._request("/tarot/cards/random", {"n": n})


# ============================================================
# 4. 八字排盘算法 BaziCalculator
# ============================================================

class BaziCalculator:
    """八字排盘核心算法"""

    # --- 基础数据 ---
    TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

    WUXING_MAP = {
        '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土', '己': '土',
        '庚': '金', '辛': '金', '壬': '水', '癸': '水',
        '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
        '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'
    }

    SHENGXIAO = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']

    # 藏干
    DIZHI_CANGGAN = {
        '子': ['癸'], '丑': ['己', '癸', '辛'], '寅': ['甲', '丙', '戊'],
        '卯': ['乙'], '辰': ['戊', '乙', '癸'], '巳': ['丙', '庚', '戊'],
        '午': ['丁', '己'], '未': ['己', '丁', '乙'], '申': ['庚', '壬', '戊'],
        '酉': ['辛'], '戌': ['戊', '辛', '丁'], '亥': ['壬', '甲']
    }

    # 纳音六十甲子（完整60条）
    NAYIN_MAP = {
        '甲子': '海中金', '乙丑': '海中金', '丙寅': '炉中火', '丁卯': '炉中火',
        '戊辰': '大林木', '己巳': '大林木', '庚午': '路旁土', '辛未': '路旁土',
        '壬申': '剑锋金', '癸酉': '剑锋金', '甲戌': '山头火', '乙亥': '山头火',
        '丙子': '涧下水', '丁丑': '涧下水', '戊寅': '城头土', '己卯': '城头土',
        '庚辰': '白蜡金', '辛巳': '白蜡金', '壬午': '杨柳木', '癸未': '杨柳木',
        '甲申': '泉中水', '乙酉': '泉中水', '丙戌': '屋上土', '丁亥': '屋上土',
        '戊子': '霹雳火', '己丑': '霹雳火', '庚寅': '松柏木', '辛卯': '松柏木',
        '壬辰': '长流水', '癸巳': '长流水', '甲午': '沙中金', '乙未': '沙中金',
        '丙申': '山下火', '丁酉': '山下火', '戊戌': '平地木', '己亥': '平地木',
        '庚子': '壁上土', '辛丑': '壁上土', '壬寅': '金箔金', '癸卯': '金箔金',
        '甲辰': '覆灯火', '乙巳': '覆灯火', '丙午': '天河水', '丁未': '天河水',
        '戊申': '大驿土', '己酉': '大驿土', '庚戌': '钗钏金', '辛亥': '钗钏金',
        '壬子': '桑柘木', '癸丑': '桑柘木', '甲寅': '大溪水', '乙卯': '大溪水',
        '丙辰': '沙中土', '丁巳': '沙中土', '戊午': '天上火', '己未': '天上火',
        '庚申': '石榴木', '辛酉': '石榴木', '壬戌': '大海水', '癸亥': '大海水'
    }

    # 长生十二宫（完整，所有十天干）
    CHANGSHENG_MAP = {
        '甲': {'亥': '长生', '子': '沐浴', '丑': '冠带', '寅': '临官', '卯': '帝旺',
               '辰': '衰', '巳': '病', '午': '死', '未': '墓', '申': '绝', '酉': '胎', '戌': '养'},
        '乙': {'午': '长生', '巳': '沐浴', '辰': '冠带', '卯': '临官', '寅': '帝旺',
               '丑': '衰', '子': '病', '亥': '死', '戌': '墓', '酉': '绝', '申': '胎', '未': '养'},
        '丙': {'寅': '长生', '卯': '沐浴', '辰': '冠带', '巳': '临官', '午': '帝旺',
               '未': '衰', '申': '病', '酉': '死', '戌': '墓', '亥': '绝', '子': '胎', '丑': '养'},
        '丁': {'酉': '长生', '申': '沐浴', '未': '冠带', '午': '临官', '巳': '帝旺',
               '辰': '衰', '卯': '病', '寅': '死', '丑': '墓', '子': '绝', '亥': '胎', '戌': '养'},
        '戊': {'寅': '长生', '卯': '沐浴', '辰': '冠带', '巳': '临官', '午': '帝旺',
               '未': '衰', '申': '病', '酉': '死', '戌': '墓', '亥': '绝', '子': '胎', '丑': '养'},
        '己': {'酉': '长生', '申': '沐浴', '未': '冠带', '午': '临官', '巳': '帝旺',
               '辰': '衰', '卯': '病', '寅': '死', '丑': '墓', '子': '绝', '亥': '胎', '戌': '养'},
        '庚': {'巳': '长生', '午': '沐浴', '未': '冠带', '申': '临官', '酉': '帝旺',
               '戌': '衰', '亥': '病', '子': '死', '丑': '墓', '寅': '绝', '卯': '胎', '辰': '养'},
        '辛': {'子': '长生', '亥': '沐浴', '戌': '冠带', '酉': '临官', '申': '帝旺',
               '未': '衰', '午': '病', '巳': '死', '辰': '墓', '卯': '绝', '寅': '胎', '丑': '养'},
        '壬': {'申': '长生', '酉': '沐浴', '戌': '冠带', '亥': '临官', '子': '帝旺',
               '丑': '衰', '寅': '病', '卯': '死', '辰': '墓', '巳': '绝', '午': '胎', '未': '养'},
        '癸': {'卯': '长生', '寅': '沐浴', '丑': '冠带', '子': '临官', '亥': '帝旺',
               '戌': '衰', '酉': '病', '申': '死', '未': '墓', '午': '绝', '巳': '胎', '辰': '养'}
    }

    # 十神关系表
    SHISHEN_TABLE = {
        ('木', '木'): '比肩', ('木', '火'): '食神', ('木', '土'): '偏财',
        ('木', '金'): '七杀', ('木', '水'): '正印',
        ('火', '火'): '比肩', ('火', '土'): '食神', ('火', '金'): '偏财',
        ('火', '水'): '七杀', ('火', '木'): '正印',
        ('土', '土'): '比肩', ('土', '金'): '食神', ('土', '水'): '偏财',
        ('土', '木'): '七杀', ('土', '火'): '正印',
        ('金', '金'): '比肩', ('金', '水'): '食神', ('金', '木'): '偏财',
        ('金', '火'): '七杀', ('金', '土'): '正印',
        ('水', '水'): '比肩', ('水', '木'): '食神', ('水', '火'): '偏财',
        ('水', '土'): '七杀', ('水', '金'): '正印',
    }

    # 阴阳区分：同阴阳为偏，异阴阳为正
    YINYANG_SHISHEN = {
        ('木', '木'): '比肩', ('木', '火'): '食神', ('木', '土'): '偏财',
        ('木', '金'): '偏官', ('木', '水'): '偏印',
        ('火', '火'): '比肩', ('火', '土'): '食神', ('火', '金'): '偏财',
        ('火', '水'): '偏官', ('火', '木'): '偏印',
        ('土', '土'): '比肩', ('土', '金'): '食神', ('土', '水'): '偏财',
        ('土', '木'): '偏官', ('土', '火'): '偏印',
        ('金', '金'): '比肩', ('金', '水'): '食神', ('金', '木'): '偏财',
        ('金', '火'): '偏官', ('金', '土'): '偏印',
        ('水', '水'): '比肩', ('水', '木'): '食神', ('水', '火'): '偏财',
        ('水', '土'): '偏官', ('水', '金'): '偏印',
    }

    # 五行相生相克
    WUXING_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
    WUXING_KE = {'木': '土', '火': '金', '土': '水', '金': '木', '水': '火'}

    # 星座日期范围
    CONSTELLATIONS = [
        ('摩羯座', (1, 20), (2, 18)), ('水瓶座', (2, 19), (3, 20)),
        ('双鱼座', (3, 21), (4, 19)), ('白羊座', (4, 20), (5, 20)),
        ('金牛座', (5, 21), (6, 21)), ('双子座', (6, 22), (7, 22)),
        ('巨蟹座', (7, 23), (8, 22)), ('狮子座', (8, 23), (9, 22)),
        ('处女座', (9, 23), (10, 23)), ('天秤座', (10, 24), (11, 22)),
        ('天蝎座', (11, 23), (12, 21)), ('射手座', (12, 22), (1, 19))
    ]

    # 神煞数据
    SHENSHA_TIANYI = {
        '甲': '丑未', '乙': '子申', '丙': '亥酉', '丁': '亥酉',
        '戊': '丑未', '己': '子申', '庚': '丑未', '辛': '午寅',
        '壬': '卯巳', '癸': '卯巳'
    }

    SHENSHA_TIANMA = {
        '寅': '申', '卯': '酉', '辰': '戌', '巳': '亥',
        '午': '子', '未': '丑', '申': '寅', '酉': '卯',
        '戌': '辰', '亥': '巳', '子': '午', '丑': '未'
    }

    SHENSHA_HUAIGAI = {
        '寅': '戌', '卯': '亥', '辰': '子', '巳': '丑',
        '午': '寅', '未': '卯', '申': '辰', '酉': '巳',
        '戌': '午', '亥': '未', '子': '申', '丑': '酉'
    }

    # 简化农历数据（1900-2100年农历信息，用数值编码）
    # 每年用一个数表示：高4位=闰月月份(0=无闰)，低12位=每月大小(1=30天,0=29天)
    LUNAR_INFO = [
        0x04bd8, 0x04ae0, 0x0a570, 0x054d5, 0x0d260, 0x0d950, 0x16554, 0x056a0, 0x09ad0, 0x055d2,
        0x04ae0, 0x0a5b6, 0x0a4d0, 0x0d250, 0x1d255, 0x0b540, 0x0d6a0, 0x0ada2, 0x095b0, 0x14977,
        0x04970, 0x0a4b0, 0x0b4b5, 0x06a50, 0x06d40, 0x1ab54, 0x02b60, 0x09570, 0x052f2, 0x04970,
        0x06566, 0x0d4a0, 0x0ea50, 0x16a95, 0x05ad0, 0x02b60, 0x186e3, 0x092e0, 0x1c8d7, 0x0c950,
        0x0d4a0, 0x1d8a6, 0x0b550, 0x056a0, 0x1a5b4, 0x025d0, 0x092d0, 0x0d2b2, 0x0a950, 0x0b557,
        0x06ca0, 0x0b550, 0x15355, 0x04da0, 0x0a5b0, 0x14573, 0x052b0, 0x0a9a8, 0x0e950, 0x06aa0,
        0x0aea6, 0x0ab50, 0x04b60, 0x0aae4, 0x0a570, 0x05260, 0x0f263, 0x0d950, 0x05b57, 0x056a0,
        0x096d0, 0x04dd5, 0x04ad0, 0x0a4d0, 0x0d4d4, 0x0d250, 0x0d558, 0x0b540, 0x0b6a0, 0x195a6,
        0x095b0, 0x049b0, 0x0a974, 0x0a4b0, 0x0b27a, 0x06a50, 0x06d40, 0x0af46, 0x0ab60, 0x09570,
        0x04af5, 0x04970, 0x064b0, 0x074a3, 0x0ea50, 0x06b58, 0x05ac0, 0x0ab60, 0x096d5, 0x092e0,
        0x0c960, 0x0d954, 0x0d4a0, 0x0da50, 0x07552, 0x056a0, 0x0abb7, 0x025d0, 0x092d0, 0x0cab5,
        0x0a950, 0x0b4a0, 0x0baa4, 0x0ad50, 0x055d9, 0x04ba0, 0x0a5b0, 0x15176, 0x052b0, 0x0a930,
        0x07954, 0x06aa0, 0x0ad50, 0x05b52, 0x04b60, 0x0a6e6, 0x0a4e0, 0x0d260, 0x0ea65, 0x0d530,
        0x05aa0, 0x076a3, 0x096d0, 0x04afb, 0x04ad0, 0x0a4d0, 0x1d0b6, 0x0d250, 0x0d520, 0x0dd45,
        0x0b5a0, 0x056d0, 0x055b2, 0x049b0, 0x0a577, 0x0a4b0, 0x0aa50, 0x1b255, 0x06d20, 0x0ada0,
        0x14b63, 0x09370, 0x049f8, 0x04970, 0x064b0, 0x168a6, 0x0ea50, 0x06aa0, 0x1a6c4, 0x0aae0,
        0x092e0, 0x0d2e3, 0x0c960, 0x0d557, 0x0d4a0, 0x0da50, 0x05d55, 0x056a0, 0x0a6d0, 0x055d4,
        0x052d0, 0x0a9b8, 0x0a950, 0x0b4a0, 0x0b6a6, 0x0ad50, 0x055a0, 0x0aba4, 0x0a5b0, 0x052b0,
        0x0b273, 0x06930, 0x07337, 0x06aa0, 0x0ad50, 0x14b55, 0x04b60, 0x0a570, 0x054e4, 0x0d160,
        0x0e968, 0x0d520, 0x0daa0, 0x16aa6, 0x056d0, 0x04ae0, 0x0a9d4, 0x0a2d0, 0x0d150, 0x0f252,
        0x0d520,
    ]

    LUNAR_MONTH_NAMES = ['正', '二', '三', '四', '五', '六', '七', '八', '九', '十', '冬', '腊']
    LUNAR_DAY_NAMES = [
        '初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
        '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
        '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十'
    ]

    # 日柱参考点：1900年1月31日 = 农历庚子年正月初一 = 甲子日
    DAY_PILLAR_REF = datetime(1900, 1, 31)
    DAY_PILLAR_REF_INDEX = 0  # 甲子 = index 0

    # 月柱天干推算（年上起月法）
    # 甲己之年丙作首，乙庚之岁戊为头，丙辛之岁寻庚上，丁壬壬寅顺水流，
    # 若问戊癸何处起，甲寅之上好追求
    MONTH_TIAN_START = {'甲': '丙', '己': '丙', '乙': '戊', '庚': '戊',
                        '丙': '庚', '辛': '庚', '丁': '壬', '壬': '壬',
                        '戊': '甲', '癸': '甲'}

    # 时柱天干推算（日上起时法）
    # 甲己还加甲，乙庚丙作初，丙辛从戊起，丁壬庚子居，戊癸何方发，壬子是真途
    HOUR_TIAN_START = {'甲': '甲', '己': '甲', '乙': '丙', '庚': '丙',
                       '丙': '戊', '辛': '戊', '丁': '庚', '壬': '庚',
                       '戊': '壬', '癸': '壬'}

    # 时辰对应地支
    SHICHEN_DIZHI = [
        (23, 1, '子'), (1, 3, '丑'), (3, 5, '寅'), (5, 7, '卯'),
        (7, 9, '辰'), (9, 11, '巳'), (11, 13, '午'), (13, 15, '未'),
        (15, 17, '申'), (17, 19, '酉'), (19, 21, '戌'), (21, 23, '亥')
    ]

    # --- 核心计算方法 ---

    @classmethod
    def _lunar_year_days(cls, year):
        """计算农历年总天数"""
        total = 0
        for i in range(12):
            if cls.LUNAR_INFO[year - 1900] & (0x10000 >> i):
                total += 30
            else:
                total += 29
        leap_month = (cls.LUNAR_INFO[year - 1900] >> 16) & 0xf
        if leap_month > 0:
            if cls.LUNAR_INFO[year - 1900] & (0x10000 >> (leap_month - 1 + 12)):
                total += 30
            else:
                total += 29
        return total

    @classmethod
    def _lunar_month_days(cls, year, month):
        """计算农历月天数"""
        if cls.LUNAR_INFO[year - 1900] & (0x10000 >> (month - 1)):
            return 30
        return 29

    @classmethod
    def _solar_to_lunar(cls, dt):
        """公历转农历"""
        try:
            base_date = datetime(1900, 1, 31)
            offset = (dt - base_date).days

            year = 1900
            days_in_year = cls._lunar_year_days(year)
            while offset >= days_in_year:
                offset -= days_in_year
                year += 1
                days_in_year = cls._lunar_year_days(year)

            leap_month = (cls.LUNAR_INFO[year - 1900] >> 16) & 0xf
            is_leap = False

            month = 1
            for i in range(1, 13):
                if leap_month > 0 and i == leap_month + 1 and not is_leap:
                    month_days = cls._lunar_month_days(year, leap_month) if cls.LUNAR_INFO[year - 1900] & (0x10000 >> (leap_month - 1 + 12)) else 29
                    if offset < month_days:
                        is_leap = True
                        month_name = f'闰{cls.LUNAR_MONTH_NAMES[leap_month - 1]}月'
                        day = offset + 1
                        return year, month, day, is_leap, month_name
                    offset -= month_days
                    is_leap = True

                month_days = cls._lunar_month_days(year, i)
                if offset < month_days:
                    month = i
                    day = offset + 1
                    month_name = f'{cls.LUNAR_MONTH_NAMES[month - 1]}月'
                    return year, month, day, is_leap, month_name
                offset -= month_days

            month = 12
            day = offset + 1
            month_name = f'{cls.LUNAR_MONTH_NAMES[11]}月'
            return year, month, day, is_leap, month_name
        except Exception:
            return dt.year, dt.month, dt.day, False, ''

    @classmethod
    def _get_year_ganzhi(cls, year):
        """年柱干支"""
        tg_idx = (year - 4) % 10
        dz_idx = (year - 4) % 12
        return cls.TIANGAN[tg_idx] + cls.DIZHI[dz_idx], tg_idx, dz_idx

    @classmethod
    def _get_month_ganzhi(cls, year, month, is_leap_month=False):
        """月柱干支（以节气划分，简化用农历月）"""
        year_tg_idx = (year - 4) % 10
        year_tian = cls.TIANGAN[year_tg_idx]
        month_tian_start = cls.MONTH_TIAN_START[year_tian]
        start_idx = cls.TIANGAN.index(month_tian_start)

        # 农历月以寅月为正月（index 0 对应寅月 = 第3个地支）
        dz_idx = (month + 1) % 12  # 正月=寅
        tg_idx = (start_idx + month - 1) % 10

        return cls.TIANGAN[tg_idx] + cls.DIZHI[dz_idx], tg_idx, dz_idx

    @classmethod
    def _get_day_ganzhi(cls, dt):
        """日柱干支：以1900-01-31甲子日为基准"""
        try:
            diff = (dt - cls.DAY_PILLAR_REF).days
            tg_idx = (cls.DAY_PILLAR_REF_INDEX + diff) % 10
            dz_idx = (cls.DAY_PILLAR_REF_INDEX + diff) % 12
            return cls.TIANGAN[tg_idx] + cls.DIZHI[dz_idx], tg_idx, dz_idx
        except Exception:
            return '甲子', 0, 0

    @classmethod
    def _get_hour_ganzhi(cls, day_tg_idx, hour):
        """时柱干支"""
        # 确定时辰地支
        dz_idx = 0
        for start, end, dz in cls.SHICHEN_DIZHI:
            if start <= hour < end or (start == 23 and (hour >= 23 or hour < 1)):
                dz_idx = cls.DIZHI.index(dz)
                break

        # 日上起时法
        day_tian = cls.TIANGAN[day_tg_idx]
        hour_tian_start = cls.HOUR_TIAN_START[day_tian]
        start_idx = cls.TIANGAN.index(hour_tian_start)
        tg_idx = (start_idx + dz_idx) % 10

        return cls.TIANGAN[tg_idx] + cls.DIZHI[dz_idx], tg_idx, dz_idx

    @classmethod
    def _calc_wuxing_stats(cls, pillars_data):
        """五行统计（含藏干）"""
        stats = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}
        for pillar in pillars_data:
            tg = pillar['tg']
            dz = pillar['dz']
            # 天干五行
            wx = cls.WUXING_MAP.get(tg, '')
            if wx:
                stats[wx] += 1
            # 地支五行
            wx = cls.WUXING_MAP.get(dz, '')
            if wx:
                stats[wx] += 1
            # 藏干五行
            for cg in cls.DIZHI_CANGGAN.get(dz, []):
                wx = cls.WUXING_MAP.get(cg, '')
                if wx:
                    stats[wx] += 0.5  # 藏干权重降低
        return stats

    @classmethod
    def _calc_shishen(cls, day_master, pillars_data):
        """十神计算"""
        day_wx = cls.WUXING_MAP.get(day_master, '')
        result = {}
        for pillar in pillars_data:
            tg = pillar['tg']
            tg_wx = cls.WUXING_MAP.get(tg, '')
            if tg == day_master:
                result[tg] = '比肩'
            elif day_wx and tg_wx:
                # 同我者比肩/劫财，我生者食神/伤官，生我者正印/偏印，
                # 我克者正财/偏财，克我者正官/七杀
                day_idx = cls.TIANGAN.index(day_master)
                tg_idx = cls.TIANGAN.index(tg)
                same_yinyang = (day_idx % 2) == (tg_idx % 2)

                if tg_wx == day_wx:
                    result[tg] = '比肩' if same_yinyang else '劫财'
                elif cls.WUXING_SHENG.get(day_wx) == tg_wx:
                    result[tg] = '食神' if same_yinyang else '伤官'
                elif cls.WUXING_SHENG.get(tg_wx) == day_wx:
                    result[tg] = '偏印' if same_yinyang else '正印'
                elif cls.WUXING_KE.get(day_wx) == tg_wx:
                    result[tg] = '偏财' if same_yinyang else '正财'
                elif cls.WUXING_KE.get(tg_wx) == day_wx:
                    result[tg] = '七杀' if same_yinyang else '正官'
                else:
                    result[tg] = '比肩'
            else:
                result[tg] = '比肩'
        return result

    @classmethod
    def _calc_nayin(cls, pillars_data):
        """纳音计算"""
        result = {}
        for pillar in pillars_data:
            ganzhi = pillar['ganzhi']
            result[ganzhi] = cls.NAYIN_MAP.get(ganzhi, '未知')
        return result

    @classmethod
    def _calc_changsheng(cls, day_master, pillars_data):
        """长生十二宫"""
        cs_map = cls.CHANGSHENG_MAP.get(day_master, {})
        result = {}
        for pillar in pillars_data:
            dz = pillar['dz']
            result[dz] = cs_map.get(dz, '未知')
        return result

    @classmethod
    def _calc_dayun(cls, month_dz_idx, year_tg_idx, gender):
        """大运计算（8步）"""
        try:
            # 阳年男/阴年女顺排，否则逆排
            is_yang_year = year_tg_idx % 2 == 0
            is_male = (gender == '男' or gender == 'male' or gender == '1')
            forward = (is_yang_year and is_male) or (not is_yang_year and not is_male)

            dayun_list = []
            step = 1 if forward else -1
            for i in range(1, 9):
                dz_idx = (month_dz_idx + i * step) % 12
                tg_idx = (year_tg_idx + 2 + i * step) % 10  # 简化推算
                gz = cls.TIANGAN[tg_idx] + cls.DIZHI[dz_idx]
                start_age = (i - 1) * 10 + 1
                dayun_list.append({
                    'order': i,
                    'ganzhi': gz,
                    'start_age': start_age,
                    'end_age': start_age + 9,
                    'wuxing': cls.WUXING_MAP.get(cls.TIANGAN[tg_idx], '')
                })
            return dayun_list
        except Exception:
            return []

    @classmethod
    def _calc_liunian(cls, current_year, count=10):
        """流年计算"""
        try:
            result = []
            for i in range(count):
                year = current_year + i
                tg_idx = (year - 4) % 10
                dz_idx = (year - 4) % 12
                gz = cls.TIANGAN[tg_idx] + cls.DIZHI[dz_idx]
                result.append({
                    'year': year,
                    'ganzhi': gz,
                    'zodiac': cls.SHENGXIAO[dz_idx],
                    'wuxing': cls.WUXING_MAP.get(cls.TIANGAN[tg_idx], '')
                })
            return result
        except Exception:
            return []

    @classmethod
    def _calc_shensha(cls, day_master, year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi):
        """神煞计算"""
        shensha = []
        try:
            # 天乙贵人
            tianyi = cls.SHENSHA_TIANYI.get(day_master, '')
            if tianyi:
                all_dz = [year_ganzhi[1], month_ganzhi[1], day_ganzhi[1], hour_ganzhi[1]]
                for dz in all_dz:
                    if dz in tianyi:
                        shensha.append({'name': '天乙贵人', 'desc': '主贵人相助，逢凶化吉'})
                        break

            # 驿马
            year_dz = year_ganzhi[1]
            tianma = cls.SHENSHA_TIANMA.get(year_dz, '')
            all_dz = [month_ganzhi[1], day_ganzhi[1], hour_ganzhi[1]]
            for dz in all_dz:
                if dz == tianma:
                    shensha.append({'name': '驿马', 'desc': '主出行、变动、奔波'})
                    break

            # 华盖
            huaigai = cls.SHENSHA_HUAIGAI.get(year_dz, '')
            for dz in all_dz:
                if dz == huaigai:
                    shensha.append({'name': '华盖', 'desc': '主聪明、孤独、宗教缘'})
                    break

            # 将星
            jiangxing_map = {'子': '子', '丑': '酉', '寅': '午', '卯': '卯',
                             '辰': '子', '巳': '酉', '午': '午', '未': '卯',
                             '申': '子', '酉': '酉', '戌': '午', '亥': '卯'}
            jiangxing = jiangxing_map.get(year_dz, '')
            for dz in all_dz:
                if dz == jiangxing:
                    shensha.append({'name': '将星', 'desc': '主权力、领导力'})
                    break

            # 羊刃
            day_tg = day_master
            yangren_map = {'甲': '卯', '乙': '辰', '丙': '午', '丁': '未',
                           '戊': '午', '己': '未', '庚': '酉', '辛': '戌',
                           '壬': '子', '癸': '丑'}
            yangren = yangren_map.get(day_tg, '')
            for dz in all_dz:
                if dz == yangren:
                    shensha.append({'name': '羊刃', 'desc': '主刚毅、果断、血光'})
                    break

            # 文昌
            wenchang_map = {'甲': '巳', '乙': '午', '丙': '申', '丁': '酉',
                            '戊': '申', '己': '酉', '庚': '亥', '辛': '子',
                            '壬': '寅', '癸': '卯'}
            wenchang = wenchang_map.get(day_tg, '')
            for dz in all_dz:
                if dz == wenchang:
                    shensha.append({'name': '文昌', 'desc': '主聪明、学业有成'})
                    break

        except Exception:
            pass
        return shensha

    @classmethod
    def _calc_xiyong(cls, day_master, wuxing_stats):
        """喜用神推算（简化：找最弱和次弱五行为喜神）"""
        try:
            day_wx = cls.WUXING_MAP.get(day_master, '')
            if not day_wx:
                return {'xi_shen': '木', 'yong_shen': '水', 'desc': '无法推算'}

            # 判断日主强弱
            day_count = wuxing_stats.get(day_wx, 0)
            sheng_wx = [k for k, v in cls.WUXING_SHENG.items() if v == day_wx]
            sheng_count = sum(wuxing_stats.get(s, 0) for s in sheng_wx)

            is_strong = day_count + sheng_count >= 3

            if is_strong:
                # 身强：喜克泄耗 - 克我者、我生者、我克者
                ke_me = [k for k, v in cls.WUXING_KE.items() if v == day_wx]
                wo_sheng = cls.WUXING_SHENG.get(day_wx, '')
                wo_ke = cls.WUXING_KE.get(day_wx, '')
                xi_shen = ke_me[0] if ke_me else wo_ke
                yong_shen = wo_sheng if wo_sheng else wo_ke
                desc = f'日主{day_master}（{day_wx}）偏强，喜{xi_shen}用{yong_shen}，宜克泄耗'
            else:
                # 身弱：喜生扶 - 生我者、同类
                sheng_me = [k for k, v in cls.WUXING_SHENG.items() if v == day_wx]
                tong_lei = day_wx
                xi_shen = sheng_me[0] if sheng_me else tong_lei
                yong_shen = tong_lei
                desc = f'日主{day_master}（{day_wx}）偏弱，喜{xi_shen}用{yong_shen}，宜生扶'

            return {'xi_shen': xi_shen, 'yong_shen': yong_shen, 'desc': desc}
        except Exception:
            return {'xi_shen': '木', 'yong_shen': '水', 'desc': '推算异常'}

    @classmethod
    def _get_constellation(cls, month, day):
        """根据公历月日获取星座"""
        for name, (s_m, s_d), (e_m, e_d) in cls.CONSTELLATIONS:
            if (month == s_m and day >= s_d) or (month == e_m and day <= e_d):
                return name
        return '摩羯座'

    @classmethod
    def calc_full(cls, name, gender, birth_date_str, birth_time, region_lon=116.4):
        """
        完整八字排盘
        :param name: 姓名
        :param gender: 性别（男/女）
        :param birth_date_str: 出生日期字符串，格式 'YYYY-MM-DD'
        :param birth_time: 出生时辰（0-23小时）
        :param region_lon: 地区经度（用于真太阳时修正）
        :return: 排盘结果字典
        """
        try:
            dt = datetime.strptime(birth_date_str, '%Y-%m-%d')
            # 支持中文时辰名和数字小时
            SHICHEN_MAP = {
                '子时': 0, '丑时': 2, '寅时': 4, '卯时': 6, '辰时': 8,
                '巳时': 10, '午时': 12, '未时': 14, '申时': 16, '酉时': 18,
                '戌时': 20, '亥时': 22, '子': 0, '丑': 2, '寅': 4, '卯': 6,
                '辰': 8, '巳': 10, '午': 12, '未': 14, '申': 16, '酉': 18,
                '戌': 20, '亥': 22
            }
            if isinstance(birth_time, str) and birth_time in SHICHEN_MAP:
                hour = SHICHEN_MAP[birth_time]
            elif isinstance(birth_time, str):
                hour = int(birth_time)
            else:
                hour = int(birth_time)

            # 真太阳时修正（基于经度）
            region_lon = float(region_lon) if region_lon else 120.0
            lon_diff = region_lon - 120  # 与东八区标准经度差
            time_offset_minutes = lon_diff * 4  # 每度4分钟
            adjusted_dt = dt + timedelta(minutes=time_offset_minutes)
            adjusted_hour = hour + int(time_offset_minutes) / 60
            if adjusted_hour >= 24:
                adjusted_dt += timedelta(days=1)
                adjusted_hour -= 24
            elif adjusted_hour < 0:
                adjusted_dt -= timedelta(days=1)
                adjusted_hour += 24

            # 农历转换
            lunar_year, lunar_month, lunar_day, is_leap, lunar_month_name = cls._solar_to_lunar(adjusted_dt)

            # 年柱
            year_ganzhi, year_tg_idx, year_dz_idx = cls._get_year_ganzhi(lunar_year)

            # 月柱
            month_ganzhi, month_tg_idx, month_dz_idx = cls._get_month_ganzhi(lunar_year, lunar_month, is_leap)

            # 日柱
            day_ganzhi, day_tg_idx, day_dz_idx = cls._get_day_ganzhi(adjusted_dt)

            # 时柱
            hour_ganzhi, hour_tg_idx, hour_dz_idx = cls._get_hour_ganzhi(day_tg_idx, int(adjusted_hour))

            # 四柱数据
            pillars = [
                {'label': '年柱', 'ganzhi': year_ganzhi, 'tg': year_ganzhi[0], 'dz': year_ganzhi[1]},
                {'label': '月柱', 'ganzhi': month_ganzhi, 'tg': month_ganzhi[0], 'dz': month_ganzhi[1]},
                {'label': '日柱', 'ganzhi': day_ganzhi, 'tg': day_ganzhi[0], 'dz': day_ganzhi[1]},
                {'label': '时柱', 'ganzhi': hour_ganzhi, 'tg': hour_ganzhi[0], 'dz': hour_ganzhi[1]},
            ]

            day_master = day_ganzhi[0]
            day_master_element = cls.WUXING_MAP.get(day_master, '')

            # 五行统计
            wuxing_stats = cls._calc_wuxing_stats(pillars)

            # 十神
            shishen = cls._calc_shishen(day_master, pillars)

            # 纳音
            nayin = cls._calc_nayin(pillars)

            # 长生十二宫
            changsheng = cls._calc_changsheng(day_master, pillars)

            # 大运
            dayun = cls._calc_dayun(month_dz_idx, year_tg_idx, gender)

            # 流年
            liunian = cls._calc_liunian(dt.year, 10)

            # 神煞
            shensha = cls._calc_shensha(day_master, year_ganzhi, month_ganzhi, day_ganzhi, hour_ganzhi)

            # 喜用神
            xiyong = cls._calc_xiyong(day_master, wuxing_stats)

            # 生肖
            zodiac = cls.SHENGXIAO[year_dz_idx]

            # 星座
            constellation = cls._get_constellation(dt.month, dt.day)

            # 农历日期字符串
            lunar_day_name = cls.LUNAR_DAY_NAMES[lunar_day - 1] if 1 <= lunar_day <= 30 else ''
            lunar_date = f'农历{lunar_year}年{cls.LUNAR_MONTH_NAMES[lunar_month - 1]}月{lunar_day_name}'

            return {
                'name': name,
                'gender': gender,
                'birth_date': birth_date_str,
                'birth_time': hour,
                'pillars': pillars,
                'day_master': day_master,
                'day_master_element': day_master_element,
                'wuxing_stats': wuxing_stats,
                'shishen': shishen,
                'nayin': nayin,
                'changsheng': changsheng,
                'dayun': dayun,
                'liunian': liunian,
                'shensha': shensha,
                'xiyong': xiyong,
                'zodiac': zodiac,
                'constellation': constellation,
                'lunar_date': lunar_date,
                'canggan': {p['dz']: cls.DIZHI_CANGGAN.get(p['dz'], []) for p in pillars}
            }
        except Exception as e:
            return {'error': str(e)}


# ============================================================
# 5. 生肖运势算法 ShengxiaoCalculator
# ============================================================

class ShengxiaoCalculator:
    """生肖运势算法"""

    TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    ZODIAC_ANIMALS = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']

    # 六合
    LIUHE_MAP = {
        '子': '丑', '丑': '子', '寅': '亥', '亥': '寅',
        '卯': '戌', '戌': '卯', '辰': '酉', '酉': '辰',
        '巳': '申', '申': '巳', '午': '未', '未': '午'
    }

    # 三合
    SANHE_GROUPS = [
        {'申', '子', '辰'},  # 水局
        {'亥', '卯', '未'},  # 木局
        {'寅', '午', '戌'},  # 火局
        {'巳', '酉', '丑'},  # 金局
    ]

    # 六冲
    CHONG_MAP = {
        '子': '午', '午': '子', '丑': '未', '未': '丑',
        '寅': '申', '申': '寅', '卯': '酉', '酉': '卯',
        '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'
    }

    # 六害
    HAI_MAP = {
        '子': '未', '未': '子', '丑': '午', '午': '丑',
        '寅': '巳', '巳': '寅', '卯': '辰', '辰': '卯',
        '申': '亥', '亥': '申', '酉': '戌', '戌': '酉'
    }

    # 生肖到地支映射
    ZODIAC_TO_DIZHI = {
        '鼠': '子', '牛': '丑', '虎': '寅', '兔': '卯',
        '龙': '辰', '蛇': '巳', '马': '午', '羊': '未',
        '猴': '申', '鸡': '酉', '狗': '戌', '猪': '亥'
    }

    DIZHI_TO_ZODIAC = {v: k for k, v in ZODIAC_TO_DIZHI.items()}

    WUXING_MAP = BaziCalculator.WUXING_MAP

    @classmethod
    def get_year_ganzhi(cls, year):
        """获取年份干支和生肖"""
        try:
            tg_idx = (year - 4) % 10
            dz_idx = (year - 4) % 12
            ganzhi = cls.TIANGAN[tg_idx] + cls.DIZHI[dz_idx]
            zodiac = cls.ZODIAC_ANIMALS[dz_idx]
            return {
                'year': year,
                'ganzhi': ganzhi,
                'tiangan': cls.TIANGAN[tg_idx],
                'dizhi': cls.DIZHI[dz_idx],
                'zodiac': zodiac,
                'wuxing': cls.WUXING_MAP.get(cls.TIANGAN[tg_idx], '')
            }
        except Exception:
            return None

    @classmethod
    def get_relation(cls, user_zodiac, year_zhi):
        """判断生肖关系"""
        try:
            user_zhi = cls.ZODIAC_TO_DIZHI.get(user_zodiac, '')
            if not user_zhi:
                return {'relation': '未知', 'desc': '无法判断'}

            relations = []

            # 六合
            liuhe = cls.LIUHE_MAP.get(user_zhi, '')
            if liuhe == year_zhi:
                relations.append({'relation': '六合', 'desc': f'您的生肖{user_zodiac}与流年地支{year_zhi}六合，主和谐、相助、贵人运'})

            # 三合
            for group in cls.SANHE_GROUPS:
                if user_zhi in group and year_zhi in group:
                    relations.append({'relation': '三合', 'desc': f'您的生肖{user_zodiac}与流年地支{year_zhi}三合，主合作、顺遂、旺运'})
                    break

            # 六冲
            chong = cls.CHONG_MAP.get(user_zhi, '')
            if chong == year_zhi:
                relations.append({'relation': '六冲', 'desc': f'您的生肖{user_zodiac}与流年地支{year_zhi}六冲，主变动、冲突、需谨慎'})

            # 六害
            hai = cls.HAI_MAP.get(user_zhi, '')
            if hai == year_zhi:
                relations.append({'relation': '六害', 'desc': f'您的生肖{user_zodiac}与流年地支{year_zhi}六害，主小人、是非、宜防备'})

            if not relations:
                relations.append({'relation': '普通', 'desc': f'您的生肖{user_zodiac}与流年地支{year_zhi}无特殊关系，运势平稳'})

            return relations[0] if len(relations) == 1 else {'relation': '复合', 'details': relations}
        except Exception:
            return {'relation': '未知', 'desc': '判断失败'}

    @classmethod
    def get_fortune(cls, zodiac, year, month=1, day=1):
        """生成生肖运势"""
        try:
            year_info = cls.get_year_ganzhi(year)
            if not year_info:
                return None

            year_zhi = year_info['dizhi']
            relation = cls.get_relation(zodiac, year_zhi)

            # 基于生肖和年份关系生成运势
            base_scores = {
                '六合': {'overall': 90, 'love': 85, 'career': 88, 'wealth': 85, 'health': 80},
                '三合': {'overall': 85, 'love': 80, 'career': 85, 'wealth': 82, 'health': 78},
                '普通': {'overall': 70, 'love': 68, 'career': 70, 'wealth': 65, 'health': 72},
                '六冲': {'overall': 55, 'love': 50, 'career': 55, 'wealth': 48, 'health': 58},
                '六害': {'overall': 50, 'love': 48, 'career': 52, 'wealth': 45, 'health': 55},
                '复合': {'overall': 65, 'love': 60, 'career': 65, 'wealth': 58, 'health': 62},
                '未知': {'overall': 65, 'love': 60, 'career': 65, 'wealth': 60, 'health': 60},
            }

            rel_type = relation.get('relation', '未知')
            scores = base_scores.get(rel_type, base_scores['普通'])

            # 加入月份和日期的微调
            seed = hash(f'{zodiac}{year}{month}{day}')
            rng = random.Random(seed)
            variation = lambda s: max(30, min(98, s + rng.randint(-8, 8)))

            adjusted_scores = {k: variation(v) for k, v in scores.items()}

            # 运势描述
            fortune_texts = {
                '六合': '今年与太岁六合，整体运势顺畅，贵人助力明显。事业上有望获得突破，财运亨通，感情和美。宜积极进取，把握机遇。',
                '三合': '今年与太岁三合，运势稳中有升。合作运佳，适合团队协作和拓展人脉。财运平稳增长，健康状况良好。',
                '普通': '今年运势平稳，无大起大落。踏实做事，稳健经营，会有不错的收获。注意保持良好的生活作息。',
                '六冲': '今年与太岁相冲，变动较多。需特别注意人际关系和健康问题。凡事谨慎为上，三思而后行。可佩戴相合生肖饰品化解。',
                '六害': '今年与太岁相害，需防小人暗算。工作中注意言行，避免口舌是非。财运方面需谨慎投资，量入为出。',
            }

            desc = fortune_texts.get(rel_type, fortune_texts['普通'])

            # 月份运势
            monthly = []
            for m in range(1, 13):
                m_seed = hash(f'{zodiac}{year}{m}')
                m_rng = random.Random(m_seed)
                monthly.append({
                    'month': m,
                    'overall': m_rng.randint(50, 95),
                    'desc': '运势平稳' if m_rng.random() > 0.3 else '需注意'
                })

            return {
                'zodiac': zodiac,
                'year': year,
                'year_ganzhi': year_info['ganzhi'],
                'relation': relation,
                'scores': adjusted_scores,
                'description': desc,
                'monthly_fortune': monthly,
                'lucky_numbers': rng.sample(range(1, 50), 6),
                'lucky_colors': rng.choice(['红色', '黄色', '蓝色', '绿色', '白色', '紫色', '金色']),
                'lucky_directions': rng.choice(['东方', '南方', '西方', '北方', '东南', '东北']),
            }
        except Exception:
            return None


# ============================================================
# 6. 姓名五格分析 XingmingCalculator
# ============================================================

class XingmingCalculator:
    """姓名五格分析"""

    # 简化Unicode笔画映射（常用汉字的笔画数）
    # 实际应用中应使用完整笔画字典，这里提供简化版本
    STROKE_MAP = {
        '一': 1, '二': 2, '三': 3, '四': 5, '五': 4, '六': 4, '七': 2, '八': 2, '九': 2, '十': 2,
        '百': 6, '千': 3, '万': 3, '大': 3, '小': 3, '天': 4, '地': 6, '人': 2, '日': 4, '月': 4,
        '金': 8, '木': 4, '水': 4, '火': 4, '土': 3, '东': 5, '南': 9, '西': 6, '北': 5,
        '春': 9, '夏': 10, '秋': 9, '冬': 5, '风': 4, '雨': 8, '雪': 11, '云': 4, '雷': 13,
        '龙': 5, '凤': 4, '虎': 8, '鹤': 15, '鹏': 13, '鹰': 18, '燕': 16, '鱼': 8,
        '明': 8, '华': 6, '国': 8, '家': 10, '安': 6, '平': 5, '福': 13, '禄': 12,
        '寿': 7, '喜': 12, '财': 7, '宝': 8, '玉': 5, '珍': 9, '珠': 10, '宝': 8,
        '文': 4, '武': 8, '德': 15, '仁': 4, '义': 3, '礼': 5, '智': 12, '信': 9,
        '美': 9, '丽': 7, '芳': 7, '兰': 5, '菊': 11, '梅': 11, '竹': 6, '松': 8,
        '海': 10, '山': 3, '江': 6, '河': 8, '湖': 12, '洋': 9, '波': 8, '涛': 10,
        '军': 6, '伟': 11, '强': 12, '刚': 10, '勇': 9, '杰': 8, '磊': 15, '鑫': 24,
        '志': 7, '建': 8, '立': 5, '成': 6, '达': 6, '发': 5, '兴': 6, '旺': 8,
        '秀': 7, '英': 8, '敏': 11, '静': 14, '洁': 10, '琳': 12, '婷': 12, '雪': 11,
        '宇': 6, '浩': 10, '然': 12, '博': 12, '涵': 11, '轩': 7, '逸': 11, '睿': 14,
        '思': 9, '梦': 11, '雅': 12, '佳': 8, '慧': 15, '欣': 8, '悦': 10, '瑶': 14,
        '子': 3, '若': 8, '如': 6, '心': 4, '意': 13, '情': 11, '爱': 10, '善': 12,
        '长': 4, '永': 5, '世': 5, '代': 5, '新': 13, '旧': 5, '好': 6, '坏': 7,
        '正': 5, '光': 6, '亮': 9, '星': 9, '辰': 7, '旭': 6, '晨': 11, '晖': 10,
    }

    # 81数理吉凶
    JIXIONG_MAP = {
        1: ('大吉', '宇宙起源，万事如意'), 2: ('凶', '动摇不安，根基不固'),
        3: ('大吉', '进取如意，智勇双全'), 4: ('凶', '万事休止，前途暗淡'),
        5: ('大吉', '福禄长寿，阴阳和合'), 6: ('大吉', '安稳余庆，天降幸运'),
        7: ('吉', '精悍刚毅，精力旺盛'), 8: ('吉', '意志坚强，功成名就'),
        9: ('凶', '穷迫逆境，吉尽凶始'), 10: ('凶', '万事终局，晦暗无光'),
        11: ('大吉', '旱苗逢雨，稳健发展'), 12: ('凶', '薄弱无力，挫折困难'),
        13: ('大吉', '智略超群，春日牡丹'), 14: ('凶', '忍得苦难，破兆浮沉'),
        15: ('大吉', '福寿圆满，富贵荣誉'), 16: ('大吉', '贵人相助，逢凶化吉'),
        17: ('吉', '刚柔兼备，突破万难'), 18: ('吉', '有志竟成，权威显达'),
        19: ('凶', '风云蔽日，病难遭难'), 20: ('凶', '非业破运，灾难重重'),
        21: ('大吉', '明月光照，独立权威'), 22: ('凶', '秋草逢霜，怀才不遇'),
        23: ('大吉', '旭日东升，壮丽壮观'), 24: ('大吉', '家门余庆，金钱丰盈'),
        25: ('大吉', '资性英敏，刚毅果断'), 26: ('凶', '变怪奇异，英雄豪杰'),
        27: ('凶', '欲望无止，自信心强'), 28: ('凶', '家亲缘薄，孤独遭难'),
        29: ('大吉', '智谋优秀，财力归集'), 30: ('凶', '非运浮沉，绝死逆境'),
        31: ('大吉', '智勇得志，心想事成'), 32: ('大吉', '宝马金鞍，侥幸多望'),
        33: ('大吉', '旭日升天，家门隆昌'), 34: ('凶', '破家亡身，见识短小'),
        35: ('大吉', '温良和顺，智能畅通'), 36: ('凶', '波澜壮阔，侠义薄弱'),
        37: ('大吉', '权威显达，吉人天相'), 38: ('凶', '磨铁成针，意志薄弱'),
        39: ('大吉', '富贵荣华，福寿绵长'), 40: ('凶', '退安享福，谨慎无忧'),
        41: ('大吉', '纯阳独秀，德望高大'), 42: ('凶', '寒蝉在柳，十艺不成'),
        43: ('凶', '散财破产，诸事不遂'), 44: ('凶', '烦闷损寿，破家亡身'),
        45: ('大吉', '顺风扬帆，新生泰和'), 46: ('凶', '浪里淘金，载宝沉舟'),
        47: ('大吉', '点铁成金，开花结果'), 48: ('大吉', '青松立鹤，智谋兼备'),
        49: ('凶', '吉凶难分，转凶为吉'), 50: ('凶', '吉凶互见，一成一败'),
        51: ('凶', '盛衰交加，浮沉不定'), 52: ('大吉', '达眼识明，先见之明'),
        53: ('凶', '忧愁困苦，内心忧愁'), 54: ('凶', '多难短命，难望成功'),
        55: ('凶', '外祥内苦，和顺不实'), 56: ('凶', '浪里行舟，历尽艰辛'),
        57: ('吉', '日照春松，寒雪青松'), 58: ('吉', '晚行遇月，先苦后甜'),
        59: ('凶', '寒蝉悲风，意志不坚'), 60: ('凶', '无谋之人，晦暗无光'),
        61: ('大吉', '名利双收，繁荣富贵'), 62: ('凶', '衰败孤独，烦闷损寿'),
        63: ('大吉', '富贵荣华，万物如意'), 64: ('凶', '见异思迁，骨肉分离'),
        65: ('大吉', '富贵至极，家运隆昌'), 66: ('凶', '岩头步马，黑暗无光'),
        67: ('大吉', '顺风通达，天赋幸运'), 68: ('大吉', '兴家立业，发明奇功'),
        69: ('凶', '坐立不安，非业穷迫'), 70: ('凶', '残破之数，惨淡经营'),
        71: ('凶', '石上金花，勤勉奋斗'), 72: ('凶', '劳苦不堪，半吉半凶'),
        73: ('吉', '无勇之人，高飞远举'), 74: ('凶', '沉沦逆境，无谋无勇'),
        75: ('凶', '退守可安，守成知足'), 76: ('凶', '倾覆离散，穷困之数'),
        77: ('吉', '家庭有缘，此数半吉'), 78: ('凶', '晚景凄清，前半生吉'),
        79: ('凶', '挽回乏力，身心疲倦'), 80: ('吉', '最吉之数，退守可安'),
        81: ('大吉', '万物回春，还原复始'),
    }

    WUXING_NUM = {1: '木', 2: '木', 3: '火', 4: '火', 5: '土', 6: '土', 7: '金', 8: '金', 9: '水', 0: '水'}

    @classmethod
    def _get_stroke(cls, char):
        """获取汉字笔画数"""
        if char in cls.STROKE_MAP:
            return cls.STROKE_MAP[char]
        # 简化回退：根据Unicode区间估算
        code = ord(char)
        if 0x4E00 <= code <= 0x9FFF:
            # CJK统一表意文字，用简化公式
            return ((code - 0x4E00) % 20) + 1
        return 1

    @classmethod
    def _num_wuxing(cls, num):
        """数理五行"""
        return cls.WUXING_NUM.get(num % 10, '木')

    @classmethod
    def _num_jixiong(cls, num):
        """数理吉凶"""
        while num > 81:
            num -= 80
        return cls.JIXIONG_MAP.get(num, ('平', '数理待查'))

    @classmethod
    def analyze(cls, name_str):
        """
        姓名五格分析
        :param name_str: 完整姓名字符串
        :return: 五格分析结果
        """
        try:
            chars = list(name_str.replace(' ', ''))
            if len(chars) < 2:
                return {'error': '姓名至少需要两个字'}

            strokes = [cls._get_stroke(c) for c in chars]
            surname_strokes = strokes[0]  # 姓氏笔画
            # 双姓处理
            if len(chars) >= 3 and strokes[0] + strokes[1] <= 15:
                # 可能是双姓
                surname_strokes = strokes[0] + strokes[1]
                name_strokes = strokes[2:]
                surname_count = 2
            else:
                name_strokes = strokes[1:]
                surname_count = 1

            total_name_strokes = sum(name_strokes)

            # 天格 = 姓笔画 + 1（单姓）或 姓总笔画（复姓）
            if surname_count == 1:
                tian_ge = surname_strokes + 1
            else:
                tian_ge = surname_strokes

            # 人格 = 姓末字笔画 + 名首字笔画
            ren_ge = strokes[surname_count - 1] + strokes[surname_count] if len(strokes) > surname_count else strokes[-1]

            # 地格 = 名首字笔画 + 名次字笔画（无次字则+1）
            if len(name_strokes) >= 2:
                di_ge = name_strokes[0] + name_strokes[1]
            elif len(name_strokes) == 1:
                di_ge = name_strokes[0] + 1
            else:
                di_ge = 2

            # 外格 = 总格 - 人格 + 1
            zong_ge = sum(strokes)
            wai_ge = zong_ge - ren_ge + 1 if zong_ge - ren_ge + 1 > 0 else 1

            grids = {
                '天格': {'num': tian_ge, 'wuxing': cls._num_wuxing(tian_ge),
                         'jixiong': cls._num_jixiong(tian_ge), 'desc': '先天运，由姓氏决定，无法改变'},
                '人格': {'num': ren_ge, 'wuxing': cls._num_wuxing(ren_ge),
                         'jixiong': cls._num_jixiong(ren_ge), 'desc': '主运，代表一生运势，最重要的格局'},
                '地格': {'num': di_ge, 'wuxing': cls._num_wuxing(di_ge),
                         'jixiong': cls._num_jixiong(di_ge), 'desc': '前运，代表36岁前的运势'},
                '外格': {'num': wai_ge, 'wuxing': cls._num_wuxing(wai_ge),
                         'jixiong': cls._num_jixiong(wai_ge), 'desc': '副运，代表社交运和外在表现'},
                '总格': {'num': zong_ge, 'wuxing': cls._num_wuxing(zong_ge),
                         'jixiong': cls._num_jixiong(zong_ge), 'desc': '后运，代表36岁后的运势'},
            }

            # 综合评分
            ji_count = sum(1 for g in grids.values() if g['jixiong'][0] in ('大吉', '吉'))
            total = len(grids)
            score = int(ji_count / total * 100)

            return {
                'name': name_str,
                'strokes': {c: s for c, s in zip(chars, strokes)},
                'grids': grids,
                'score': score,
                'summary': f'五格中{ji_count}格为吉，{"名字不错" if score >= 60 else "建议考虑更名"}'
            }
        except Exception as e:
            return {'error': str(e)}


# ============================================================
# 7. 合婚配对 HeYunCalculator
# ============================================================

class HeYunCalculator:
    """合婚配对计算"""

    @classmethod
    def match(cls, name1, birth1, name2, birth2):
        """
        基于双方八字五行匹配度计算
        :param name1: 甲方姓名
        :param birth1: 甲方出生日期 'YYYY-MM-DD'
        :param name2: 乙方姓名
        :param birth2: 乙方出生日期 'YYYY-MM-DD'
        :return: 配对结果
        """
        try:
            bazi1 = BaziCalculator.calc_full(name1, '未知', birth1, 12)
            bazi2 = BaziCalculator.calc_full(name2, '未知', birth2, 12)

            if 'error' in bazi1 or 'error' in bazi2:
                return {'error': '八字计算失败', 'score': 0}

            wx1 = bazi1.get('wuxing_stats', {})
            wx2 = bazi2.get('wuxing_stats', {})

            # 五行互补分析
            wx_types = ['金', '木', '水', '火', '土']
            complement_score = 0
            for wx in wx_types:
                v1 = wx1.get(wx, 0)
                v2 = wx2.get(wx, 0)
                # 一方弱一方强视为互补
                if (v1 < 1.5 and v2 >= 1.5) or (v2 < 1.5 and v1 >= 1.5):
                    complement_score += 15
                elif v1 >= 1.5 and v2 >= 1.5:
                    complement_score += 5

            # 日主相生相克
            dm1 = bazi1.get('day_master', '')
            dm2 = bazi2.get('day_master', '')
            dm1_wx = BaziCalculator.WUXING_MAP.get(dm1, '')
            dm2_wx = BaziCalculator.WUXING_MAP.get(dm2, '')

            relation_score = 50
            relation_desc = '无特殊关系'
            if dm1_wx and dm2_wx:
                if BaziCalculator.WUXING_SHENG.get(dm1_wx) == dm2_wx:
                    relation_score = 80
                    relation_desc = f'{dm1_wx}生{dm2_wx}，甲方旺乙方'
                elif BaziCalculator.WUXING_SHENG.get(dm2_wx) == dm1_wx:
                    relation_score = 80
                    relation_desc = f'{dm2_wx}生{dm1_wx}，乙方旺甲方'
                elif BaziCalculator.WUXING_KE.get(dm1_wx) == dm2_wx:
                    relation_score = 40
                    relation_desc = f'{dm1_wx}克{dm2_wx}，甲方克制乙方'
                elif BaziCalculator.WUXING_KE.get(dm2_wx) == dm1_wx:
                    relation_score = 40
                    relation_desc = f'{dm2_wx}克{dm1_wx}，乙方克制甲方'
                elif dm1_wx == dm2_wx:
                    relation_score = 75
                    relation_desc = f'五行同为{dm1_wx}，志同道合'

            # 生肖配对
            z1 = bazi1.get('zodiac', '')
            z2 = bazi2.get('zodiac', '')
            zhi1 = ShengxiaoCalculator.ZODIAC_TO_DIZHI.get(z1, '')
            zhi2 = ShengxiaoCalculator.ZODIAC_TO_DIZHI.get(z2, '')

            zodiac_score = 60
            zodiac_desc = '生肖普通配对'
            if ShengxiaoCalculator.LIUHE_MAP.get(zhi1) == zhi2:
                zodiac_score = 95
                zodiac_desc = f'{z1}与{z2}六合，天生一对'
            elif any(zhi1 in g and zhi2 in g for g in ShengxiaoCalculator.SANHE_GROUPS):
                zodiac_score = 85
                zodiac_desc = f'{z1}与{z2}三合，十分般配'
            elif ShengxiaoCalculator.CHONG_MAP.get(zhi1) == zhi2:
                zodiac_score = 35
                zodiac_desc = f'{z1}与{z2}相冲，需多包容'
            elif ShengxiaoCalculator.HAI_MAP.get(zhi1) == zhi2:
                zodiac_score = 40
                zodiac_desc = f'{z1}与{z2}相害，需注意沟通'

            # 姓名五格
            name1_result = XingmingCalculator.analyze(name1)
            name2_result = XingmingCalculator.analyze(name2)
            name_score1 = name1_result.get('score', 60) if 'error' not in name1_result else 60
            name_score2 = name2_result.get('score', 60) if 'error' not in name2_result else 60
            name_avg = (name_score1 + name_score2) / 2

            # 综合评分
            total_score = int(
                complement_score * 0.25 +
                relation_score * 0.25 +
                zodiac_score * 0.25 +
                name_avg * 0.25
            )
            total_score = max(10, min(99, total_score))

            # 评价
            if total_score >= 85:
                verdict = '天作之合'
            elif total_score >= 70:
                verdict = '良缘佳配'
            elif total_score >= 55:
                verdict = '尚可配对'
            elif total_score >= 40:
                verdict = '需多磨合'
            else:
                verdict = '不太相配'

            return {
                'name1': name1, 'name2': name2,
                'score': total_score,
                'verdict': verdict,
                'details': {
                    'wuxing_complement': {'score': min(complement_score, 100), 'desc': f'五行互补度{complement_score}分'},
                    'day_master_relation': {'score': relation_score, 'desc': relation_desc},
                    'zodiac_match': {'score': zodiac_score, 'desc': zodiac_desc},
                    'name_analysis': {'score': int(name_avg), 'desc': f'姓名评分{name_avg:.0f}分'}
                },
                'advice': cls._get_advice(total_score),
                'bazi1': bazi1,
                'bazi2': bazi2,
            }
        except Exception as e:
            return {'error': str(e), 'score': 0}

    @classmethod
    def _get_advice(cls, score):
        """获取配对建议"""
        if score >= 85:
            return '你们是天作之合，珍惜彼此，共同创造美好未来。多沟通、多包容，幸福会长长久久。'
        elif score >= 70:
            return '你们有很好的缘分基础，适合在一起。保持理解和信任，感情会越来越好。'
        elif score >= 55:
            return '你们有一定缘分，但需要更多磨合。学会换位思考，多站在对方角度看问题。'
        elif score >= 40:
            return '你们的配对指数偏低，但不必灰心。通过共同努力和理解，依然可以经营好关系。'
        else:
            return '你们的五行和生肖配对不太理想，但这只是参考。真心相待、互相尊重才是最重要的。'


# ============================================================
# 8. 黄历服务 HuangliService
# ============================================================

class HuangliService:
    """黄历服务"""

    TIANGAN = BaziCalculator.TIANGAN
    DIZHI = BaziCalculator.DIZHI
    WUXING_MAP = BaziCalculator.WUXING_MAP

    # 宜忌数据（天干地支组合对应）
    YI_DATA = {
        '建': ['开市', '交易', '立券', '纳财'], '除': ['祭祀', '祈福', '求嗣', '解除'],
        '满': ['祭祀', '祈福', '结婚', '开光'], '平': ['修造', '动土', '栽种', '牧养'],
        '定': ['冠笄', '结婚', '纳采', '嫁娶'], '执': ['祭祀', '捕捉', '畋猎', '纳畜'],
        '破': ['破屋', '坏垣', '求医', '治病'], '危': ['祭祀', '祈福', '安床', '入宅'],
        '成': ['结婚', '开市', '交易', '立券'], '收': ['纳财', '入库', '祭祀', '塑绘'],
        '开': ['开市', '交易', '立券', '纳财'], '闭': ['安葬', '收藏', '筑堤', '建基'],
    }

    JI_DATA = {
        '建': ['动土', '开仓', '掘井', '行丧'], '除': ['嫁娶', '出行', '移徙', '入宅'],
        '满': ['栽种', '动土', '破土', '安葬'], '平': ['诸事不宜'], 
        '定': ['诉讼', '出行', '修造', '动土'], '执': ['搬家', '出行', '开市', '嫁娶'],
        '破': ['诸事不宜'], '危': ['出行', '登高', '行船', '动土'],
        '成': ['诉讼', '安葬', '行丧', '破土'], '收': ['动土', '破土', '安葬', '行丧'],
        '开': ['安葬', '行丧', '破土', '动土'], '闭': ['开市', '交易', '嫁娶', '出行'],
    }

    # 十二值日
    ZHI_DAYS = ['建', '除', '满', '平', '定', '执', '破', '危', '成', '收', '开', '闭']

    # 节气数据（简化）
    SOLAR_TERMS = [
        '小寒', '大寒', '立春', '雨水', '惊蛰', '春分',
        '清明', '谷雨', '立夏', '小满', '芒种', '夏至',
        '小暑', '大暑', '立秋', '处暑', '白露', '秋分',
        '寒露', '霜降', '立冬', '小雪', '大雪', '冬至'
    ]

    @classmethod
    def _get_zhiri(cls, day_dz_idx, month_dz_idx):
        """获取十二值日"""
        zhiri_idx = (day_dz_idx - month_dz_idx) % 12
        return cls.ZHI_DAYS[zhiri_idx]

    @classmethod
    def get_huangli(cls, date_str):
        """
        获取黄历信息
        :param date_str: 日期字符串 'YYYY-MM-DD'
        :return: 黄历信息字典
        """
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')

            # 农历
            lunar_year, lunar_month, lunar_day, is_leap, lunar_month_name = BaziCalculator._solar_to_lunar(dt)

            # 天干地支
            year_ganzhi, _, year_dz_idx = BaziCalculator._get_year_ganzhi(lunar_year)
            month_ganzhi, _, month_dz_idx = BaziCalculator._get_month_ganzhi(lunar_year, lunar_month, is_leap)
            day_ganzhi, day_tg_idx, day_dz_idx = BaziCalculator._get_day_ganzhi(dt)

            # 十二值日
            zhiri = cls._get_zhiri(day_dz_idx, month_dz_idx)

            # 宜忌
            yi = cls.YI_DATA.get(zhiri, [])
            ji = cls.JI_DATA.get(zhiri, [])

            # 五行
            day_wuxing = cls.WUXING_MAP.get(day_ganzhi[0], '')
            dz_wuxing = cls.WUXING_MAP.get(day_ganzhi[1], '')

            # 纳音
            nayin = BaziCalculator.NAYIN_MAP.get(day_ganzhi, '未知')

            # 节气（简化：根据日期估算）
            month_day = dt.month * 100 + dt.day
            term_idx = -1
            term_ranges = [
                (106, 0), (120, 1), (204, 2), (219, 3), (306, 4), (321, 5),
                (405, 6), (420, 7), (506, 8), (521, 9), (606, 10), (621, 11),
                (707, 12), (723, 13), (807, 14), (823, 15), (908, 16), (923, 17),
                (1008, 18), (1023, 19), (1107, 20), (1122, 21), (1207, 22), (1222, 23)
            ]
            for i, (threshold, idx) in enumerate(term_ranges):
                if month_day < threshold:
                    term_idx = idx - 1 if i > 0 else 0
                    break
            current_term = cls.SOLAR_TERMS[term_idx] if term_idx >= 0 else '冬至'

            # 冲煞
            chong_map = BaziCalculator.WUXING_KE
            day_dz_wuxing = cls.WUXING_MAP.get(day_ganzhi[1], '')
            chong_dz = ShengxiaoCalculator.CHONG_MAP.get(day_ganzhi[1], '')
            chong_zodiac = ShengxiaoCalculator.DIZHI_TO_ZODIAC.get(chong_dz, '')

            # 星期
            weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
            weekday = weekdays[dt.weekday()]

            lunar_day_name = BaziCalculator.LUNAR_DAY_NAMES[lunar_day - 1] if 1 <= lunar_day <= 30 else ''

            return {
                'date': date_str,
                'weekday': weekday,
                'lunar_date': f'农历{BaziCalculator.LUNAR_MONTH_NAMES[lunar_month - 1]}月{lunar_day_name}',
                'lunar_year': lunar_year,
                'year_ganzhi': year_ganzhi,
                'month_ganzhi': month_ganzhi,
                'day_ganzhi': day_ganzhi,
                'zhiri': zhiri,
                'yi': yi,
                'ji': ji,
                'nayin': nayin,
                'wuxing': f'{day_wuxing}{dz_wuxing}',
                'solar_term': current_term,
                'chong_sha': f'冲{chong_zodiac}({chong_dz})煞{"东" if day_dz_idx % 4 == 0 else "南" if day_dz_idx % 4 == 1 else "西" if day_dz_idx % 4 == 2 else "北"}',
                'zodiac': BaziCalculator.SHENGXIAO[year_dz_idx],
            }
        except Exception as e:
            return {'error': str(e)}


# ============================================================
# 9. 解梦服务 JieMengService
# ============================================================

class JieMengService:
    """解梦服务"""

    # 常见梦境数据库
    DREAM_DB = {
        '蛇': {
            'keywords': ['蛇', '蟒蛇', '毒蛇', '大蛇', '小蛇'],
            'analysis': '梦见蛇通常象征潜意识的恐惧或欲望。蛇在梦中代表智慧、诱惑和变革。被蛇追赶暗示你在逃避某些问题；蛇缠身则可能暗示情感纠葛；梦到蛇蜕皮象征重生和转变。',
            'elements': '蛇属火，与变革、激情相关',
            'advice': '面对内心的恐惧，不要逃避问题。蛇也代表机遇，勇敢迎接变化。'
        },
        '水': {
            'keywords': ['水', '洪水', '大海', '河水', '游泳', '溺水'],
            'analysis': '梦见水象征情感和潜意识。清澈的水代表内心平静；浑浊的水暗示情感困扰；溺水可能暗示被情绪淹没；在水中自由游泳则表示情感释放和自由。',
            'elements': '水属阴，主情感、直觉和潜意识',
            'advice': '关注自己的情绪状态，学会疏导和释放情感，保持内心平静。'
        },
        '火': {
            'keywords': ['火', '火焰', '着火', '火灾', '烧'],
            'analysis': '梦见火象征热情、愤怒或净化。大火可能暗示情绪激动或危机；小火苗代表希望和灵感；被火灼伤暗示感情受挫；玩火则提醒不要冒险。',
            'elements': '火属阳，主热情、能量和转化',
            'advice': '控制好自己的脾气，将热情引导到正确的方向上。火也代表机遇，需谨慎把握。'
        },
        '飞行': {
            'keywords': ['飞', '飞翔', '飞行', '飘', '升空'],
            'analysis': '梦见飞行象征自由和超越。自由飞翔代表自信和成就感；飞不高暗示能力未充分发挥；从高处坠落则反映对失控的恐惧。',
            'elements': '飞行属木，主成长、自由和理想',
            'advice': '你渴望突破现状，不妨大胆尝试新事物。相信自己的能力，勇于追求梦想。'
        },
        '掉落': {
            'keywords': ['掉', '掉落', '坠落', '摔', '跌'],
            'analysis': '梦见掉落通常反映不安全感和对失控的恐惧。从高处坠落暗示对地位或关系的担忧；掉入水中则可能暗示情感上的不安。',
            'elements': '掉落属金，主收敛、反思和内省',
            'advice': '审视让你感到不安的根源，建立安全感。适当放松，不必事事追求完美。'
        },
        '考试': {
            'keywords': ['考试', '考', '测试', '答题', '交卷'],
            'analysis': '梦见考试通常反映焦虑和自我评价。考试迟到暗示准备不足；答不上题反映能力焦虑；考试顺利则表示自信；忘记带笔暗示缺乏自信。',
            'elements': '考试属土，主考验、责任和担当',
            'advice': '不要过分苛求自己，适当降低期望值。充分准备是消除焦虑的最好方法。'
        },
        '牙齿': {
            'keywords': ['牙齿', '牙', '掉牙', '拔牙'],
            'analysis': '梦见牙齿脱落是最常见的梦境之一。掉牙象征对衰老、失去和变化的焦虑；牙齿碎裂暗示自信受损；拔牙则可能反映需要做出痛苦的决定。',
            'elements': '牙齿属金，主决断、力量和自信',
            'advice': '关注自身健康，同时审视是否有需要放手的事物。变化是成长的一部分。'
        },
        '死亡': {
            'keywords': ['死', '死亡', '去世', '离世', '丧'],
            'analysis': '梦见死亡并非不祥之兆，反而象征结束和新生。自己死亡暗示旧我消逝、新我诞生；亲人去世可能反映对分离的恐惧或关系的转变。',
            'elements': '死亡属水，主转化、循环和重生',
            'advice': '不要恐惧变化，旧的结束意味着新的开始。拥抱转变，迎接新生。'
        },
        '婚礼': {
            'keywords': ['婚礼', '结婚', '嫁', '婚', '新郎', '新娘'],
            'analysis': '梦见婚礼象征新的开始和承诺。参加婚礼暗示将有喜事；自己结婚反映对亲密关系的渴望；婚礼被中断则暗示对承诺的犹豫。',
            'elements': '婚礼属火，主喜庆、承诺和新的开始',
            'advice': '你的内心渴望稳定的关系和新的开始。勇于做出承诺，珍惜身边的人。'
        },
        '追': {
            'keywords': ['追', '被追', '逃跑', '追赶'],
            'analysis': '梦见被追赶是最常见的压力梦境。被追赶暗示你在逃避某些问题或责任；追赶别人则表示你渴望掌控局面；追不上暗示目标过高。',
            'elements': '追赶属木，主行动、追求和压力',
            'advice': '停止逃避，勇敢面对让你焦虑的事物。直面问题才能找到解决方法。'
        },
        '鬼': {
            'keywords': ['鬼', '幽灵', '鬼魂', '灵异'],
            'analysis': '梦见鬼魂象征内心的恐惧和未解决的情感。被鬼追赶暗示被过去的事情困扰；与鬼交谈则可能反映内心的自我对话；见到熟悉的人变成鬼则暗示对失去的担忧。',
            'elements': '鬼属阴，主恐惧、潜意识和未了之事',
            'advice': '正视内心的恐惧，处理未了的心事。不要让过去的阴影影响现在的生活。'
        },
        '房子': {
            'keywords': ['房子', '房屋', '家', '房间', '楼房'],
            'analysis': '梦见房子象征自我和内心世界。新房代表新的开始或新的自我认知；破旧房子暗示需要自我更新；找不到房间反映迷茫；房子倒塌则暗示生活重大变故。',
            'elements': '房子属土，主安全、根基和自我',
            'advice': '审视自己的生活状态，是否需要做出改变。家是心灵的港湾，关注内心的安全感。'
        },
        '钱': {
            'keywords': ['钱', '金钱', '发财', '钞票', '钱币', '财富'],
            'analysis': '梦见金钱象征自我价值和能量。捡到钱暗示将获得意想不到的收获；丢钱则反映对失去的恐惧；数钱表示对物质生活的关注。',
            'elements': '金钱属金，主价值、交换和能量',
            'advice': '合理规划财务，但不要被物质束缚。真正的富足来自内心。'
        },
        '动物': {
            'keywords': ['动物', '猫', '狗', '鸟', '鱼', '老虎', '狮子'],
            'analysis': '梦见动物反映本能和直觉。温顺动物代表内心平静；凶猛动物暗示被压抑的情感；被动物攻击反映内心的冲突。',
            'elements': '动物属木，主本能、直觉和自然',
            'advice': '倾听内心的声音，关注自己的本能需求。与自然和谐相处。'
        },
        '迷路': {
            'keywords': ['迷路', '找不到', '方向', '迷失'],
            'analysis': '梦见迷路象征人生方向的迷茫。在陌生地方迷路暗示对未来的不确定；在熟悉地方迷路则可能反映对现状的不满。',
            'elements': '迷路属水，主迷茫、探索和寻找',
            'advice': '放慢脚步，重新审视人生方向。迷茫是成长的一部分，给自己时间。'
        },
        '裸体': {
            'keywords': ['裸体', '光身', '没穿衣服', '赤身'],
            'analysis': '梦见裸体象征脆弱和真实。在公共场合裸体暗示害怕被评判；自在地裸体则表示内心坦然；为裸体感到羞耻反映自尊问题。',
            'elements': '裸体属火，主真实、脆弱和自我暴露',
            'advice': '学会接纳真实的自己，不必在意他人的眼光。真诚是最美的品质。'
        },
        '吃': {
            'keywords': ['吃', '食物', '用餐', '美食', '饥饿'],
            'analysis': '梦见吃东西象征对精神和情感滋养的需求。暴饮暴食暗示生活失衡；吃不到东西则可能反映需求未被满足；品尝美食代表生活的享受。',
            'elements': '饮食属土，主滋养、满足和享受',
            'advice': '关注自己的身心需求，保持生活平衡。适度享受生活，但不要过度。'
        },
        '高处': {
            'keywords': ['高处', '山顶', '楼顶', '悬崖', '登高'],
            'analysis': '梦见高处象征抱负和成就。站在高处俯瞰代表成就感和掌控力；从高处俯视感到恐惧则暗示对成功的恐惧或不安全感。',
            'elements': '高处属金，主成就、视野和抱负',
            'advice': '勇于攀登高峰，但也要脚踏实地。高处不胜寒，保持谦逊。'
        },
        '雨': {
            'keywords': ['雨', '下雨', '暴雨', '细雨', '雨中'],
            'analysis': '梦见雨象征情感的宣泄和净化。细雨代表温柔的情感；暴雨暗示情感爆发或危机；雨后彩虹则预示困难过后会有希望。',
            'elements': '雨属水，主情感、宣泄和净化',
            'advice': '允许自己表达情感，适当宣泄有益身心健康。风雨过后必有彩虹。'
        },
        '门': {
            'keywords': ['门', '开门', '关门', '钥匙', '锁'],
            'analysis': '梦见门象征机遇和选择。开门代表新机遇；关门暗示结束或错失机会；锁住的门表示障碍；钥匙则象征解决问题的方法。',
            'elements': '门属金，主机遇、选择和转变',
            'advice': '把握眼前的机遇，勇于推开新的门。每个选择都是成长的机会。'
        },
        '镜子': {
            'keywords': ['镜子', '照镜子', '倒影', '镜像'],
            'analysis': '梦见镜子象征自我认知和反思。看到清晰的自己表示自我认识明确；模糊的镜像暗示对自我的不确定；破碎的镜子反映自我认同的危机。',
            'elements': '镜子属水，主反思、自我认知和真实',
            'advice': '学会客观地认识自己，接受自己的优点和不足。自省是成长的关键。'
        },
        '黑暗': {
            'keywords': ['黑暗', '黑夜', '暗', '看不见'],
            'analysis': '梦见黑暗象征未知和恐惧。身处黑暗暗示面临不确定的情况；从黑暗走向光明预示困难即将结束；在黑暗中找到方向则表示内心强大。',
            'elements': '黑暗属水，主未知、潜意识和内省',
            'advice': '不要害怕未知，黑暗中也有希望的光芒。相信自己的判断力。'
        },
    }

    @classmethod
    def analyze(cls, keyword):
        """
        基于关键词匹配梦境解析
        :param keyword: 梦境关键词
        :return: 解析结果
        """
        try:
            keyword = keyword.strip()

            # 精确匹配
            if keyword in cls.DREAM_DB:
                result = cls.DREAM_DB[keyword]
                return {
                    'keyword': keyword,
                    'analysis': result['analysis'],
                    'elements': result['elements'],
                    'advice': result['advice'],
                }

            # 关键词模糊匹配
            for key, data in cls.DREAM_DB.items():
                if keyword in data['keywords'] or keyword in key:
                    return {
                        'keyword': key,
                        'analysis': data['analysis'],
                        'elements': data['elements'],
                        'advice': data['advice'],
                    }

            # 包含匹配
            for key, data in cls.DREAM_DB.items():
                if any(k in keyword for k in data['keywords']) or key in keyword:
                    return {
                        'keyword': key,
                        'analysis': data['analysis'],
                        'elements': data['elements'],
                        'advice': data['advice'],
                    }

            # 未匹配到，返回通用分析
            return {
                'keyword': keyword,
                'analysis': f'梦见"{keyword}"是一个独特的梦境体验。每个梦境都蕴含着潜意识的信号，反映了你内心深处的想法和感受。建议你仔细回忆梦境的细节和情绪，这些都可能包含重要的信息。',
                'elements': '此梦境与多种元素相关，需结合具体细节分析',
                'advice': '保持对内心世界的关注，尝试记录梦境日志，有助于更好地理解自己的潜意识。如果反复做同样的梦，建议深入思考其背后的含义。'
            }
        except Exception as e:
            return {'error': str(e), 'keyword': keyword}


# ============================================================
# 10. 通用分析器 UniversalAnalyzer
# ============================================================

class UniversalAnalyzer:
    """通用分析器，根据模块类型路由到对应分析"""

    # 模块类型映射
    MODULE_MAP = {
        'bazi': 'bazi', '八字': 'bazi', '八字排盘': 'bazi',
        'shengxiao': 'shengxiao', '生肖': 'shengxiao', '生肖运势': 'shengxiao',
        'xingming': 'xingming', '姓名': 'xingming', '姓名分析': 'xingming', '五格': 'xingming',
        'heyun': 'heyun', '合婚': 'heyun', '配对': 'heyun', '婚姻': 'heyun',
        'huangli': 'huangli', '黄历': 'huangli', '老黄历': 'huangli', '宜忌': 'huangli',
        'jiemeng': 'jiemeng', '解梦': 'jiemeng', '梦境': 'jiemeng', '周公解梦': 'jiemeng',
        'tarot': 'tarot', '塔罗': 'tarot', '塔罗牌': 'tarot',
        'horoscope': 'horoscope', '星座': 'horoscope', '星座运势': 'horoscope',
        'xingzuo': 'horoscope', '星座运程': 'horoscope',
        'image': 'image', '图片': 'image', '面相': 'image', '手相': 'image',
        'mianxiang': 'image', 'shouxiang': 'image',
        'ziwei': 'ziwei', '紫微': 'ziwei', '紫微斗数': 'ziwei',
        'fengshui': 'fengshui', '风水': 'fengshui', '风水布局': 'fengshui',
        'liuyao': 'liuyao', '六爻': 'liuyao', '六爻占卜': 'liuyao',
        'qimen': 'qimen', '奇门': 'qimen', '奇门遁甲': 'qimen',
        'meihua': 'meihua', '梅花': 'meihua', '梅花易数': 'meihua',
        'taiyi': 'taiyi', '太乙': 'taiyi', '太乙神数': 'taiyi',
        'tieban': 'tieban', '铁板': 'tieban', '铁板神数': 'tieban',
        'fuzhou': 'fuzhou', '符咒': 'fuzhou',
        'shuzi': 'shuzi', '数字': 'shuzi', '数字命理': 'shuzi',
        'xuexing': 'xuexing', '血型': 'xuexing',
        'zeji': 'zeji', '择吉': 'zeji', '择日': 'zeji',
        'data_analysis': 'data_analysis', '数据分析': 'data_analysis',
    }

    @classmethod
    def _hash_params(cls, params):
        """生成参数哈希"""
        param_str = json.dumps(params, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(param_str.encode()).hexdigest()[:12]

    @classmethod
    def analyze(cls, module_type, params):
        """
        根据模块类型路由到对应分析
        :param module_type: 模块类型
        :param params: 分析参数字典
        :return: 分析结果
        """
        try:
            # 标准化模块类型
            normalized = cls.MODULE_MAP.get(module_type, module_type.lower() if module_type else '')

            cache_key = f"{module_type}:{cls._hash_params(params)}"
            cached = _global_cache.get(cache_key)
            if cached is not None:
                return cached

            result = None

            if normalized == 'bazi':
                result = BaziCalculator.calc_full(
                    name=params.get('name', '未知'),
                    gender=params.get('gender', '男'),
                    birth_date_str=params.get('birth_date', '2000-01-01'),
                    birth_time=params.get('birth_time', 12),
                    region_lon=params.get('region_lon', 116.4)
                )
            elif normalized == 'shengxiao':
                result = ShengxiaoCalculator.get_fortune(
                    zodiac=params.get('zodiac', '鼠'),
                    year=params.get('year', datetime.now().year),
                    month=params.get('month', 1),
                    day=params.get('day', 1)
                )
            elif normalized == 'xingming':
                result = XingmingCalculator.analyze(
                    name_str=params.get('name', '')
                )
            elif normalized == 'heyun':
                result = HeYunCalculator.match(
                    name1=params.get('name1', ''),
                    birth1=params.get('birth1', '2000-01-01'),
                    name2=params.get('name2', ''),
                    birth2=params.get('birth2', '2000-01-01')
                )
            elif normalized == 'huangli':
                result = HuangliService.get_huangli(
                    date_str=params.get('date', datetime.now().strftime('%Y-%m-%d'))
                )
            elif normalized == 'jiemeng':
                result = JieMengService.analyze(
                    keyword=params.get('keyword', '')
                )
            elif normalized == 'tarot':
                n = params.get('n', 3)
                result = TarotAPIClient.draw_random(n=n)
            elif normalized == 'horoscope':
                sign = params.get('sign', 'aries')
                period = params.get('period', 'daily')
                if period == 'weekly':
                    result = HoroscopeAPIClient.get_weekly(sign)
                elif period == 'monthly':
                    result = HoroscopeAPIClient.get_monthly(sign)
                else:
                    result = HoroscopeAPIClient.get_daily(sign)
            elif normalized == 'image':
                result = analyze_image(
                    params.get('base64_data', ''),
                    params.get('module_type', 'face')
                )
            else:
                result = cls._smart_fallback(normalized, params)

            if result is not None:
                _global_cache.set(cache_key, result, ttl=3600)

            return result
        except Exception as e:
            return {'error': str(e)}

    @classmethod
    def _smart_fallback(cls, normalized, params):
        """
        智能仿真分析：为暂无专用计算器的模块类型生成有意义的分析结果。
        基于输入参数（姓名、日期等）生成确定性的仿真数据，确保相同输入得到相同输出。
        """
        import hashlib

        param_str = json.dumps(params, sort_keys=True, ensure_ascii=False)
        seed_val = int(hashlib.md5(param_str.encode()).hexdigest()[:8], 16)
        rng = random.Random(seed_val)

        name = params.get('name', '用户')
        birth = params.get('birth_date', '2000-01-01')
        time_str = params.get('birth_time', '12:00')

        # 各维度的仿真评分
        categories = {
            'bazi': {'综合': (60, 95), '事业': (55, 92), '财运': (50, 90), '健康': (60, 95), '感情': (55, 92), '学业': (50, 88)},
            'ziwei': {'综合': (58, 95), '命宫': (50, 92), '财帛': (48, 90), '官禄': (52, 93), '夫妻': (50, 90), '福德': (55, 95)},
            'fengshui': {'综合': (55, 90), '方位': (50, 88), '格局': (48, 85), '气场': (52, 90), '财运': (45, 88), '健康': (55, 92)},
            'liuyao': {'综合': (55, 92), '用神': (48, 88), '应期': (50, 85), '变爻': (45, 90), '卦象': (52, 92), '世应': (50, 88)},
            'qimen': {'综合': (55, 90), '天盘': (50, 88), '地盘': (48, 85), '八门': (52, 90), '九星': (45, 88), '值符': (50, 85)},
            'meihua': {'综合': (58, 93), '主卦': (50, 90), '互卦': (48, 88), '变卦': (52, 92), '体用': (50, 90), '爻辞': (45, 85)},
            'taiyi': {'综合': (50, 88), '太乙': (48, 85), '计神': (45, 82), '文昌': (50, 88), '主算': (42, 80), '客算': (45, 82)},
            'tieban': {'综合': (55, 90), '命数': (50, 88), '运数': (48, 85), '流年': (52, 90), '条目': (45, 85), '考刻': (50, 88)},
            'fuzhou': {'综合': (50, 85), '符力': (45, 80), '咒力': (42, 78), '灵力': (48, 82), '缘份': (50, 85), '效验': (40, 80)},
            'shuzi': {'综合': (55, 92), '命数': (50, 90), '运数': (48, 88), '灵数': (52, 90), '周期': (50, 85), '吉凶': (45, 88)},
            'xuexing': {'综合': (55, 88), '性格': (50, 90), '运势': (48, 85), '健康': (52, 88), '事业': (50, 90), '爱情': (48, 88)},
            'zeji': {'综合': (60, 95), '天时': (55, 92), '地利': (50, 90), '人和': (52, 92), '吉时': (48, 88), '冲煞': (45, 85)},
            'data_analysis': {'综合': (60, 95), '模型': (55, 92), '数据': (52, 90), '算法': (50, 88), '趋势': (55, 93), '精准度': (58, 95)},
        }

        cat = categories.get(normalized, {'综合': (55, 90), '运势': (50, 88), '财运': (48, 85), '事业': (50, 88), '健康': (52, 90), '感情': (48, 85)})

        scores = {}
        for k, (lo, hi) in cat.items():
            scores[k] = rng.randint(lo, hi)

        # 生成综合评分
        overall = sum(scores.values()) // len(scores)

        # 幸运元素
        colors = ['红色', '金色', '蓝色', '绿色', '紫色', '白色', '黄色', '橙色', '青色', '黑色']
        numbers = [str(rng.randint(1, 9)) for _ in range(rng.randint(2, 5))]
        directions = ['东', '南', '西', '北', '东南', '西南', '东北', '西北']
        elements = ['金', '木', '水', '火', '土']

        lucky = {
            'colors': '、'.join(rng.sample(colors, 3)),
            'numbers': '、'.join(numbers),
            'directions': '、'.join(rng.sample(directions, 2)),
            'element': rng.choice(elements),
        }

        # 预计算条件文本（避免f-string嵌套大括号问题）
        z_yunshi = '上扬' if overall >= 75 else '平稳'
        z_jiji = '积极' if overall >= 70 else '谨慎'
        z_caibo = '格局良好' if scores.get('财帛', 70) >= 65 else '需要关注'
        f_qichang = '流通顺畅' if overall >= 72 else '需要调整'
        f_caiyun = '财运方位吉星高照，可适当布置招财物件' if scores.get('财运', 65) >= 62 else '建议在东南方位摆放绿植以改善气场'
        f_geju = '上等' if overall >= 80 else ('中等' if overall >= 65 else '尚可')
        l_da = '大有可为' if overall >= 75 else '需耐心等待'
        l_yong = '得力' if scores.get('用神', 65) >= 60 else '受克'
        l_shiying = '和谐' if scores.get('世应', 65) >= 60 else '需调和'
        q_men = '休门、生门、开门' if overall >= 72 else '需谨慎选择时机'
        q_xing = '明亮' if overall >= 70 else '有晦'
        q_fu = '得力' if overall >= 68 else '不足'
        m_gua = '吉卦' if overall >= 72 else '中平之卦'
        m_tiyong = '有利' if scores.get('体用', 65) >= 60 else '需注意'
        m_biangua = '向好' if scores.get('变卦', 65) >= 60 else '需谨慎'
        m_qianlu = '前路光明' if overall >= 75 else '有波折但可克服'
        t_ming = '贵格' if overall >= 75 else '中平'
        t_ru = '庙旺' if overall >= 70 else '闲地'
        t_shun = '顺行' if overall >= 68 else '逆行'
        t_wenchang = '照临' if scores.get('文昌', 65) >= 55 else '暗淡'
        t_xueye = '有成' if scores.get('文昌', 65) >= 55 else '需努力'
        tb_zhu = '吉' if overall >= 72 else '平'
        tb_yun = '顺遂' if scores.get('运数', 65) >= 58 else '有波折'
        tb_kao = '精准' if scores.get('考刻', 65) >= 58 else '需复验'
        tb_jie = '大吉' if overall >= 80 else ('中吉' if overall >= 65 else '尚可')
        fu_yuan = '深厚' if overall >= 70 else '一般'
        fu_fuli = '充沛' if scores.get('符力', 60) >= 50 else '平常'
        fu_zhouli = '通达' if scores.get('咒力', 60) >= 48 else '需加持'
        life_num = overall % 9 + 1
        life_types = ['领导型','协调型','创意型','务实型','自由型','关怀型','智慧型','权力型','博爱型']
        shu_type = life_types[life_num - 1] if life_num <= 9 else '综合型'
        shu_zhouqi = '上升' if overall >= 70 else '稳定'
        xue_xingge = '鲜明积极' if overall >= 72 else '内敛务实'
        xue_shiye = '看好' if scores.get('事业', 65) >= 58 else '宜稳中求进'
        xue_aiqing = '甜蜜' if scores.get('爱情', 65) >= 58 else '需用心经营'
        xue_zhengti = '运势不错' if overall >= 68 else '运势平稳'
        zj_day = '宜行大事' if overall >= 75 else '宜小事不宜大事'
        zj_tian = '大吉' if scores.get('天时', 65) >= 60 else '中平'
        zj_di = '优越' if scores.get('地利', 65) >= 58 else '一般'
        da_model = '深度学习模型' if overall >= 75 else '多维度数据'
        da_match = '成功' if overall >= 72 else '部分成功'
        da_advice = '综合建议：近期宜主动出击' if overall >= 73 else '综合建议：近期宜稳中求进'
        fb_level = '上等' if overall >= 80 else ('中上' if overall >= 70 else ('中等' if overall >= 60 else '尚可'))
        fb_zhishi = '表现良好' if overall >= 70 else '有望提升'

        # 生成总结
        summaries = {
            'ziwei': '紫微斗数命盘分析显示，%s的命宫主星旺相，整体运势%s。各大限宫位呈现%s态势，财帛宫与官禄宫%s。建议在%s旺的年份把握机遇。' % (name, z_yunshi, z_jiji, z_caibo, lucky['element']),
            'fengshui': '风水布局分析表明，当前气场%s。%s。整体格局属于%s格局。' % (f_qichang, f_caiyun, f_geju),
            'liuyao': '六爻占卜结果显示，%s所求之事%s。用神爻位%s，世爻与应爻关系%s。建议选择%s方行事。' % (name, l_da, l_yong, l_shiying, lucky['directions'].split('、')[0]),
            'qimen': '奇门遁甲排盘显示，八门中%s之方为吉。天盘星宿%s，值符%s。建议在%s方%s时行事。' % (q_men, q_xing, q_fu, lucky['directions'].split('、')[0], lucky['colors'].split('、')[0]),
            'meihua': '梅花易数起卦分析，%s得%s。体用生克关系%s，变卦%s。综合来看，%s。' % (name, m_gua, m_tiyong, m_biangua, m_qianlu),
            'taiyi': '太乙神数推算，%s命格属%s。太乙入%s，计神%s。文昌星%s，主学业%s。' % (name, t_ming, t_ru, t_shun, t_wenchang, t_xueye),
            'tieban': '铁板神数推算，%s命数为第%s条，主%s。运数%s，考刻%s。综合来看%s。' % (name, overall, tb_zhu, tb_yun, tb_kao, tb_jie),
            'fuzhou': '符咒灵力分析，%s与符咒之缘%s。今日符力%s，咒力%s。建议配合%s性法器使用。' % (name, fu_yuan, fu_fuli, fu_zhouli, lucky['element']),
            'shuzi': '数字命理分析，%s的生命灵数为%s，属于%s。运势周期处于%s阶段。' % (name, life_num, shu_type, shu_zhouqi),
            'xuexing': '血型命理分析，%s的性格特质%s。事业运势%s，感情运势%s。整体%s。' % (name, xue_xingge, xue_shiye, xue_aiqing, xue_zhengti),
            'zeji': '择吉分析，%s今日%s。天时%s，地利%s。建议在%s方行事，避开冲煞。' % (name, zj_day, zj_tian, zj_di, lucky['directions'].split('、')[0]),
            'data_analysis': '大数据AI分析，对%s的生辰八字进行%s分析。模型预测精准度为%s%%，命理模式匹配%s。%s。' % (name, da_model, overall, da_match, da_advice),
        }

        fallback_summary = '综合分析显示，%s的整体运势评分为%s分，属于%s水平。各项指标%s，建议保持积极心态，把握好运时机。' % (name, overall, fb_level, fb_zhishi)

        summary = summaries.get(normalized, fallback_summary)

        # 生成细分描述
        details = []
        for k, v in scores.items():
            is_health = (k == '健康')
            if v >= 85:
                d1 = '精力充沛' if is_health else '一片光明'
                d2 = '适度锻炼' if is_health else '大胆行动'
                details.append('%s: 极佳 (%s分) — 该领域%s，可%s。' % (k, v, d1, d2))
            elif v >= 75:
                d1 = '状态良好' if is_health else '稳中有升'
                details.append('%s: 良好 (%s分) — 该领域%s，保持现状即可收获。' % (k, v, d1))
            elif v >= 65:
                d1 = '需注意作息' if is_health else '平平，宜稳扎稳打'
                details.append('%s: 中等 (%s分) — 该领域%s，不宜冒进。' % (k, v, d1))
            elif v >= 55:
                d1 = '需关注，建议体检' if is_health else '有挑战，需谨慎应对'
                details.append('%s: 偏低 (%s分) — 该领域%s。' % (k, v, d1))
            else:
                d1 = '建议调养' if is_health else '压力较大'
                d2 = '寻医问诊' if is_health else '韬光养晦'
                details.append('%s: 较弱 (%s分) — 该领域%s，宜%s。' % (k, v, d1, d2))

        # 建议
        advices = [
            f'幸运方位: {lucky["directions"]}，办事宜面向此方',
            f'幸运颜色: {lucky["colors"]}，可在衣物或配饰中选用',
            f'幸运数字: {lucky["numbers"]}，选择日期时可优先考虑',
            f'五行喜{lucky["element"]}，可佩戴{lucky["element"]}性饰品增强运势',
            '保持心态平和，顺势而为，方能事半功倍',
        ]

        return {
            'scores': scores,
            'overall': overall,
            'summary': summary,
            'details': details,
            'advices': advices,
            'lucky_elements': lucky,
            'module_type': normalized,
            'source': '智能仿真分析',
            'generated_at': datetime.now().isoformat(),
        }


# ============================================================
# 11. 图片分析增强版
# ============================================================

def analyze_image(base64_data, module_type='face'):
    """
    增强版图片分析
    :param base64_data: 图片的base64编码
    :param module_type: 分析模块类型（face/palm/physiognomy等）
    :return: 分析结果字典
    """
    try:
        if not base64_data:
            return {'error': '未提供图片数据'}

        # 基于图片数据生成确定性种子
        data_hash = hashlib.md5(base64_data.encode()).hexdigest()
        seed = int(data_hash[:8], 16)
        rng = random.Random(seed)

        # 颜色分析（简化：基于数据哈希）
        colors = {
            'dominant': rng.choice(['暖色调', '冷色调', '中性色调', '明亮色调', '柔和色调']),
            'brightness': rng.randint(40, 90),
            'saturation': rng.randint(30, 80),
            'contrast': rng.choice(['高对比', '中等对比', '低对比']),
        }

        # 构图分析
        composition = {
            'balance': rng.choice(['对称构图', '三分构图', '居中构图', '对角线构图']),
            'depth': rng.choice(['前景清晰', '层次分明', '平面构图']),
            'focus': rng.choice(['中心聚焦', '分散聚焦', '边缘聚焦']),
            'lines': rng.choice(['水平线为主', '垂直线为主', '曲线为主', '斜线为主']),
        }

        # 纹理复杂度
        texture = {
            'complexity': rng.choice(['简洁', '适中', '复杂', '非常复杂']),
            'pattern': rng.choice(['几何图案', '自然纹理', '随机纹理', '混合纹理']),
            'detail_level': rng.randint(1, 10),
        }

        # 根据模块类型生成分析
        if module_type in ('face', '面相'):
            result = _analyze_face(rng)
        elif module_type in ('palm', '手相'):
            result = _analyze_palm(rng)
        elif module_type in ('physiognomy', '相术'):
            result = _analyze_physiognomy(rng)
        else:
            result = _analyze_generic_image(rng, module_type)

        # 合并通用分析
        result['image_analysis'] = {
            'colors': colors,
            'composition': composition,
            'texture': texture,
            'data_hash': data_hash[:12],
        }

        return result
    except Exception as e:
        return {'error': str(e)}


def _analyze_face(rng):
    """面相分析"""
    features = ['额头饱满', '眉清目秀', '鼻梁挺直', '嘴唇丰厚', '下巴圆润',
                '颧骨适中', '耳大有轮', '眼大有神', '眉骨突出', '面部方正']
    selected = rng.sample(features, 4)

    fortune_areas = {
        '事业运': rng.randint(60, 95),
        '财运': rng.randint(55, 90),
        '感情运': rng.randint(50, 92),
        '健康运': rng.randint(60, 88),
        '人际运': rng.randint(55, 90),
    }

    return {
        'module_type': 'face',
        'features': selected,
        'fortune': fortune_areas,
        'face_shape': rng.choice(['圆形', '方形', '长形', '瓜子脸', '鹅蛋脸']),
        'five_features': {
            '眉': rng.choice(['浓眉', '淡眉', '长眉', '短眉', '柳叶眉']),
            '眼': rng.choice(['大眼', '小眼', '凤眼', '杏眼', '三角眼']),
            '鼻': rng.choice(['高鼻', '塌鼻', '蒜头鼻', '鹰钩鼻', '直鼻']),
            '口': rng.choice(['大口', '小口', '厚唇', '薄唇', '樱桃口']),
            '耳': rng.choice(['大耳', '小耳', '贴脑耳', '招风耳', '圆耳']),
        },
        'summary': f'面相分析显示{selected[0]}，{selected[1]}，整体面相{"上佳" if sum(fortune_areas.values()) / 5 > 75 else "中等" if sum(fortune_areas.values()) / 5 > 60 else "需注意"}。'
    }


def _analyze_palm(rng):
    """手相分析"""
    lines = {
        '生命线': {'length': rng.choice(['长', '中等', '短']), 'depth': rng.choice(['深', '浅', '中等']),
                   'desc': rng.choice(['生命力旺盛', '需注意健康', '生活平稳'])},
        '智慧线': {'length': rng.choice(['长', '中等', '短']), 'clarity': rng.choice(['清晰', '模糊', '有分叉']),
                   'desc': rng.choice(['思维敏捷', '善于分析', '创造力强'])},
        '感情线': {'length': rng.choice(['长', '中等', '短']), 'shape': rng.choice(['平直', '弯曲', '有岛纹']),
                   'desc': rng.choice(['感情丰富', '理性对待感情', '感情细腻'])},
        '事业线': {'depth': rng.choice(['深', '浅', '无']), 'direction': rng.choice(['直上', '弯曲', '分叉']),
                   'desc': rng.choice(['事业稳定上升', '事业多变化', '创业之相'])},
    }

    return {
        'module_type': 'palm',
        'palm_lines': lines,
        'finger_shape': rng.choice(['修长', '粗壮', '匀称', '纤细']),
        'palm_shape': rng.choice(['方形', '长形', '圆形', '椭圆形']),
        'special_marks': rng.sample(['金星丘饱满', '月丘发达', '水星丘突出', '木星丘隆起', '太阳丘明显'], 2),
        'summary': f'手相分析显示生命线{lines["生命线"]["desc"]}，智慧线{lines["智慧线"]["desc"]}，感情线{lines["感情线"]["desc"]}。'
    }


def _analyze_physiognomy(rng):
    """综合相术分析"""
    return {
        'module_type': 'physiognomy',
        'overall_rating': rng.randint(60, 95),
        'elements': {
            '天庭': rng.choice(['饱满', '一般', '略窄']),
            '地阁': rng.choice(['方圆', '尖削', '丰满']),
            '左右': rng.choice(['对称', '微偏', '匀称']),
        },
        'energy': rng.choice(['气场强', '气场温和', '内敛']),
        'summary': '综合相术分析显示您具有独特的气质和潜力，未来可期。'
    }


def _analyze_generic_image(rng, module_type):
    """通用图片分析"""
    scores = {
        '综合评分': rng.randint(55, 95),
        '能量指数': rng.randint(40, 90),
        '吉祥指数': rng.randint(50, 95),
        '和谐指数': rng.randint(45, 90),
    }
    return {
        'module_type': module_type,
        'scores': scores,
        'summary': f'图片分析完成，综合评分{scores["综合评分"]}分。',
    }


# ============================================================
# 模块级全局实例（供 fortune_routes.py 导入使用）
# ============================================================
cache = FortuneCache()
horoscope_client = HoroscopeAPIClient()
tarot_client = TarotAPIClient()
bazi_calc = BaziCalculator()
shengxiao_calc = ShengxiaoCalculator()
xingming_calc = XingmingCalculator()
heyun_calc = HeYunCalculator()
huangli_svc = HuangliService()
jiemeng_svc = JieMengService()
universal_analyzer = UniversalAnalyzer()
