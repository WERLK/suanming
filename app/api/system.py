"""系统路由：健康检查/版本/静态资源/下载代理/广告健康/图片分析"""

from datetime import datetime
from flask import current_app

from flask import Blueprint, Response, jsonify, make_response, request, send_from_directory

from app.api.deps import load_users
from app.services.security import verify_token

import json


import os

import requests
from config import PROJECT_ROOT, USERS_FILE

bp = Blueprint('system', __name__)

@bp.route('/api/health')
def health_check():
    """健康检查端点"""
    try:
        # 检查数据库连接（这里使用文件检查代替）
        import os
        users_file_exists = os.path.exists(USERS_FILE)
        
        # 读取版本信息
        version_info = {'version': '1.0.0'}
        version_file = os.path.join(PROJECT_ROOT, 'version.json')
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                version_info = json.load(f)
        
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'service': 'xuanji-fortune',
            'version': version_info.get('version', '1.0.0'),
            'build_time': version_info.get('build_time', ''),
            'database': 'connected' if users_file_exists else 'disconnected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ========== 版本信息 ==========
@bp.route('/api/version')
def get_version():
    """获取版本信息"""
    try:
        import os
        version_file = os.path.join(PROJECT_ROOT, 'version.json')
        
        if os.path.exists(version_file):
            with open(version_file, 'r', encoding='utf-8') as f:
                version_info = json.load(f)
            return jsonify({
                'success': True,
                'version': version_info
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': '版本文件不存在'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 静态文件服务 ==========

@bp.route('/')
def index():
    return send_from_directory(PROJECT_ROOT, 'index.html')

@bp.route('/<path:filename>')
def serve_static(filename):
    """通用静态文件服务，捕获所有异常防止 500"""
    import os.path
    safe_path = os.path.realpath(os.path.join(PROJECT_ROOT, filename))
    real_root = os.path.realpath(PROJECT_ROOT)
    if not safe_path.startswith(real_root + os.sep) and safe_path != real_root:
        return 'Forbidden', 403
    try:
        return send_from_directory(PROJECT_ROOT, filename)
    except FileNotFoundError:
        return 'Not Found', 404
    except PermissionError:
        return 'Permission Denied', 403
    except Exception as e:
        current_app.logger.error(f'静态文件服务错误: {filename} - {str(e)}')
        return f'Internal Server Error: {str(e)}', 500

# 专用视频服务端点（绕过静态文件路由的潜在问题）
@bp.route('/video/guide-intro.mp4')
def serve_guide_video():
    """直接服务教程视频，设置正确的流媒体头"""
    import os.path
    video_path = os.path.join(PROJECT_ROOT, 'static', 'videos', 'guide-intro.mp4')
    if not os.path.isfile(video_path):
        return 'Video not found', 404
    try:
        response = make_response(send_from_directory(
            os.path.dirname(video_path),
            os.path.basename(video_path),
            mimetype='video/mp4',
            as_attachment=False
        ))
        response.headers['Accept-Ranges'] = 'bytes'
        response.headers['Content-Length'] = str(os.path.getsize(video_path))
        return response
    except Exception as e:
        current_app.logger.error(f'视频服务错误: {str(e)}')
        return f'Video serve error: {str(e)}', 500

@bp.route('/video/guide-poster.jpg')
def serve_guide_poster():
    """服务教程视频封面"""
    import os.path
    poster_path = os.path.join(PROJECT_ROOT, 'static', 'videos', 'guide-poster.jpg')
    if not os.path.isfile(poster_path):
        return 'Poster not found', 404
    try:
        return send_from_directory(os.path.dirname(poster_path), os.path.basename(poster_path), mimetype='image/jpeg')
    except Exception as e:
        current_app.logger.error(f'封面服务错误: {str(e)}')
        return f'Poster serve error: {str(e)}', 500

# ========== API路由 ==========


@bp.route('/api/image-analyze', methods=['POST'])
def image_analyze():
    """图片智能分析（玄学方向）"""
    try:
        data = request.get_json()
        image_data = data.get('image', '')
        module_type = data.get('module_type', 'bazi')
        
        if not image_data:
            return jsonify({'success': False, 'message': '请上传图片'}), 400
        
        # 去掉 base64 前缀
        if 'base64,' in image_data:
            image_data = image_data.split('base64,')[1]
        
        import base64
        from PIL import Image
        import io
        from collections import Counter
        
        img_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(img_bytes))
        
        width, height = img.size
        mode = img.mode
        img_rgb = img.convert('RGB')
        img_small = img_rgb.resize((50, 50))
        pixels = list(img_small.getdata())
        
        # 统计主色调
        r_avg = sum(p[0] for p in pixels) // len(pixels)
        g_avg = sum(p[1] for p in pixels) // len(pixels)
        b_avg = sum(p[2] for p in pixels) // len(pixels)
        brightness = (r_avg + g_avg + b_avg) // 3
        
        # 判断主色系和五行
        if r_avg > g_avg and r_avg > b_avg:
            dominant_color = '红'
            color_element = '火'
        elif g_avg > r_avg and g_avg > b_avg:
            dominant_color = '绿'
            color_element = '木'
        elif b_avg > r_avg and b_avg > g_avg:
            dominant_color = '蓝'
            color_element = '水'
        elif r_avg > 200 and g_avg > 200 and b_avg > 200:
            dominant_color = '白'
            color_element = '金'
        else:
            dominant_color = '黄'
            color_element = '土'
        
        # 根据模块类型生成分析
        analysis_map = {
            'bazi': f'【八字排盘·图片分析】\n主色调：{dominant_color}色系（五行属{color_element}）\n亮度：{"明亮" if brightness > 128 else "偏暗"}\n\n玄学解读：\n{"气色明亮，主近期运势顺畅，事宜进取。" if brightness > 128 else "气色偏暗，主近期宜守不宜攻，需蓄势待发。"}\n图片构图：{"方正清晰，主心性稳重。" if width >= height else "长方形构图，主思虑绵长。"}',
            'ziwei': f'【紫微斗数·图片分析】\n主色调：{dominant_color}色系（五行属{color_element}）\n\n玄学解读：\n{"命盘主色明亮，主福气深厚。" if brightness > 128 else "命盘主色偏暗，宜静心修持。"}',
            'fengshui': f'【风水堪舆·图片分析】\n主色调：{dominant_color}色系（五行属{color_element}）\n亮度：{brightness}\n\n风水解读：\n{"光线充足，阳气充沛，利于财运。" if brightness > 128 else "光线偏暗，阴气较重，宜增加照明。"}\n图片尺寸：{width}×{height}，{"横长方形宜作客厅布局" if width > height else "竖长方形宜作书房或卧室布局"}。',
            'tarot': f'【塔罗牌·图片分析】\n主色调：{dominant_color}色系（五行属{color_element}）\n\n牌意解读：\n{"色调明亮，主正位牌意，事情发展顺利。" if brightness > 128 else "色调偏暗，主逆位警示，需谨慎应对。"}',
            'heyun': f'【合婚配对·图片分析】\n主色调：{dominant_color}色系（五行属{color_element}）\n\n合婚解读：\n{"两人合照色调明亮，气场相合，配对指数高。" if brightness > 128 else "照片色调偏暗，建议多沟通增进了解。"}',
            'shengxiao': f'【生肖运势·图片分析】\n主色调：{dominant_color}色系\n\n生肖解读：\n{"属{color_element}之年出生者，今年财运较旺，宜把握机会。" if brightness > 128 else "今年宜稳扎稳打，不宜冒进。"}',
            'xingzuo': f'【星座运势·图片分析】\n主色调：{dominant_color}色系\n\n星座解读：\n{"性格外放，适合主动出击。" if brightness > 128 else "性格内敛，适合深思熟虑后行动。"}',
            'xuexing': f'【血型性格·图片分析】\n主色调：{dominant_color}色系\n\n血型解读：\n{"热血型性格，行动力强。" if r_avg > 150 else "冷静型性格，理智稳重。"}',
            'xingming': f'【姓名测试·图片分析】\n主色调：{dominant_color}色系（五行属{color_element}）\n\n姓名解读：\n{"姓名与图片色调相合，五格剖象吉。" if brightness > 128 else "建议改名或加用字以补五行。"}',
            'caishen': f'【财神方位·图片分析】\n主色调：{dominant_color}色系\n亮度：{brightness}\n\n财位解读：\n{"财神在正东方向，宜在此方位布置红色或金色物品。" if r_avg > 150 else "财神在西南方向，宜静待时机。"}',
        }
        
        analysis = analysis_map.get(module_type, analysis_map['bazi'])
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'image_info': {
                'width': width,
                'height': height,
                'dominant_color': dominant_color,
                'brightness': brightness,
                'element': color_element
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'分析失败：{str(e)}'}), 500


