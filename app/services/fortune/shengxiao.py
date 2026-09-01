"""生肖运势计算器"""

import hashlib
import json
import math
import random
import time
from datetime import datetime, timedelta

import requests

from app.services.fortune.logging_utils import log_info, log_error, log_debug, log_warning
from app.services.fortune.bazi import BaziCalculator

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
