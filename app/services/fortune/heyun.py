"""合婚配对计算器"""

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
from app.services.fortune.xingming import XingmingCalculator

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