# ========== 客户端下载代理（绕过 GitHub 访问限制）==========

# GitHub Release 文件映射 + MIME 类型
_DOWNLOAD_FILES = {
    'windows': {
        'url': 'https://github.com/WERLK/suanming/releases/latest/download/玄机算命-Setup.exe',
        'filename': '玄机算命-Setup.exe',
        'mime': 'application/vnd.microsoft.portable-executable'
    },
    'linux': {
        'url': 'https://github.com/WERLK/suanming/releases/latest/download/玄机算命-Linux.AppImage',
        'filename': '玄机算命-Linux.AppImage',
        'mime': 'application/octet-stream'
    },
    'android': {
        'url': 'https://github.com/WERLK/suanming/releases/latest/download/玄机算命-Android.apk',
        'filename': '玄机算命-Android.apk',
        'mime': 'application/vnd.android.package-archive'
    }
}

# 下载缓存目录
_DOWNLOAD_CACHE_DIR = os.path.join(PROJECT_ROOT, 'downloads')
_CACHE_MAX_AGE = 24 * 3600  # 缓存24小时

# ========== 多平台广告健康检查 ==========
# 服务器在国内，可准确检测各平台链接是否可用
_AD_HEALTH_CACHE = {'platforms': {}, 'ts': 0}
_AD_HEALTH_TTL = 300  # 缓存 5 分钟

