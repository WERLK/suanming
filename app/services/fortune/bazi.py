"""八字排盘计算器"""

import hashlib
import json
import math
import random
import time
from datetime import datetime, timedelta

import requests

from app.services.fortune.logging_utils import log_info, log_error, log_debug, log_warning

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
                # 支持 "HH:MM" 格式和纯数字字符串
                if ':' in birth_time:
                    hour = int(birth_time.split(':')[0])
                else:
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
