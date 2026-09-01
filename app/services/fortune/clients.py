"""外部 API 客户端（星座 / 塔罗，带重试与降级）"""

import hashlib
import json
import math
import random
import time
from datetime import datetime, timedelta

import requests

from app.services.fortune.logging_utils import log_info, log_error, log_debug, log_warning

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
