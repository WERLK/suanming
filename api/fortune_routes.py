"""
算命API路由定义
包含：八字、生肖、星座、塔罗、黄历、合婚、解梦、姓名、紫微、通用分析等16条API端点

优化说明：
1. 添加详细日志记录
2. 优化速率限制（添加响应头）
3. 改进错误处理和降级策略
4. 添加性能监控
"""

import json
import time
from datetime import date, datetime
from functools import wraps
from flask import Blueprint, request, jsonify, g

from .fortune_service import (
    cache,
    horoscope_client,
    tarot_client,
    bazi_calc,
    shengxiao_calc,
    xingming_calc,
    heyun_calc,
    huangli_svc,
    jiemeng_svc,
    universal_analyzer,
    analyze_image,
    log_info,
    log_error,
    log_debug,
    log_warning,
)

fortune_bp = Blueprint('fortune', __name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ZODIAC_MAP = {
    '白羊座': 'aries', '金牛座': 'taurus', '双子座': 'gemini',
    '巨蟹座': 'cancer', '狮子座': 'leo', '处女座': 'virgo',
    '天秤座': 'libra', '天蝎座': 'scorpio', '射手座': 'sagittarius',
    '摩羯座': 'capricorn', '水瓶座': 'aquarius', '双鱼座': 'pisces',
}

# Simple in-memory IP-based rate limiter
_rate_limit_store = {}
_RATE_LIMIT_MAX = 60
_RATE_LIMIT_WINDOW = 60  # seconds


def _resolve_zodiac(raw):
    """Return the English zodiac name from either Chinese or English input."""
    if not raw:
        return 'aries'
    raw_lower = raw.strip().lower()
    # direct English mapping
    if raw_lower in ZODIAC_MAP.values():
        return raw_lower
    # Chinese → English via reverse lookup
    for cn, en in ZODIAC_MAP.items():
        if raw_lower == cn.lower():
            return en
    return 'aries'  # safe default


# ---------------------------------------------------------------------------
# Rate limiter helpers
# ---------------------------------------------------------------------------

def _check_rate_limit():
    """Check if the IP has exceeded rate limit. Returns True if allowed."""
    ip = request.remote_addr or '127.0.0.1'
    now = time.time()
    entry = _rate_limit_store.get(ip)

    if entry is None:
        _rate_limit_store[ip] = {'count': 1, 'reset': now + _RATE_LIMIT_WINDOW}
        log_debug(f"速率限制: {ip} 首次请求")
        return True

    if now > entry['reset']:
        _rate_limit_store[ip] = {'count': 1, 'reset': now + _RATE_LIMIT_WINDOW}
        log_debug(f"速率限制: {ip} 窗口重置")
        return True

    if entry['count'] >= _RATE_LIMIT_MAX:
        log_warning(f"速率限制: {ip} 超出限制 ({entry['count']}/{_RATE_LIMIT_MAX})")
        return False

    entry['count'] += 1
    return True


def _get_rate_limit_info():
    """Return current rate limit info for the IP."""
    ip = request.remote_addr or '127.0.0.1'
    entry = _rate_limit_store.get(ip)
    if entry is None:
        return {'count': 0, 'remaining': _RATE_LIMIT_MAX, 'reset_in': _RATE_LIMIT_WINDOW}
    remaining = max(0, _RATE_LIMIT_MAX - entry['count'])
    reset_in = max(0, int(entry['reset'] - time.time()))
    return {'count': entry['count'], 'remaining': remaining, 'reset_in': reset_in}


# ---------------------------------------------------------------------------
# Response helpers
# ---------------------------------------------------------------------------

def success_response(data, source='realtime', message='', module_type=None):
    """Return a success JSON response."""
    # 优先使用 data 中自带的 generated_at，否则用当前服务器时间
    generated_at = None
    if isinstance(data, dict) and 'generated_at' in data:
        generated_at = data['generated_at']
    if not generated_at:
        generated_at = datetime.now().isoformat()
    payload = {
        'success': True,
        'message': message,
        'data': data,
        'meta': {
            'source': source,
            'module_type': module_type if module_type else request.path.split('/')[-1],
            'generated_at': generated_at,
        },
    }
    log_info(f"API成功: {request.path} (source={source})")
    return jsonify(payload)


def error_response(message, code=400):
    """Return an error JSON response."""
    log_error(f"API错误: {request.path} - {message} (code={code})")
    return jsonify({'success': False, 'message': message}), code


def _cache_or_fetch(cache_key, ttl, fetcher):
    """Helper: try cache first, fall back to fetcher, then populate cache."""
    cached = cache.get(cache_key)
    if cached is not None:
        log_debug(f"缓存命中: {cache_key}")
        return cached, 'cached'

    log_debug(f"缓存未命中: {cache_key}，调用fetcher")
    try:
        data = fetcher()
        if data is not None:
            cache.set(cache_key, data, ttl)
            log_info(f"数据获取成功: {cache_key}")
            return data, 'realtime'
    except Exception as e:
        log_error(f"数据获取失败: {cache_key} - {str(e)}")
        # Try cache again (maybe expired but still usable)
        if cached is not None:
            log_warning(f"使用过期缓存: {cache_key}")
            return cached, 'local_fallback'

    return None, 'N/A'


# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------

def _endpoint(f):
    """Decorator for rate limiting and error handling."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Start timing
        start_time = time.time()
        
        # Rate limiting
        if not _check_rate_limit():
            return error_response('请求过于频繁，请稍后再试', 429)

        # Add rate limit headers
        rate_info = _get_rate_limit_info()
        
        try:
            response = f(*args, **kwargs)
            
            # Add rate limit headers to response
            if isinstance(response, tuple):
                resp, code = response
                resp.headers['X-RateLimit-Limit'] = str(_RATE_LIMIT_MAX)
                resp.headers['X-RateLimit-Remaining'] = str(rate_info['remaining'])
                resp.headers['X-RateLimit-Reset'] = str(rate_info['reset_in'])
                
                # Log response time
                elapsed = time.time() - start_time
                log_debug(f"API耗时: {request.path} - {elapsed:.3f}s")
                
                return resp, code
            elif hasattr(response, 'headers'):
                response.headers['X-RateLimit-Limit'] = str(_RATE_LIMIT_MAX)
                response.headers['X-RateLimit-Remaining'] = str(rate_info['remaining'])
                response.headers['X-RateLimit-Reset'] = str(rate_info['reset_in'])
                
                # Log response time
                elapsed = time.time() - start_time
                log_debug(f"API耗时: {request.path} - {elapsed:.3f}s")
                
            return response
        except ValueError as e:
            log_error(f"参数错误: {request.path} - {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            log_error(f"服务器错误: {request.path} - {str(e)}")
            return error_response('服务器内部错误，请稍后重试', 500)
    
    return decorated_function


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

# 1. POST /bazi
@fortune_bp.route('/bazi', methods=['POST'])
@_endpoint
def fortune_bazi():
    payload = request.get_json(silent=True) or {}
    name = payload.get('name', '')
    gender = payload.get('gender', 'unknown')
    birth_date = payload.get('birth_date', '')
    birth_time = payload.get('birth_time', 12)
    region_lon = payload.get('region_lon', 116.4)

    if not name or not birth_date:
        raise ValueError('姓名和出生日期不能为空')

    # 兼容中文时辰名
    SHICHEN_MAP = {
        '子时': 0, '丑时': 2, '寅时': 4, '卯时': 6,
        '辰时': 8, '巳时': 10, '午时': 12, '未时': 14,
        '申时': 16, '酉时': 18, '戌时': 20, '亥时': 22,
    }
    if isinstance(birth_time, str):
        if birth_time in SHICHEN_MAP:
            birth_time = SHICHEN_MAP[birth_time]
        else:
            try:
                birth_time = int(birth_time)
            except ValueError:
                birth_time = 12

    region_lon = float(region_lon) if region_lon else 120.0

    cache_key = f"bazi:{name}:{birth_date}:{birth_time}"
    data, source = _cache_or_fetch(cache_key, 86400, lambda: bazi_calc.calc_full(
        name, gender, birth_date, birth_time, region_lon
    ))
    if data is None:
        return error_response('请求过于频繁，请稍后重试', 429)
    return success_response(data, source, module_type='bazi')


# 2. POST /shengxiao
@fortune_bp.route('/shengxiao', methods=['POST'])
@_endpoint
def fortune_shengxiao():
    payload = request.get_json(silent=True) or {}
    zodiac = payload.get('zodiac', '')
    year = payload.get('year', date.today().year)
    month = payload.get('month', date.today().month)
    day = payload.get('day', date.today().day)

    if not zodiac:
        raise ValueError('生肖不能为空')

    cache_key = f"shengxiao:{zodiac}:{year}-{month}-{day}"
    data, source = _cache_or_fetch(cache_key, 3600, lambda: shengxiao_calc.get_fortune(
        zodiac, year, month, day
    ))
    if data is None:
        return error_response('请求过于频繁，请稍后重试', 429)
    return success_response(data, source, module_type='shengxiao')


# 3. POST /xingming
@fortune_bp.route('/xingming', methods=['POST'])
@_endpoint
def fortune_xingming():
    payload = request.get_json(silent=True) or {}
    name = payload.get('name', '')
    if not name:
        raise ValueError('姓名不能为空')

    cache_key = f"xingming:{name}"
    data, source = _cache_or_fetch(cache_key, 604800, lambda: xingming_calc.analyze(name))
    if data is None:
        return error_response('请求过于频繁，请稍后重试', 429)
    return success_response(data, source, module_type='xingming')


# 4. GET /xingzuo/daily
@fortune_bp.route('/xingzuo/daily', methods=['GET'])
@_endpoint
def fortune_xingzuo_daily():
    raw_sign = request.args.get('sign', 'aries')
    sign = _resolve_zodiac(raw_sign)
    cache_key = f'horoscope:daily:{sign}:{date.today().isoformat()}'
    data, source = _cache_or_fetch(cache_key, 86400, lambda: horoscope_client.get_daily(sign))
    if data is None:
        return error_response('请求过于频繁，请稍后重试', 429)
    return success_response(data, source, module_type='xingzuo_daily')


# 5. GET /xingzuo/weekly
@fortune_bp.route('/xingzuo/weekly', methods=['GET'])
@_endpoint
def fortune_xingzuo_weekly():
    raw_sign = request.args.get('sign', 'aries')
    sign = _resolve_zodiac(raw_sign)
    cache_key = f'horoscope:weekly:{sign}:{date.today().isoformat()}'
    data, source = _cache_or_fetch(cache_key, 86400, lambda: horoscope_client.get_weekly(sign))
    if data is None:
        return error_response('请求过于频繁，请稍后重试', 429)
    return success_response(data, source, module_type='xingzuo_weekly')


# 6. GET /xingzuo/monthly
@fortune_bp.route('/xingzuo/monthly', methods=['GET'])
@_endpoint
def fortune_xingzuo_monthly():
    raw_sign = request.args.get('sign', 'aries')
    sign = _resolve_zodiac(raw_sign)
    cache_key = f'horoscope:monthly:{sign}:{date.today().isoformat()}'
    data, source = _cache_or_fetch(cache_key, 86400, lambda: horoscope_client.get_monthly(sign))
    if data is None:
        return error_response('请求过于频繁，请稍后重试', 429)
    return success_response(data, source, module_type='xingzuo_monthly')


# 7. GET /tarot/cards
@fortune_bp.route('/tarot/cards', methods=['GET'])
@_endpoint
def fortune_tarot_cards():
    cache_key = 'tarot:all_cards'
    data, source = _cache_or_fetch(cache_key, 604800, tarot_client.get_all_cards)
    if data is None:
        return error_response('请求过于频繁，请稍后重试', 429)
    return success_response(data, source, module_type='tarot_cards')


# 8. GET /tarot/draw
@fortune_bp.route('/tarot/draw', methods=['GET'])
@_endpoint
def fortune_tarot_draw():
    try:
        n = int(request.args.get('n', 3))
    except (TypeError, ValueError):
        n = 3
    n = max(1, min(n, 10))

    # drawing is intentionally random – no caching
    data = tarot_client.draw_random(n)
    return success_response(data, 'realtime', module_type='tarot_draw')


# 9. GET /huangli
@fortune_bp.route('/huangli', methods=['GET'])
@_endpoint
def fortune_huangli():
    target_date = request.args.get('date', date.today().isoformat())
    cache_key = f'huangli:{target_date}'
    data, source = _cache_or_fetch(cache_key, 86400, lambda: huangli_svc.get_huangli(target_date))
    if data is None:
        return error_response('请求过于频繁，请稍后重试', 429)
    return success_response(data, source, module_type='huangli')


# 10. POST /heyun
@fortune_bp.route('/heyun', methods=['POST'])
@_endpoint
def fortune_heyun():
    payload = request.get_json(silent=True) or {}
    required_fields = ['name1', 'birth_date1', 'name2', 'birth_date2']
    missing = [f for f in required_fields if not payload.get(f)]
    if missing:
        raise ValueError(f'缺少必要参数: {", ".join(missing)}')

    cache_key = f"heyun:{payload['name1']}:{payload['birth_date1']}:{payload['name2']}:{payload['birth_date2']}"
    data, source = _cache_or_fetch(cache_key, 86400, lambda: heyun_calc.match(
        payload['name1'], payload['birth_date1'],
        payload['name2'], payload['birth_date2'],
    ))
    if data is None:
        return error_response('请求过于频繁，请稍后重试', 429)
    return success_response(data, source, module_type='heyun')


# 11. POST /jiemeng
@fortune_bp.route('/jiemeng', methods=['POST'])
@_endpoint
def fortune_jiemeng():
    payload = request.get_json(silent=True) or {}
    keyword = payload.get('keyword', '')
    if not keyword:
        raise ValueError('梦境关键词不能为空')

    cache_key = f'jiemeng:{keyword}'
    data, source = _cache_or_fetch(cache_key, 604800, lambda: jiemeng_svc.analyze(keyword))
    if data is None:
        return error_response('请求过于频繁，请稍后重试', 429)
    return success_response(data, source, module_type='jiemeng')


# 12. POST /ziwei
@fortune_bp.route('/ziwei', methods=['POST'])
@_endpoint
def fortune_ziwei():
    payload = request.get_json(silent=True) or {}
    name = payload.get('name', '')
    birth_date = payload.get('birth_date', '')
    birth_time = payload.get('birth_time', '')

    cache_key = f"ziwei:{name}:{birth_date}:{birth_time}"
    data, source = _cache_or_fetch(cache_key, 86400, lambda: universal_analyzer.analyze_ziwei(
        name, birth_date, birth_time
    ))
    if data is None:
        return error_response('请求过于频繁，请稍后重试', 429)
    return success_response(data, source, module_type='ziwei')


# 13. POST /analyze
@fortune_bp.route('/analyze', methods=['POST'])
@_endpoint
def fortune_analyze():
    payload = request.get_json(silent=True) or {}
    module_type = payload.get('module_type', '')
    module_subtype = payload.get('module_subtype', '')

    if not module_type:
        raise ValueError('module_type不能为空')

    cache_key = f"analyze:{module_type}:{module_subtype}:{json.dumps(payload, sort_keys=True)}"
    if module_subtype:
        payload['module_subtype'] = module_subtype
    data, source = _cache_or_fetch(cache_key, 86400, lambda: universal_analyzer.analyze(
        module_type, payload
    ))
    if data is None:
        return error_response('请求过于频繁，请稍后重试', 429)
    return success_response(data, source, module_type=module_type)


# 14. POST /image-analyze
@fortune_bp.route('/image-analyze', methods=['POST'])
@_endpoint
def fortune_image_analyze():
    if 'image' not in request.files:
        raise ValueError('请上传图片')

    file = request.files['image']
    module_type = request.form.get('module_type', 'mianxiang')

    if not file.filename:
        raise ValueError('请选择图片文件')

    # Save temporarily
    import os
    temp_path = f"/tmp/fortune_upload_{int(time.time())}.jpg"
    file.save(temp_path)

    try:
        data, source = analyze_image(temp_path, module_type)
        os.remove(temp_path)  # Clean up
        if data is None:
            return error_response('图片分析失败，请稍后重试', 500)
        return success_response(data, source, module_type=f'{module_type}_image')
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        log_error(f"图片分析失败: {str(e)}")
        return error_response('图片分析失败，请稍后重试', 500)


# 15. GET /caishen
@fortune_bp.route('/caishen', methods=['GET'])
@_endpoint
def fortune_caishen():
    target_date = request.args.get('date', date.today().isoformat())
    cache_key = f'caishen:{target_date}'
    data, source = _cache_or_fetch(cache_key, 86400, lambda: universal_analyzer.get_caishen(target_date))
    if data is None:
        return error_response('请求过于频繁，请稍后重试', 429)
    return success_response(data, source, module_type='caishen')


# 16. POST /liuyao
@fortune_bp.route('/liuyao', methods=['POST'])
@_endpoint
def fortune_liuyao():
    payload = request.get_json(silent=True) or {}
    question = payload.get('question', '')
    birth_date = payload.get('birth_date', '')

    if not question:
        raise ValueError('问题不能为空')

    cache_key = f"liuyao:{question}:{birth_date}"
    data, source = _cache_or_fetch(cache_key, 86400, lambda: universal_analyzer.analyze_liuyao(
        question, birth_date
    ))
    if data is None:
        return error_response('请求过于频繁，请稍后重试', 429)
    return success_response(data, source, module_type='liuyao')


# ---------------------------------------------------------------------------
# Health check endpoint
# ---------------------------------------------------------------------------

@fortune_bp.route('/health', methods=['GET'])
def fortune_health():
    """Health check endpoint."""
    return success_response({
        'status': 'ok',
        'cache_stats': cache.get_stats(),
        'timestamp': time.time()
    }, source='realtime', module_type='health')
