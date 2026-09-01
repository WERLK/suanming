"""缓存层 FortuneCache（TTL + 命中统计）"""

import hashlib
import json
import math
import random
import time
from datetime import datetime, timedelta

import requests

from app.services.fortune.logging_utils import log_info, log_error, log_debug, log_warning

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

# 全局缓存实例
_global_cache = FortuneCache()

# ============================================================
# 2. 外部API客户端 HoroscopeAPIClient
# ============================================================
