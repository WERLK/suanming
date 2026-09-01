"""
算命领域服务包 — 聚合导出（保持与旧 fortune_routes.py 相同的导入契约）。

每个计算器独立成模块，此处统一实例化为模块级单例，
路由层只从这里取依赖，替换实现（如换 Redis 缓存）只改本文件。
"""
from app.services.fortune.cache import FortuneCache
from app.services.fortune.clients import HoroscopeAPIClient, TarotAPIClient
from app.services.fortune.bazi import BaziCalculator
from app.services.fortune.shengxiao import ShengxiaoCalculator
from app.services.fortune.xingming import XingmingCalculator
from app.services.fortune.heyun import HeYunCalculator
from app.services.fortune.huangli import HuangliService
from app.services.fortune.jiemeng import JieMengService
from app.services.fortune.universal import UniversalAnalyzer
from app.services.fortune.image import analyze_image
from app.services.fortune.logging_utils import (
    log_info, log_error, log_debug, log_warning,
)

# ---- 模块级单例（与旧版 fortune_service.py 导出保持同名同序） ----
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

__all__ = [
    'FortuneCache', 'HoroscopeAPIClient', 'TarotAPIClient',
    'BaziCalculator', 'ShengxiaoCalculator', 'XingmingCalculator',
    'HeYunCalculator', 'HuangliService', 'JieMengService',
    'UniversalAnalyzer', 'analyze_image',
    'cache', 'horoscope_client', 'tarot_client', 'bazi_calc',
    'shengxiao_calc', 'xingming_calc', 'heyun_calc', 'huangli_svc',
    'jiemeng_svc', 'universal_analyzer',
    'log_info', 'log_error', 'log_debug', 'log_warning',
]
