"""黄历服务"""

import hashlib
import json
import math
import random
import time
from datetime import datetime, timedelta

import requests

from app.services.fortune.logging_utils import log_info, log_error, log_debug, log_warning
from app.services.fortune.bazi import BaziCalculator
from app.services.fortune.shengxiao import ShengxiaoCalculator

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