# 各平台检测 URL 列表
_AD_PLATFORM_URLS = {
    'ningmeng': [
        'http://www.huyis.com/link?1185',
        'http://www.huyis.com/link?1186'
    ],
    'huicheng': [
        'https://www.hczzw.com/'
    ],
    'mimeihui': [
        'https://www.mimeihui.com/'
    ],
    'douhao': [
        'https://union.douhao.com/'
    ]
}


@bp.route('/api/ad-health')
def ad_health_check():
    """检测各广告平台是否可用（由前端 ads.js 调用）"""
    now = time.time()
    if now - _AD_HEALTH_CACHE['ts'] < _AD_HEALTH_TTL:
        return jsonify({'success': True, 'platforms': _AD_HEALTH_CACHE['platforms']})

    platforms = {}
    for pid, urls in _AD_PLATFORM_URLS.items():
        alive = False
        for url in urls:
            try:
                r = requests.head(url, timeout=5, allow_redirects=True,
                                headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36'})
                if 200 <= r.status_code < 400:
                    alive = True
                    break
            except Exception:
                pass
        platforms[pid] = alive

    _AD_HEALTH_CACHE['platforms'] = platforms
    _AD_HEALTH_CACHE['ts'] = now
    return jsonify({'success': True, 'platforms': platforms})

@bp.route('/api/download/<platform>')
def download_proxy(platform):
    """下载代理：优先从服务器本地提供文件，本地不存在时尝试从 GitHub 拉取"""
    info = _DOWNLOAD_FILES.get(platform)
    if not info:
        return jsonify({'success': False, 'message': f'不支持的平台: {platform}'}), 404

    os.makedirs(_DOWNLOAD_CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(_DOWNLOAD_CACHE_DIR, info['filename'])

    # 1. 优先从本地直接返回（服务器本地已构建好的安装包）
    if os.path.exists(cache_path):
        return _send_file_response(cache_path, info['filename'], info['mime'])

    # 2. 本地没有，尝试从 GitHub Release 流式下载并缓存
    try:
        resp = requests.get(info['url'], stream=True, timeout=60,
                           headers={'User-Agent': 'XuanjiDownloadProxy/1.0'})
        if resp.status_code == 404:
            return jsonify({'success': False, 'message': '文件尚未构建，请稍后再试'}), 404
        if resp.status_code != 200:
            return jsonify({'success': False, 'message': f'下载失败 (HTTP {resp.status_code})'}), 502

        total_size = resp.headers.get('Content-Length')

        def generate():
            with open(cache_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        yield chunk

        headers = {
            'Content-Type': info['mime'],
            'Content-Disposition': f'attachment; filename="{info["filename"]}"'
        }
        if total_size:
            headers['Content-Length'] = total_size

        return Response(generate(), headers=headers, status=200)
    except requests.RequestException as e:
        return jsonify({'success': False, 'message': f'下载服务暂不可用: {str(e)}'}), 502


def _send_file_response(filepath, filename, mime):
    """发送本地文件响应（支持断点续传）"""
    file_size = os.path.getsize(filepath)
    range_header = request.headers.get('Range')

    if range_header:
        # 简单断点续传支持
        try:
            byte_range = range_header.replace('bytes=', '').split('-')
            start = int(byte_range[0]) if byte_range[0] else 0
            end = int(byte_range[1]) if len(byte_range) > 1 and byte_range[1] else file_size - 1
        except (ValueError, IndexError):
            start, end = 0, file_size - 1

        if start >= file_size:
            return Response('Range Not Satisfiable', status=416)

        length = end - start + 1
        with open(filepath, 'rb') as f:
            f.seek(start)
            data = f.read(length)

        resp = Response(data, status=206, mimetype=mime)
        resp.headers['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        resp.headers['Content-Length'] = str(length)
    else:
        with open(filepath, 'rb') as f:
            data = f.read()
        resp = Response(data, status=200, mimetype=mime)
        resp.headers['Content-Length'] = str(file_size)

    resp.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    resp.headers['Accept-Ranges'] = 'bytes'
    return resp
def auto_update():
    import subprocess
    try:
        cwd = '/root/suanming'  # 服务器项目目录
        # 拉取最新代码
        r1 = subprocess.run(['git', 'fetch', 'origin'], cwd=cwd, capture_output=True, text=True, timeout=300)
        # 重置到最新 main 分支
        r2 = subprocess.run(['git', 'reset', '--hard', 'origin/main'], cwd=cwd, capture_output=True, text=True, timeout=300)
        # 安装依赖（如果有变化）
        r3 = subprocess.run(['pip3', 'install', '-r', 'requirements.txt'], cwd=cwd, capture_output=True, text=True, timeout=300)
        # 重启 Gunicorn
        subprocess.run(['pkill', '-f', 'gunicorn'], capture_output=True, text=True, timeout=300)
        import time
        time.sleep(2)
        subprocess.Popen(['gunicorn', '-c', 'gunicorn_config.py', 'api.app:app'],
                        cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f'更新成功！{r2.stdout}', 200
    except Exception as e:
        return f'更新失败：{str(e)}', 500

# ========== 会员VIP系统（常量从 vip_service 导入）==========


def _get_today():
    return datetime.now().strftime('%Y-%m-%d')


def _safe_parse_datetime(date_str):
    """安全解析日期时间字符串，支持 ISO 格式和其他常见格式"""
    if not date_str:
        return None
    if isinstance(date_str, datetime):
        return date_str
    try:
        return datetime.fromisoformat(date_str)
    except (ValueError, TypeError):
        pass
    # 尝试其他常见格式
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d %H:%M:%S', '%Y/%m/%d'):
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            pass
    return None


def _get_auth_user():
    """获取当前登录用户——优先验证Authorization头，cookie作为fallback"""
    header_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    cookie_token = request.cookies.get('token')

    user_id = None
    # 优先使用前端主动传递的 Authorization 头
    if header_token:
        user_id = verify_token(header_token)
    # 头 token 无效时，尝试 cookie 中的 token
    if not user_id and cookie_token:
        user_id = verify_token(cookie_token)

    if not user_id:
        return None
    users = load_users()
    for u in users:
        if u['id'] == user_id:
            return u, users
    return None


def _ensure_vip_fields(user):
    """确保用户有VIP字段"""
    defaults = {
        'vip_level': 'free',
        'vip_expire': None,
        'ad_watch_count': 0,
        'ad_watch_date': '',
        'total_ad_count': 0,
        'points': 0,
        'last_checkin': '',
        'checkin_streak': 0,
        'wheel_spins_today': 0,
        'wheel_date': '',
        'last_login_reward_date': '',
        'bottom_ad_count': 0,
        'bottom_ad_date': ''
    }
    for k, v in defaults.items():
        if k not in user:
            user[k] = v
    return user


def _ensure_realname_fields(user):
    """确保用户有实名字段"""
    defaults = {
        'real_name': '',
        'id_number_hash': '',
        'id_last4': '',
        'id_verified': False,
        'id_region': '',
        'id_region_code': '',
        'verify_time': '',
        'idcard_image': '',      # 兼容旧字段
        'idcard_image_front': '',
        'idcard_image_back': '',
        'idcard_upload_time': ''
    }
    for k, v in defaults.items():
        if k not in user:
            user[k] = v
    return user


def _ensure_tutorial_field(user):
    """确保用户有新手教程标记字段"""
    if 'tutorial_shown' not in user:
        user['tutorial_shown'] = False
    return user


def _ensure_linked_accounts(user):
    """确保用户有第三方账号绑定字段"""
    if 'linked_accounts' not in user:
        user['linked_accounts'] = {}
    return user


# ========== 会员VIP系统（委托给 VipService）==========


@bp.route('/api/upload-file', methods=['POST'])
def upload_file():
    """接收上传文件并保存到 downloads 目录"""
    import hmac as _hmac
    token = request.headers.get('X-Upload-Token', '')
    if not _hmac.compare_digest(token, 'xuanji_upload_2026'):
        return jsonify({'success': False, 'message': '未授权'}), 403
    fname = request.headers.get('X-Filename', '')
    if not fname:
        return jsonify({'success': False, 'message': '缺少文件名'}), 400
    os.makedirs(_DOWNLOAD_CACHE_DIR, exist_ok=True)
    dest = os.path.join(_DOWNLOAD_CACHE_DIR, fname)
    with open(dest, 'wb') as f:
        f.write(request.get_data())
    return jsonify({'success': True, 'filename': fname, 'size': os.path.getsize(dest)})

# ===== WSGI 支持（PythonAnywhere 部署）=====
# 添加 application 对象（WSGI 标准）
