"""通用分析器（模块路由分发 + 降级生成）"""

import hashlib
import json
import math
import random
import time
from datetime import datetime, timedelta

import requests

from app.services.fortune.logging_utils import log_info, log_error, log_debug, log_warning
from app.services.fortune.bazi import BaziCalculator
from app.services.fortune.cache import FortuneCache
from app.services.fortune.clients import HoroscopeAPIClient, TarotAPIClient
from app.services.fortune.heyun import HeYunCalculator
from app.services.fortune.huangli import HuangliService
from app.services.fortune.image import analyze_image
from app.services.fortune.jiemeng import JieMengService
from app.services.fortune.shengxiao import ShengxiaoCalculator
from app.services.fortune.xingming import XingmingCalculator

_global_cache = FortuneCache()

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
        'caishen': 'caishen', '财神': 'caishen', '财神方位': 'caishen',
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

            try:
                if normalized == 'bazi':
                    result = BaziCalculator.calc_full(
                        name=params.get('name', '未知'),
                        gender=params.get('gender', '男'),
                        birth_date_str=params.get('birth_date', '2000-01-01'),
                        birth_time=params.get('birth_time', 12),
                        region_lon=params.get('region_lon', 116.4)
                    )
                    if result and isinstance(result, dict) and 'error' not in result:
                        result = cls._enrich_bazi_result(result)
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
            except Exception as e:
                log_warning(f"专用计算器失败 ({normalized}): {str(e)}，回退到智能仿真")
                result = cls._smart_fallback(normalized, params)

            if result is not None:
                _global_cache.set(cache_key, result, ttl=3600)

            return result
        except Exception as e:
            log_error(f"analyze 全局异常: {str(e)}")
            return cls._smart_fallback(normalized if 'normalized' in dir() else module_type, params)

    @classmethod
    def _enrich_bazi_result(cls, bazi_data):
        """
        为八字排盘结果添加通用分析字段（scores/summary/lucky_elements 等），
        使前端通用模板能够正确渲染展示。
        """
        import random
        import hashlib
        # 基于姓名+日柱生成确定性评分
        seed_str = bazi_data.get('name', '') + bazi_data.get('day_master', '')
        seed_val = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        rng = random.Random(seed_val)

        # 五行平衡度评分
        wuxing = bazi_data.get('wuxing_stats', {})
        total = sum(wuxing.values()) if wuxing else 1
        balance = 100 - int(max(abs(v/total - 0.2) for v in wuxing.values()) * 200) if wuxing else 70
        balance = max(50, min(95, balance))

        overall = rng.randint(70, 92)
        scores = {
            '综合': overall,
            '五行平衡': balance,
            '事业': rng.randint(65, 95),
            '财运': rng.randint(60, 90),
            '婚姻': rng.randint(65, 92),
            '健康': rng.randint(70, 95),
        }

        day_master = bazi_data.get('day_master', '日')
        day_master_element = bazi_data.get('day_master_element', '')
        xiyong = bazi_data.get('xiyong', {})
        xishen = xiyong.get('喜神', '')
        yongshen = xiyong.get('用神', '')

        summary = (
            f"八字排盘分析：日主为{day_master}（{day_master_element}），"
            f"喜神{xishen}，用神{yongshen}。"
            f"整体运势{'较佳' if overall >= 80 else '平稳'}，"
            f"五行{'' if balance >= 75 else '略欠'}平衡，"
            f"建议顺势而为，把握机遇。"
        )

        # 幸运元素
        lucky_elements = {
            'colors': f"{yongshen}色、{xishen}色" if yongshen and xishen else '白色、青色',
            'numbers': str(rng.choice([2, 4, 6, 8])) + '、' + str(rng.choice([1, 3, 5, 7, 9])),
            'directions': rng.choice(['东、东南', '南、西南', '西、西北', '北、东北']),
            'element': yongshen or day_master_element or '木',
        }

        # 详情列表
        details = []
        if bazi_data.get('shishen'):
            for gan, shen in list(bazi_data['shishen'].items())[:4]:
                details.append(f"{gan}：{shen}")
        if bazi_data.get('pillars'):
            details.append(
                "四柱：" + " ".join([p['ganzhi'] for p in bazi_data['pillars']])
            )

        # 建议列表
        advices = [
            f"五行喜{lucky_elements['element']}，可多接触相关属性事物增强运势",
            f"幸运方位：{lucky_elements['directions']}，办事宜面向此方",
            f"幸运颜色：{lucky_elements['colors']}，可在衣物或配饰中选用",
            f"幸运数字：{lucky_elements['numbers']}，选择日期时可优先考虑",
            "保持心态平和，顺势而为，方能事半功倍",
        ]

        bazi_data['scores'] = scores
        bazi_data['overall'] = overall
        bazi_data['summary'] = summary
        bazi_data['details'] = details
        bazi_data['advices'] = advices
        bazi_data['lucky_elements'] = lucky_elements
        bazi_data['module_type'] = 'bazi'
        bazi_data['source'] = '八字排盘分析'
        return bazi_data

    @classmethod
    def get_caishen(cls, date_str):
        """
        获取指定日期的财神方位
        根据传统干支推算：日干决定财神方位
        :param date_str: 日期字符串 YYYY-MM-DD
        :return: 财神方位详细信息
        """
        try:
            from datetime import date as date_type
            dt = date_type.fromisoformat(date_str)

            # 计算日柱天干（与 BaziCalculator 算法一致）
            ref_date = date_type(1900, 1, 31)  # 甲子日
            diff = (dt - ref_date).days
            tg_idx = (0 + diff) % 10  # 1900-01-31 = 甲子, index 0
            tian_gan = BaziCalculator.TIANGAN[tg_idx]

            # 财神方位根据日干确定
            direction_map = {
                '甲': ('东北方', '甲日财神在东北，宜向东北方求财'),
                '乙': ('东北方', '乙日财神在东北，宜向东北方求财'),
                '丙': ('正东方', '丙日财神在正东，宜向正东方求财'),
                '丁': ('正东方', '丁日财神在正东，宜向正东方求财'),
                '戊': ('正北方', '戊日财神在正北，宜向正北方求财'),
                '己': ('正北方', '己日财神在正北，宜向正北方求财'),
                '庚': ('正西方', '庚日财神在正西，宜向正西方求财'),
                '辛': ('正西方', '辛日财神在正西，宜向正西方求财'),
                '壬': ('正南方', '壬日财神在正南，宜向正南方求财'),
                '癸': ('正南方', '癸日财神在正南，宜向正南方求财'),
            }
            direction, direction_desc = direction_map.get(
                tian_gan, ('正东方', '财神方位正东')
            )

            # 喜神方位
            xishen_map = {
                '甲': '东北方', '乙': '西北方', '丙': '西南方',
                '丁': '正南方', '戊': '东南方', '己': '正东方',
                '庚': '西北方', '辛': '西南方', '壬': '正南方', '癸': '东南方',
            }
            # 福神方位
            fushen_map = {
                '甲': '东南方', '乙': '正东方', '丙': '正北方',
                '丁': '正东方', '戊': '正北方', '己': '正南方',
                '庚': '西南方', '辛': '正西方', '壬': '西北方', '癸': '正西方',
            }

            xishen = xishen_map.get(tian_gan, '东南方')
            fushen = fushen_map.get(tian_gan, '正东方')

            # 最佳时段（巳时、午时）
            best_time = '巳时(09:00-11:00)、午时(11:00-13:00)'

            # 宜忌
            yi_list = ['求财', '交易', '开市', '签约', '纳财', '投资']
            ji_list = ['破土', '安葬', '词讼', '争执']

            # 供品
            supplies = '香三支、红烛一对、时令水果三样、糕点三盘、清茶一杯'

            # 供香指南
            incense_guide = (
                '1. 面向%s摆放供桌，保持整洁\n'
                '2. 点燃香烛，虔诚默念心愿\n'
                '3. 摆放供品，水果以苹果、橘子、葡萄为佳\n'
                '4. 最佳祭拜时间：%s\n'
                '5. 祭拜完毕后，供品可分食，寓意分享福气\n'
                '6. 心诚则灵，不可心存不敬'
            ) % (direction, best_time)

            return {
                'direction': direction,
                'wealth_direction': direction,
                'day_gan': tian_gan,
                'xishen': xishen,
                'fushen': fushen,
                'best_time': best_time,
                'time': best_time,
                '时辰': best_time,
                'yi': '、'.join(yi_list),
                'suitable': '、'.join(yi_list),
                '宜': '、'.join(yi_list),
                'ji': '、'.join(ji_list),
                'taboo': '、'.join(ji_list),
                '忌': '、'.join(ji_list),
                'supplies': supplies,
                '供品': supplies,
                'incense_guide': incense_guide,
                '供香指南': incense_guide,
                'tips': '今日财神位于%s，喜神在%s，福神在%s。最佳求财时段为巳时和午时。' % (direction, xishen, fushen),
                'advice': '建议在%s放置招财物件或进行商务活动，可提升财运。' % direction,
                '建议': '建议在%s放置招财物件或进行商务活动，可提升财运。' % direction,
                'summary': '%s（%s日）财神方位：%s。%s。' % (date_str, tian_gan, direction, direction_desc),
                'date': date_str,
            }
        except Exception as e:
            return {
                'direction': '正东方',
                'summary': '财神方位查询出错：%s' % str(e),
                'date': date_str,
                'error': str(e),
            }

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
            'caishen': {'综合': (58, 95), '财神': (55, 92), '财运': (55, 95), '吉时': (52, 90), '方位': (50, 88)},
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
