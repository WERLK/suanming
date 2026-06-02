import os
import sys

# Fix Python path for gunicorn compatibility (can start from any directory)
api_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(api_dir)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from flask import Flask, request, jsonify, session, make_response, send_from_directory, Response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import hashlib
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
from datetime import datetime, timedelta
import jwt
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import threading
import time
import fcntl

from api.vip_service import VipService, VIP_LEVELS, AD_REWARD_HOURS, BONUS_AD_THRESHOLD, BONUS_MIN_HOURS, BONUS_MAX_HOURS
from api.oauth import get_provider, get_enabled_providers, create_oauth_state, verify_oauth_state, _generate_oauth_username

app = Flask(__name__, static_folder='../', static_url_path='')
app.secret_key = os.environ.get('JWT_SECRET', 'xuanji_fortune_secret_key_2026!!')
CORS(app)

# API 请求限流（防止暴力破解和 API 滥用）
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute"],  # 默认：每个 IP 每分钟 100 次请求
    storage_uri="memory://",  # 使用内存存储（生产环境建议使用 Redis）
)

# 用户数据存储文件（使用绝对路径）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
TOKENS_FILE = os.path.join(DATA_DIR, 'tokens.json')
CAPTCHA_FILE = os.path.join(DATA_DIR, 'captcha_store.json')

# ========== 验证码文件存储（支持多 worker / 多进程共享） ==========
_captcha_lock = threading.Lock()

def _load_captcha_store():
    if not os.path.exists(CAPTCHA_FILE):return {}
    try:
        with open(CAPTCHA_FILE,'r') as f:
            fcntl.flock(f.fileno(),fcntl.LOCK_SH)
            try:return json.load(f)
            finally:fcntl.flock(f.fileno(),fcntl.LOCK_UN)
    except:return {}
def _save_captcha_store(store):
    now=datetime.now().isoformat()
    store={k:v for k,v in store.items() if v.get('expire_time','')>now}
    fd=os.open(CAPTCHA_FILE,os.O_CREAT|os.O_WRONLY|os.O_TRUNC,0o644)
    try:
        fcntl.flock(fd,fcntl.LOCK_EX)
        os.write(fd,json.dumps(store,ensure_ascii=False).encode())
    finally:
        fcntl.flock(fd,fcntl.LOCK_UN)
        os.close(fd)
def _get_captcha_entry(captcha_id):
    """获取单个验证码条目"""
    store = _load_captcha_store()
    if captcha_id not in store:
        return None
    entry = store[captcha_id]
    if datetime.now().isoformat() > entry.get('expire_time', ''):
        del store[captcha_id]
        _save_captcha_store(store)
        return None
    return entry

def _set_captcha_entry(captcha_id, entry):
    """设置验证码条目"""
    store = _load_captcha_store()
    store[captcha_id] = entry
    _save_captcha_store(store)

def _delete_captcha_entry(captcha_id):
    """删除验证码条目"""
    store = _load_captcha_store()
    if captcha_id in store:
        del store[captcha_id]
        _save_captcha_store(store)

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# 初始化用户数据文件
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)

if not os.path.exists(TOKENS_FILE):
    with open(TOKENS_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

# ========== 随机昵称和头像生成 ==========

# 随机昵称词库（玄学主题）
_NICKNAME_FIRST = [
    '灵', '玄', '智', '慧', '明', '静', '清', '远', '妙', '神',
    '道', '仙', '易', '天', '紫', '碧', '丹', '鹤', '金', '玉',
    '太', '无', '真', '素', '逸', '观', '通', '空', '微', '至',
    '云', '风', '月', '星', '梦', '尘', '雪', '雨', '霜', '露'
]
_NICKNAME_SECOND = [
    '机', '心', '镜', '光', '空', '云', '风', '月', '星', '辰',
    '梦', '尘', '水', '山', '雪', '雾', '雨', '烟', '火', '雷',
    '阳', '阴', '气', '数', '道', '缘', '法', '术', '门', '子',
    '客', '人', '君', '生', '华', '音', '羽', '林', '松', '鹤'
]
# 预设头像池（与前端avatar picker一致）
_PRESET_AVATARS = [
    '🔮', '🎴', '☯️', '🐉', '⭐', '🌙', '🀄', '🧙', '🦊', '🌸',
    '👤', '👨', '👩', '🧑', '🤵', '👸', '🧚', '🧛', '🧝', '🧞',
    '🐱', '🐶', '🐼', '🐨', '🐰', '🐯', '🐸', '🐵', '🐤', '🦁',
    '💎', '🎯', '🍀', '🌞', '🕊️', '🔥', '💜', '🏆', '🎭', '🌈'
]

def generate_random_nickname():
    """生成随机玄学主题中文昵称，格式：前缀+后缀+数字"""
    first = random.choice(_NICKNAME_FIRST)
    second = random.choice(_NICKNAME_SECOND)
    number = str(random.randint(10, 999))
    return f"{first}{second}{number}"

def generate_random_avatar():
    """随机选择一个预设头像"""
    return random.choice(_PRESET_AVATARS)

# 密码加密
def hash_password(password, salt=None):
    if salt is None:
        salt = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return f"{salt}${password_hash}"

def verify_password(password, hashed):
    salt, _ = hashed.split('$')
    return hash_password(password, salt) == hashed

# 生成JWT token
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    token = jwt.encode(payload, app.secret_key, algorithm='HS256')
    return token

# 验证JWT token
def verify_token(token):
    try:
        payload = jwt.decode(token, app.secret_key, algorithms=['HS256'])
        return payload['user_id']
    except Exception:
        return None

# 读取用户数据（带文件锁，防止多worker竞态条件）
def load_users():
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)  # 共享锁
        try:
            data = json.load(f)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        return data

# 保存用户数据（带文件锁，防止多worker竞态条件导致数据丢失）
def save_users(users):
    with open(USERS_FILE, 'r+', encoding='utf-8') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # 排他锁
        try:
            f.seek(0)
            f.truncate()
            json.dump(users, f, ensure_ascii=False, indent=2)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

# 发送邮件（用于密码重置）
# SMTP 配置优先级：环境变量 > mail_config.json > 演示模式

def _get_mail_config():
    """获取邮件配置，优先从环境变量读取"""
    config = {
        'smtp_server': os.environ.get('SMTP_SERVER', ''),
        'smtp_port': int(os.environ.get('SMTP_PORT', '0') or '0'),
        'sender_email': os.environ.get('SMTP_EMAIL', ''),
        'sender_password': os.environ.get('SMTP_PASSWORD', ''),
    }
    if config['smtp_server'] and config['sender_email'] and config['sender_password']:
        if not config['smtp_port']:
            config['smtp_port'] = 587
        return config

    # 尝试从配置文件读取
    mail_config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mail_config.json')
    if os.path.exists(mail_config_file):
        try:
            with open(mail_config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            server = data.get('smtp_server', '')
            email = data.get('sender_email', '')
            pwd = data.get('sender_password', '')
            port = int(data.get('smtp_port', '587'))
            if server and email and pwd and 'YOUR_' not in pwd:
                return {'smtp_server': server, 'smtp_port': port, 'sender_email': email, 'sender_password': pwd}
        except Exception:
            pass
    return None

def send_email(to_email, subject, body):
    """发送邮件（自动根据配置选择真实发送或演示模式）"""
    mail_config = _get_mail_config()
    if mail_config is None:
        print(f"【演示模式】未配置SMTP，邮件内容:\n  收件人: {to_email}\n  主题: {subject}")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = mail_config['sender_email']
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        server = smtplib.SMTP(mail_config['smtp_server'], mail_config['smtp_port'])
        server.starttls()
        server.login(mail_config['sender_email'], mail_config['sender_password'])
        server.send_message(msg)
        server.quit()
        print(f"邮件发送成功: {to_email}")
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False

# ========== 健康检查 ==========
@app.route('/api/health')
def health_check():
    """健康检查端点"""
    try:
        # 检查数据库连接（这里使用文件检查代替）
        import os
        users_file_exists = os.path.exists(USERS_FILE)
        
        # 读取版本信息
        version_info = {'version': '1.0.0'}
        version_file = os.path.join(BASE_DIR, '..', 'version.json')
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
@app.route('/api/version')
def get_version():
    """获取版本信息"""
    try:
        import os
        version_file = os.path.join(BASE_DIR, '..', 'version.json')
        
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
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@app.route('/')
def index():
    return send_from_directory(PROJECT_ROOT, 'index.html')

@app.route('/<path:filename>')
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
        app.logger.error(f'静态文件服务错误: {filename} - {str(e)}')
        return f'Internal Server Error: {str(e)}', 500

# 专用视频服务端点（绕过静态文件路由的潜在问题）
@app.route('/video/guide-intro.mp4')
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
        app.logger.error(f'视频服务错误: {str(e)}')
        return f'Video serve error: {str(e)}', 500

@app.route('/video/guide-poster.jpg')
def serve_guide_poster():
    """服务教程视频封面"""
    import os.path
    poster_path = os.path.join(PROJECT_ROOT, 'static', 'videos', 'guide-poster.jpg')
    if not os.path.isfile(poster_path):
        return 'Poster not found', 404
    try:
        return send_from_directory(os.path.dirname(poster_path), os.path.basename(poster_path), mimetype='image/jpeg')
    except Exception as e:
        app.logger.error(f'封面服务错误: {str(e)}')
        return f'Poster serve error: {str(e)}', 500

# ========== API路由 ==========

@app.route('/api/captcha/generate', methods=['GET'])
def generate_captcha():
    """生成图片验证码"""
    try:
        captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        width, height = 120, 40
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        for _ in range(100):
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
            draw.point((x, y), fill=color)
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
        except (OSError, IOError):
            font = ImageFont.load_default()
        for i, char in enumerate(captcha_text):
            color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
            x = 10 + i * 25 + random.randint(-3, 3)
            y = random.randint(5, 15)
            draw.text((x, y), char, font=font, fill=color)
        for _ in range(3):
            x1, y1 = random.randint(0, width), random.randint(0, height)
            x2, y2 = random.randint(0, width), random.randint(0, height)
            draw.line([(x1, y1), (x2, y2)], fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), width=2)
        img_io = io.BytesIO()
        image.save(img_io, 'PNG')
        img_io.seek(0)
        captcha_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        _set_captcha_entry(captcha_id, {
            'type': 'image',
            'text': captcha_text,
            'expire_time': (datetime.now() + timedelta(minutes=5)).isoformat()
        })
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        return jsonify({
            'success': True,
            'captcha_id': captcha_id,
            'captcha_image': f"data:image/png;base64,{img_base64}"
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成验证码失败: {str(e)}'}), 500

@app.route('/api/captcha/verify', methods=['POST'])
def verify_captcha():
    """验证图片验证码"""
    try:
        data = request.get_json()
        captcha_id = data.get('captcha_id', '')
        captcha_text = data.get('captcha_text', '').strip().upper()
        if not captcha_id or not captcha_text:
            return jsonify({'success': False, 'message': '参数不完整'}), 200
        entry = _get_captcha_entry(captcha_id)
        if not entry or entry.get('type') != 'image':
            return jsonify({'success': False, 'message': '验证码已失效，请刷新'}), 200
        if entry['text'] != captcha_text:
            return jsonify({'success': False, 'message': '验证码错误'}), 200
        _delete_captcha_entry(captcha_id)
        return jsonify({'success': True, 'message': '验证成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'验证验证码失败: {str(e)}'}), 500

@app.route('/api/slider/generate', methods=['GET'])
def generate_slider():
    """生成滑块验证码"""
    try:
        target_x = random.randint(20, 80)
        target_y = random.randint(30, 70)
        slider_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        _set_captcha_entry(slider_id, {
            'type': 'slider',
            'target_x': target_x,
            'target_y': target_y,
            'expire_time': (datetime.now() + timedelta(minutes=5)).isoformat()
        })
        return jsonify({
            'success': True,
            'slider_id': slider_id,
            'target_x': target_x,
            'image_width': 300,
            'image_height': 150
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'生成滑块验证码失败: {str(e)}'}), 500

@app.route('/api/slider/verify', methods=['POST'])
def verify_slider():
    """验证滑块验证码"""
    try:
        data = request.get_json()
        slider_id = data.get('slider_id', '')
        slider_x = data.get('slider_x', 0)
        if not slider_id or slider_x is None:
            return jsonify({'success': False, 'message': '参数不完整'}), 200
        entry = _get_captcha_entry(slider_id)
        if not entry or entry.get('type') != 'slider':
            return jsonify({'success': False, 'message': '滑块验证码已失效，请刷新'}), 200
        target_x = entry['target_x']
        if abs(slider_x - target_x) <= 5:
            _delete_captcha_entry(slider_id)
            return jsonify({'success': True, 'message': '验证成功'}), 200
        else:
            return jsonify({'success': False, 'message': '请再试一次'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'验证滑块验证码失败: {str(e)}'}), 500

# ========== 短信验证码 ==========

@limiter.limit("3 per minute")
@app.route('/api/sms/send', methods=['POST'])
def send_sms():
    """发送短信验证码（阿里云）"""
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()
        if not phone or not phone.isdigit() or len(phone) != 11:
            return jsonify({'success': False, 'message': '请输入正确的手机号'}), 200
        
        # 生成验证码
        sms_code = ''.join(random.choices(string.digits, k=6))
        sms_id = 'sms_' + ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        
        # 尝试通过阿里云发送短信
        aliyun_sent = False
        aliyun_error = ''
        try:
            from api.sms_extension import send_aliyun_sms
            success, msg = send_aliyun_sms(phone, sms_code)
            if success:
                aliyun_sent = True
            else:
                aliyun_error = msg
        except ImportError as e:
            aliyun_error = f'SDK未安装: {e}'
        except Exception as e:
            aliyun_error = f'异常: {e}'
        
        # 如果阿里云发送失败，回退演示模式
        if not aliyun_sent:
            print(f"【短信】阿里云发送失败: {aliyun_error}, 回退演示模式: phone={phone}, code={sms_code}")
        else:
            print(f"【短信】阿里云发送成功: phone={phone}")
        
        # 存储验证码（文件存储，支持多worker）
        _set_captcha_entry(sms_id, {
            'type': 'sms',
            'phone': phone,
            'code': sms_code,
            'expire_time': (datetime.now() + timedelta(minutes=5)).isoformat(),
            'used': False
        })
        
        return jsonify({
            'success': True,
            'message': '验证码已发送' if aliyun_sent else '验证码已发送（演示模式）',
            'sms_id': sms_id,
            'code': sms_code if not aliyun_sent else None
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'发送失败: {str(e)}'}), 500

@limiter.limit("5 per minute")
@app.route('/api/sms/verify', methods=['POST'])
def verify_sms():
    """验证短信验证码"""
    try:
        data = request.get_json()
        sms_id = data.get('sms_id', '')
        code = data.get('code', '').strip()
        if not sms_id or not code:
            return jsonify({'success': False, 'message': '参数不完整'}), 200
        entry = _get_captcha_entry(sms_id)
        if not entry or entry.get('type') != 'sms':
            return jsonify({'success': False, 'message': '验证码已失效，请重新获取'}), 200
        if entry.get('used'):
            return jsonify({'success': False, 'message': '验证码已使用，请重新获取'}), 200
        if entry['code'] != code:
            return jsonify({'success': False, 'message': '验证码错误'}), 200
        # 标记已使用（一次性）
        entry['used'] = True
        _set_captcha_entry(sms_id, entry)
        return jsonify({'success': True, 'message': '验证成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'验证失败: {str(e)}'}), 500

@limiter.limit("5 per minute")  # 注册限制：每分钟 5 次
@app.route('/api/register', methods=['POST'])
def register():
    """用户注册（支持头像选择：预设emoji 或 自定义上传）"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        avatar_type = data.get('avatar_type', 'emoji')  # emoji | custom
        avatar_preset = data.get('avatar_preset', '')    # emoji字符
        avatar_data = data.get('avatar_data', '')        # base64 custom image

        if not username or len(username) < 3 or len(username) > 20:
            return jsonify({'success': False, 'message': '用户名长度应为3-20个字符'}), 400
        if not password or len(password) < 6:
            return jsonify({'success': False, 'message': '密码长度至少6个字符'}), 400
        if not username.isalnum() and '_' not in username:
            return jsonify({'success': False, 'message': '用户名只能包含字母、数字和下划线'}), 400
        users = load_users()
        if any(u['username'] == username for u in users):
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        if email and any(u.get('email') == email for u in users):
            return jsonify({'success': False, 'message': '邮箱已注册'}), 400
        if phone and any(u.get('phone') == phone for u in users):
            return jsonify({'success': False, 'message': '手机号已注册'}), 400

        # 处理头像
        if avatar_type == 'custom' and avatar_data:
            # 自定义头像：先创建用户获取ID，再保存头像文件
            pass  # 延迟处理，需要先有 user_id
            avatar_preset = ''  # 自定义头像时清空预设
        elif avatar_type == 'emoji' and avatar_preset:
            # 用户选择了特定emoji
            pass
        else:
            # 未选择，随机分配
            avatar_type = 'emoji'
            avatar_preset = generate_random_avatar()

        new_user = {
            'id': 'user_' + ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
            'username': username,
            'nickname': generate_random_nickname(),
            'password': hash_password(password),
            'email': email,
            'phone': phone,
            'avatar': '',
            'avatar_type': avatar_type,
            'avatar_preset': avatar_preset,
            'birthday': '',
            'gender': '',
            'create_time': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat(),
            'status': 'active',
            'vip_level': 'basic',
            'vip_expire': None,
            'ad_watch_count': 0,
            'ad_watch_date': '',
            'tutorial_shown': False,
            'linked_accounts': {}
        }

        # 处理自定义头像上传
        if avatar_type == 'custom' and avatar_data:
            try:
                from api.avatar_audit import AvatarAuditor
                audit_result = AvatarAuditor.audit_avatar(avatar_data)

                if audit_result['result'] == 'block':
                    return jsonify({
                        'success': False, 'message': f'头像审核未通过：{audit_result["reason"]}'
                    }), 400

                # 解码并保存头像
                clean_data = avatar_data
                if 'base64,' in clean_data:
                    clean_data = clean_data.split('base64,')[1]

                image_bytes = base64.b64decode(clean_data)
                avatar_bytes = AvatarAuditor.resize_avatar(image_bytes, size=(200, 200))

                avatar_filename = f"{new_user['id']}_{int(datetime.now().timestamp())}.jpg"
                avatar_path = os.path.join(AVATAR_SAVE_DIR, avatar_filename)

                with open(avatar_path, 'wb') as f:
                    f.write(avatar_bytes)

                new_user['avatar'] = f'/static/avatars/{avatar_filename}'
            except Exception as ave:
                import traceback
                print(f'[Register Avatar Error] {traceback.format_exc()}', flush=True)
                # 头像保存失败不影响注册，使用随机emoji兜底
                new_user['avatar_type'] = 'emoji'
                new_user['avatar_preset'] = generate_random_avatar()
                new_user['avatar'] = ''

        users.append(new_user)
        save_users(users)

        # 记录注册事件到分析数据库
        try:
            snapshot_user(user_id=new_user['id'], username=username,
                         gender='', birth_str='', vip_level='basic', is_new=True)
            from api.analytics_db import track_session as _ts2
            _ts2(user_id=new_user['id'], event_type='signup', page='/api/register',
                 client_ip=request.remote_addr or '')
        except: pass

        token = generate_token(new_user['id'])
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': new_user['id'],
                'username': new_user['username'],
                'nickname': new_user['nickname'],
                'avatar_type': new_user['avatar_type'],
                'avatar_preset': new_user['avatar_preset'],
                'avatar': new_user.get('avatar', ''),
                'tutorial_shown': False
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'}), 500

@limiter.limit("5 per minute")  # 登录限制：每分钟 5 次
@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        remember = data.get('remember', False)
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
        users = load_users()
        user = None
        for u in users:
            if u['username'] == username or u.get('email') == username or u.get('phone') == username:
                user = u
                break
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 200
        if not verify_password(password, user['password']):
            return jsonify({'success': False, 'message': '密码错误'}), 200
        if user.get('status') != 'active':
            return jsonify({'success': False, 'message': '账户已被禁用'}), 200

        # 每日登录自动发放随机 VIP 时长
        _ensure_vip_fields(user)
        _ensure_tutorial_field(user)
        _ensure_linked_accounts(user)
        today = _get_today()
        login_reward_given = False
        login_reward_hours = 0
        if user.get('last_login_reward_date', '') != today:
            now = datetime.now()
            vip_expire = user.get('vip_expire')
            if vip_expire:
                expire_dt = _safe_parse_datetime(vip_expire)
                if expire_dt is None:
                    expire_dt = now
                elif expire_dt < now:
                    expire_dt = now
            else:
                expire_dt = now
            login_reward_hours = random.randint(1, 6)
            new_expire = expire_dt + timedelta(hours=login_reward_hours)
            user['vip_expire'] = new_expire.isoformat()
            user['vip_level'] = 'basic'
            user['last_login_reward_date'] = today
            login_reward_given = True
            # 找到用户索引并保存
            for i, u in enumerate(users):
                if u['id'] == user['id']:
                    users[i] = user
                    break

        user['last_login'] = datetime.now().isoformat()
        save_users(users)

        # 记录登录事件到分析数据库
        try:
            snapshot_user(user_id=user['id'], username=user['username'],
                         gender=user.get('gender', ''), birth_str=user.get('birthday', ''),
                         vip_level=user.get('vip_level', 'basic'))
            from api.analytics_db import track_session as _ts
            _ts(user_id=user['id'], event_type='login', page='/api/login',
                client_ip=request.remote_addr or '')
        except: pass

        token = generate_token(user['id'])
        response = jsonify({
            'success': True,
            'token': token,
            'login_reward': login_reward_given,
            'reward_hours': login_reward_hours,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'nickname': user.get('nickname', user['username']),
                'avatar_type': user.get('avatar_type', ''),
                'avatar_preset': user.get('avatar_preset', ''),
                'tutorial_shown': user.get('tutorial_shown', False)
            }
        })
        if remember:
            response.set_cookie('token', token, max_age=7*24*3600, httponly=True)
        else:
            response.set_cookie('token', token, httponly=True)
        return response, 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """用户登出"""
    response = jsonify({'success': True, 'message': '登出成功'})
    response.delete_cookie('token')
    return response, 200

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """获取用户信息"""
    try:
        token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效或已过期'}), 401
        users = load_users()
        user = None
        for u in users:
            if u['id'] == user_id:
                user = u
                break
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        # 懒初始化：已有用户未设置昵称/头像时自动分配
        need_save = False
        if not user.get('nickname'):
            user['nickname'] = generate_random_nickname()
            need_save = True
        # 仅在 avatar_type 完全缺失时初始化（自定义头像的 preset 为空字符串，不应被覆盖）
        if not user.get('avatar_type'):
            user['avatar_type'] = 'emoji'
            user['avatar_preset'] = generate_random_avatar()
            need_save = True
        _ensure_tutorial_field(user)
        _ensure_linked_accounts(user)
        if need_save:
            for i, u in enumerate(users):
                if u['id'] == user['id']:
                    users[i] = user
                    break
            save_users(users)
        user_info = {
            'id': user['id'],
            'username': user['username'],
            'nickname': user.get('nickname', user['username']),
            'email': user.get('email', ''),
            'phone': user.get('phone', ''),
            'avatar': user.get('avatar', ''),
            'avatar_type': user.get('avatar_type', ''),
            'avatar_preset': user.get('avatar_preset', ''),
            'birthday': user.get('birthday', ''),
            'gender': user.get('gender', ''),
            'create_time': user.get('create_time', ''),
            'last_login': user.get('last_login', ''),
            'vip_level': user.get('vip_level', 'free'),
            'vip_expire': user.get('vip_expire', None),
            'ad_watch_count': user.get('ad_watch_count', 0),
            # 实名认证
            'id_verified': user.get('id_verified', False),
            'id_region': user.get('id_region', ''),
            'real_name': user.get('real_name', ''),
            'id_last4': user.get('id_last4', ''),
            'verify_time': user.get('verify_time', ''),
            'idcard_image': user.get('idcard_image', ''),  # 兼容旧字段
            'idcard_image_front': user.get('idcard_image_front', ''),
            'idcard_image_back': user.get('idcard_image_back', ''),
            'idcard_upload_time': user.get('idcard_upload_time', ''),
            'tutorial_shown': user.get('tutorial_shown', True)
        }
        return jsonify({'success': True, 'user': user_info}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户信息失败: {str(e)}'}), 500

@app.route('/api/profile/tutorial-done', methods=['POST'])
def tutorial_done():
    """标记新手教程已完成（服务端记录，清除浏览器数据也不重复显示）"""
    try:
        token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效或已过期'}), 401
        users = load_users()
        updated = False
        for i, u in enumerate(users):
            if u['id'] == user_id:
                u['tutorial_shown'] = True
                users[i] = u
                updated = True
                break
        if not updated:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        save_users(users)
        return jsonify({'success': True, 'message': '已标记'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500

@app.route('/api/notify-subscribe', methods=['POST'])
def notify_subscribe():
    """App上线通知订阅"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        if not email or '@' not in email:
            return jsonify({'success': False, 'message': '请输入有效的邮箱地址'}), 400

        source = data.get('source', 'website')
        subscribers_file = os.path.join(DATA_DIR, 'app_subscribers.json')
        subscribers = []
        if os.path.exists(subscribers_file):
            with open(subscribers_file, 'r', encoding='utf-8') as f:
                subscribers = json.load(f)

        # 避免重复
        for s in subscribers:
            if s.get('email') == email:
                return jsonify({'success': True, 'message': '您已订阅过，App上线时将通知您'}), 200

        subscribers.append({
            'email': email,
            'source': source,
            'subscribe_time': datetime.now().isoformat(),
            'notified': False
        })

        with open(subscribers_file, 'w', encoding='utf-8') as f:
            json.dump(subscribers, f, ensure_ascii=False, indent=2)

        return jsonify({'success': True, 'message': '订阅成功！App上线时将通知您'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    """更新用户信息"""
    try:
        token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效或已过期'}), 401
        data = request.get_json()
        users = load_users()
        user_index = None
        for i, u in enumerate(users):
            if u['id'] == user_id:
                user_index = i
                break
        if user_index is None:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        allowed_fields = ['username', 'nickname', 'email', 'phone', 'avatar', 'birthday', 'gender']
        for field in allowed_fields:
            if field in data:
                users[user_index][field] = data[field]
        save_users(users)
        user = users[user_index]
        user_info = {
            'id': user['id'],
            'username': user['username'],
            'nickname': user.get('nickname', user['username']),
            'email': user.get('email', ''),
            'phone': user.get('phone', ''),
            'avatar': user.get('avatar', ''),
            'avatar_type': user.get('avatar_type', ''),
            'avatar_preset': user.get('avatar_preset', ''),
            'birthday': user.get('birthday', ''),
            'gender': user.get('gender', '')
        }
        return jsonify({'success': True, 'message': '更新成功', 'user': user_info}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新用户信息失败: {str(e)}'}), 500


@limiter.limit("3 per minute")
@app.route('/api/profile/verify-realname', methods=['POST'])
def verify_realname():
    """实名认证：提交姓名+身份证号+可选身份证照片，本地校验并存储"""
    try:
        token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        data = request.get_json()
        real_name = (data.get('real_name', '') or '').strip()
        id_number = (data.get('id_number', '') or '').strip()
        idcard_image_front = (data.get('idcard_image_front', '') or data.get('idcard_image', '') or '').strip()  # 正面
        idcard_image_back = (data.get('idcard_image_back', '') or '').strip()   # 反面

        if not real_name or len(real_name) < 2:
            return jsonify({'success': False, 'message': '请输入真实姓名'}), 400
        if not id_number:
            return jsonify({'success': False, 'message': '请输入身份证号'}), 400

        # 身份证校验
        from api.idcard import validate_id_card, mask_name, mask_id_last4
        import hashlib

        check = validate_id_card(id_number)
        if not check['valid']:
            return jsonify({'success': False, 'message': check['error']}), 400

        # 查找用户
        users = load_users()
        user_idx = None
        for i, u in enumerate(users):
            if u['id'] == user_id:
                user = u
                user_idx = i
                break
        if user_idx is None:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        # 检查是否已认证
        _ensure_realname_fields(user)
        if user.get('id_verified'):
            # 已认证用户仍可补充上传身份证照片
            updated = False
            if idcard_image_front and not user.get('idcard_image_front'):
                saved_url = _save_idcard_image(user_id, idcard_image_front, 'front')
                if saved_url:
                    user['idcard_image_front'] = saved_url
                    user['idcard_upload_time'] = datetime.now().isoformat()
                    updated = True
            if idcard_image_back and not user.get('idcard_image_back'):
                saved_url = _save_idcard_image(user_id, idcard_image_back, 'back')
                if saved_url:
                    user['idcard_image_back'] = saved_url
                    user['idcard_upload_time'] = datetime.now().isoformat()
                    updated = True
            if updated:
                users[user_idx] = user
                save_users(users)
                front_ok = bool(user.get('idcard_image_front'))
                back_ok = bool(user.get('idcard_image_back'))
                return jsonify({
                    'success': True,
                    'message': f'身份证照片上传成功（正面{"✅" if front_ok else "❌"} 反面{"✅" if back_ok else "❌"}）',
                    'data': {
                        'real_name_masked': mask_name(user.get('real_name', '')),
                        'id_masked': mask_id_last4(user.get('id_last4', '')),
                        'region': user.get('id_region', ''),
                        'verified': True,
                        'idcard_uploaded': front_ok or back_ok,
                        'idcard_image_front': user.get('idcard_image_front', ''),
                        'idcard_image_back': user.get('idcard_image_back', '')
                    }
                }), 200
            return jsonify({'success': False, 'message': '已完成实名认证，无需重复提交或图片格式无效'}), 400

        # 存储认证信息（身份证号只存哈希）
        id_hash = hashlib.sha256(id_number.encode()).hexdigest()
        now = datetime.now().isoformat()
        user['real_name'] = real_name
        user['id_number_hash'] = id_hash
        user['id_last4'] = id_number[-4:]
        user['id_verified'] = True
        user['id_region'] = check['region_name']
        user['id_region_code'] = check['region_code']
        user['verify_time'] = now

        # 处理身份证图片（正反面）
        idcard_uploaded_front = False
        idcard_uploaded_back = False
        if idcard_image_front:
            saved_url = _save_idcard_image(user_id, idcard_image_front, 'front')
            if saved_url:
                user['idcard_image_front'] = saved_url
                user['idcard_upload_time'] = now
                idcard_uploaded_front = True
        if idcard_image_back:
            saved_url = _save_idcard_image(user_id, idcard_image_back, 'back')
            if saved_url:
                user['idcard_image_back'] = saved_url
                user['idcard_upload_time'] = now
                idcard_uploaded_back = True

        # 如果用户生日/性别为空则自动填充
        if not user.get('birthday') and check['birth_date']:
            user['birthday'] = check['birth_date']
        if not user.get('gender') and check['gender']:
            user['gender'] = 'male' if check['gender'] == 'male' else 'female'

        users[user_idx] = user
        save_users(users)

        # 更新分析数据库
        try:
            from api.analytics_db import snapshot_user
            snapshot_user(user_id=user_id, username=user['username'],
                         gender=user.get('gender', ''), birth_str=user.get('birthday', ''),
                         vip_level=user.get('vip_level', 'basic'),
                         id_region=user.get('id_region', ''), is_verified=True,
                         has_idcard_image=(idcard_uploaded_front or idcard_uploaded_back))
        except: pass

        parts = []
        if idcard_uploaded_front: parts.append('正面已上传')
        if idcard_uploaded_back: parts.append('反面已上传')
        upload_msg = '，'.join(parts) if parts else ''

        return jsonify({
            'success': True,
            'message': '实名认证成功' + ('（' + upload_msg + '）' if upload_msg else ''),
            'data': {
                'real_name_masked': mask_name(real_name),
                'id_masked': mask_id_last4(id_number),
                'region': check['region_name'],
                'gender': check['gender'],
                'birth_date': check['birth_date'],
                'verified': True,
                'idcard_uploaded': (idcard_uploaded_front or idcard_uploaded_back),
                'idcard_image_front': user.get('idcard_image_front', ''),
                'idcard_image_back': user.get('idcard_image_back', '')
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'认证失败: {str(e)}'}), 500


@app.route('/api/profile/realname-status', methods=['GET'])
def realname_status():
    """查询实名认证状态"""
    try:
        token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        users = load_users()
        user = next((u for u in users if u['id'] == user_id), None)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        _ensure_realname_fields(user)
        from api.idcard import mask_name, mask_id_last4

        if user.get('id_verified'):
            return jsonify({
                'success': True,
                'verified': True,
                'data': {
                    'real_name_masked': mask_name(user.get('real_name', '')),
                    'id_masked': mask_id_last4(user.get('id_last4', '')),
                    'region': user.get('id_region', ''),
                    'verify_time': user.get('verify_time', ''),
                    'idcard_image_front': user.get('idcard_image_front', ''),
                    'idcard_image_back': user.get('idcard_image_back', ''),
                    'idcard_upload_time': user.get('idcard_upload_time', '')
                }
            }), 200
        else:
            return jsonify({'success': True, 'verified': False, 'message': '未认证'}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/profile/upload-idcard', methods=['POST'])
def upload_idcard():
    """单独上传身份证照片（已认证用户补充上传，支持正反面）"""
    try:
        token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        data = request.get_json()
        idcard_image_front = (data.get('idcard_image_front', '') or data.get('idcard_image', '') or '').strip()
        idcard_image_back = (data.get('idcard_image_back', '') or '').strip()

        if not idcard_image_front and not idcard_image_back:
            return jsonify({'success': False, 'message': '请上传身份证照片（正面或反面）'}), 400

        users = load_users()
        user_idx = None
        for i, u in enumerate(users):
            if u['id'] == user_id:
                user = u
                user_idx = i
                break
        if user_idx is None:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        _ensure_realname_fields(user)

        saved_front = None
        saved_back = None
        if idcard_image_front:
            saved_front = _save_idcard_image(user_id, idcard_image_front, 'front')
        if idcard_image_back:
            saved_back = _save_idcard_image(user_id, idcard_image_back, 'back')

        if not saved_front and not saved_back:
            return jsonify({'success': False, 'message': '图片格式无效或超过10MB'}), 400

        now = datetime.now().isoformat()
        if saved_front:
            user['idcard_image_front'] = saved_front
        if saved_back:
            user['idcard_image_back'] = saved_back
        user['idcard_upload_time'] = now
        users[user_idx] = user
        save_users(users)

        return jsonify({
            'success': True,
            'message': '身份证照片上传成功',
            'data': {
                'idcard_image_front': user.get('idcard_image_front', ''),
                'idcard_image_back': user.get('idcard_image_back', ''),
                'idcard_upload_time': now
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@limiter.limit("3 per minute")  # 忘记密码限制：每分钟 3 次
@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """忘记密码 - 发送重置邮件"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        if not email:
            return jsonify({'success': False, 'message': '邮箱不能为空'}), 400
        users = load_users()
        user = None
        for u in users:
            if u.get('email') == email:
                user = u
                break
        if not user:
            return jsonify({'success': False, 'message': '邮箱未注册'}), 404
        reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
        with open(TOKENS_FILE, 'r', encoding='utf-8') as f:
            tokens = json.load(f)
        tokens[reset_token] = {
            'user_id': user['id'],
            'expire_time': (datetime.now() + timedelta(hours=1)).isoformat()
        }
        with open(TOKENS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tokens, f, ensure_ascii=False, indent=2)
        reset_link = f"{request.host_url.rstrip('/')}/reset-password.html?token={reset_token}"
        email_body = f"""
        <h2>重置密码</h2>
        <p>请点击以下链接重置您的密码（1小时内有效）：</p>
        <a href="{reset_link}">{reset_link}</a>
        <p>如果您没有请求重置密码，请忽略此邮件。</p>
        """

        # 尝试发送真实邮件
        email_sent = send_email(email, '密码重置 - 玄机算命网', email_body)

        if email_sent:
            return jsonify({
                'success': True, 'message': '重置链接已发送到您的邮箱，请注意查收',
            }), 200
        else:
            return jsonify({
                'success': True, 'message': '重置链接已生成（邮件服务未配置，请使用以下链接）',
                'reset_link': reset_link
            }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'发送重置邮件失败: {str(e)}'}), 500

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    """重置密码"""
    try:
        data = request.get_json()
        token = data.get('token', '')
        new_password = data.get('password', '')
        if not token or not new_password:
            return jsonify({'success': False, 'message': '参数不完整'}), 400
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': '密码长度至少6个字符'}), 400
        with open(TOKENS_FILE, 'r', encoding='utf-8') as f:
            tokens = json.load(f)
        if token not in tokens:
            return jsonify({'success': False, 'message': '重置链接无效'}), 400
        token_data = tokens[token]
        expire_time = datetime.fromisoformat(token_data['expire_time'])
        if datetime.now() > expire_time:
            del tokens[token]
            with open(TOKENS_FILE, 'w', encoding='utf-8') as f:
                json.dump(tokens, f, ensure_ascii=False, indent=2)
            return jsonify({'success': False, 'message': '重置链接已过期'}), 400
        users = load_users()
        user_index = None
        for i, u in enumerate(users):
            if u['id'] == token_data['user_id']:
                user_index = i
                break
        if user_index is None:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        users[user_index]['password'] = hash_password(new_password)
        save_users(users)
        del tokens[token]
        with open(TOKENS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tokens, f, ensure_ascii=False, indent=2)
        return jsonify({'success': True, 'message': '密码重置成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'重置密码失败: {str(e)}'}), 500

@app.route('/api/wechat-login', methods=['POST'])
def wechat_login():
    """微信登录（已迁移到 OAuth 流程）"""
    return jsonify({'success': False, 'message': '请使用页面上的"微信登录"按钮进行扫码登录'}), 400

@app.route('/api/qq-login', methods=['POST'])
def qq_login():
    """QQ登录（已迁移到 OAuth 流程）"""
    return jsonify({'success': False, 'message': '请使用页面上的"QQ登录"按钮进行授权登录'}), 400


# ========== OAuth 第三方登录 ==========

def _oauth_login_or_register(provider_key, oauth_info):
    """
    OAuth 统一登录/注册逻辑：
    1. 先按 linked_accounts 查找
    2. 再按邮箱匹配（自动合并）
    3. 否则创建新用户
    返回 (user_dict, is_new_user)
    """
    provider_uid = oauth_info['provider_uid']
    email = oauth_info.get('email', '').strip()
    nickname = oauth_info.get('nickname', '')
    avatar = oauth_info.get('avatar', '')

    users = load_users()

    # 1. 查找已绑定的用户
    for u in users:
        u = _ensure_linked_accounts(u)
        if u.get('linked_accounts', {}).get(provider_key) == provider_uid:
            return u, False

    # 2. 邮箱匹配（自动合并）
    if email:
        for u in users:
            if u.get('email', '').strip().lower() == email.lower():
                u = _ensure_linked_accounts(u)
                u['linked_accounts'][provider_key] = provider_uid
                save_users(users)
                return u, False

    # 3. 创建新用户
    uid = 'user_' + ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    username_base = _generate_oauth_username(provider_key, nickname)
    username = username_base
    counter = 1
    while any(u['username'] == username for u in users):
        username = f"{username_base}{counter}"
        counter += 1

    new_user = {
        'id': uid,
        'username': username,
        'nickname': nickname or username,
        'password': '',  # OAuth 用户无密码
        'email': email,
        'phone': '',
        'avatar': avatar,
        'avatar_type': 'custom' if avatar else 'emoji',
        'avatar_preset': '' if avatar else generate_random_avatar(),
        'birthday': '',
        'gender': '',
        'create_time': datetime.now().isoformat(),
        'last_login': datetime.now().isoformat(),
        'status': 'active',
        'vip_level': 'basic',
        'vip_expire': None,
        'ad_watch_count': 0,
        'ad_watch_date': '',
        'tutorial_shown': False,
        'linked_accounts': {provider_key: provider_uid},
    }
    users.append(new_user)
    save_users(users)
    return new_user, True


@app.route('/api/oauth/status', methods=['GET'])
def oauth_status():
    """查询各平台 OAuth 启用状态"""
    return jsonify({'success': True, 'providers': get_enabled_providers()}), 200


@app.route('/api/oauth/<provider>', methods=['GET'])
def oauth_authorize(provider):
    """发起 OAuth 授权：跳转到第三方平台授权页"""
    p = get_provider(provider)
    if not p:
        return jsonify({'success': False, 'message': f'不支持的登录平台: {provider}'}), 400
    if not p.is_enabled:
        return jsonify({'success': False, 'message': f'{p.PROVIDER_NAME}登录暂未开放，敬请期待'}), 400

    state = create_oauth_state()
    auth_url = p.get_authorization_url(state)
    resp = make_response('', 302)
    resp.headers['Location'] = auth_url
    return resp


@app.route('/api/oauth/<provider>/callback', methods=['GET'])
def oauth_callback(provider):
    """OAuth 回调处理：用 code 换 token → 获取用户信息 → 登录/注册 → 跳转首页"""
    p = get_provider(provider)
    if not p:
        return '<h3>不支持的登录平台</h3>', 400
    if not p.is_enabled:
        return f'<h3>{p.PROVIDER_NAME}登录暂未开放</h3>', 400

    # 验证 state（防 CSRF）
    state = request.args.get('state', '')
    if not verify_oauth_state(state):
        return '<script>alert("登录会话已过期，请重新登录");window.location.href="/login.html";</script>'

    # 处理错误（用户拒绝授权等）
    error = request.args.get('error', '')
    error_description = request.args.get('error_description', '')
    if error:
        return f'<script>alert("授权失败: {error_description or error}");window.location.href="/login.html";</script>'

    code = request.args.get('code', '')
    if not code:
        return '<script>alert("授权失败：缺少授权码");window.location.href="/login.html";</script>'

    # 换 token
    token_data = p.exchange_code(code)
    if not token_data:
        return '<script>alert("换取访问令牌失败，请重试");window.location.href="/login.html";</script>'

    # 获取用户信息
    oauth_info = p.get_user_info(token_data)
    if not oauth_info:
        return '<script>alert("获取用户信息失败，请重试");window.location.href="/login.html";</script>'

    # 登录或注册
    user, is_new = _oauth_login_or_register(provider, oauth_info)

    # 更新最后登录时间
    users = load_users()
    for i, u in enumerate(users):
        if u['id'] == user['id']:
            users[i]['last_login'] = datetime.now().isoformat()
            break
    save_users(users)

    # 生成 JWT token
    token = generate_token(user['id'])

    # 设置 cookie 并跳转首页
    resp = make_response('', 302)
    resp.headers['Location'] = '/'
    resp.set_cookie('token', token, max_age=7*24*3600, httponly=True, samesite='Lax')
    return resp

# 注册短信验证码路由
try:
    from api.sms_extension import register_sms_routes
    register_sms_routes(app)
    print("短信验证码扩展已加载")
except Exception as e:
    print(f"短信验证码扩展加载失败: {e}")

# 注册算命API蓝图（大数据联网实时分析）
try:
    from api.fortune_routes import fortune_bp
    app.register_blueprint(fortune_bp, url_prefix='/api/fortune')
    print("算命API蓝图已加载（/api/fortune/*）")
except Exception as e:
    print(f"算命API蓝图加载失败: {e}")

# 加载分析数据库
try:
    from api.analytics_db import init_db, track_session, snapshot_user, track_divination, track_vip
    init_db()
    print("分析数据库已加载")
except Exception as e:
    print(f"分析数据库加载失败: {e}")

# ===== 全局请求追踪 =====
@app.before_request
def before_request_track():
    """记录每个请求的页面访问"""
    # 跳过静态资源和视频请求
    path = request.path
    skip_prefixes = ('/static/', '/video/', '/css/', '/js/', '/icon-', '/manifest', '/favicon')
    if any(path.startswith(p) for p in skip_prefixes):
        return
    if request.method == 'GET' and not request.path.startswith('/api/'):
        try:
            page = request.path
            event_type = 'page_view'
            # 识别算命模块页面
            if page.startswith('/modules/'):
                event_type = 'module_view'
            track_session(
                event_type=event_type,
                page=page,
                referrer=request.referrer or '',
                client_ip=request.remote_addr or ''
            )
        except Exception:
            pass

# ===== 算命事件追踪 =====
@app.after_request
def after_request_track(response):
    """自动追踪 fortune/VIP API 请求"""
    path = request.path

    # 追踪算命API
    if path.startswith('/api/fortune/'):
        try:
            parts = path.split('/')
            module_id = parts[3] if len(parts) > 3 else ''
            # 处理子路径如 /api/fortune/xingzuo/daily → module_id = 'xingzuo'
            if module_id and len(parts) > 4 and parts[4]:
                m = parts[3] if parts[3] not in ('tarot',) else parts[3]
                module_id = m
            module_names = {
                'bazi': '八字排盘', 'ziwei': '紫微斗数', 'tarot': '塔罗牌',
                'shengxiao': '生肖运势', 'xingming': '姓名测试', 'xingzuo': '星座运势',
                'heyun': '合婚配对', 'jiemeng': '周公解梦', 'fengshui': '风水堪舆',
                'huangli': '黄道吉日', 'xingzuo': '星座运势', 'liuyao': '六爻占卜',
                'caishen': '财神方位', 'analyze': '智能分析',
                'image-analyze': '智能分析'
            }
            module_name = module_names.get(module_id, module_id)
            token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
            user_id = None
            if token:
                try:
                    uid = verify_token(token)
                    if uid: user_id = uid
                except: pass

            track_divination(
                user_id=user_id,
                module_name=module_name,
                module_id=module_id,
                is_logged_in=bool(user_id),
                client_ip=request.remote_addr or '',
                user_agent=request.headers.get('User-Agent', '')[:200]
            )
        except Exception:
            pass

    # 追踪 VIP 行为
    if path.startswith('/api/vip/'):
        try:
            vip_events = {
                '/api/vip/watch-ad': ('ad_watch', '观看广告'),
                '/api/vip/bottom-ad': ('bottom_ad', '底部广告'),
                '/api/vip/checkin': ('checkin', '每日签到'),
                '/api/vip/wheel': ('wheel', '转盘抽奖'),
            }
            for prefix, (evt, label) in vip_events.items():
                if path == prefix:
                    token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
                    if token:
                        try:
                            uid = verify_token(token)
                            if uid: track_vip(uid, evt, label)
                        except: pass
                    break
        except Exception:
            pass

    return response

# 注册分析API蓝图
try:
    from api.analytics_routes import analytics_bp
    app.register_blueprint(analytics_bp, url_prefix='/api/admin/analytics')
    print("分析API蓝图已加载（/api/admin/analytics/*）")
except Exception as e:
    print(f"分析API蓝图加载失败: {e}")

@app.route('/api/image-analyze', methods=['POST'])
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

# ========== 柠盟广告健康检查 ==========
# 服务器在国内，可准确检测柠盟链接是否可用
_AD_HEALTH_CACHE = {'alive': None, 'ts': 0}
_AD_HEALTH_TTL = 300  # 缓存 5 分钟
_AD_CHECK_LINKS = [
    'http://www.huyis.com/link?1185',
    'http://www.huyis.com/link?1186'
]

@app.route('/api/ad-health')
def ad_health_check():
    """检测柠盟广告链接是否可用（由前端 ads.js 调用）"""
    now = time.time()
    if now - _AD_HEALTH_CACHE['ts'] < _AD_HEALTH_TTL:
        return jsonify({'success': True, 'alive': _AD_HEALTH_CACHE['alive']})

    # 检测链接
    alive = False
    for url in _AD_CHECK_LINKS:
        try:
            r = requests.head(url, timeout=5, allow_redirects=True,
                            headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36'})
            # 200-399 视为活着（含重定向）
            if 200 <= r.status_code < 400:
                alive = True
                break
            # 有些广告服务返回 302 也是正常的
        except Exception:
            pass

    _AD_HEALTH_CACHE['alive'] = alive
    _AD_HEALTH_CACHE['ts'] = now
    return jsonify({'success': True, 'alive': alive})

@app.route('/api/download/<platform>')
def download_proxy(platform):
    """代理下载：从 GitHub Release 拉取文件，缓存后返回用户"""
    info = _DOWNLOAD_FILES.get(platform)
    if not info:
        return jsonify({'success': False, 'message': f'不支持的平台: {platform}'}), 404

    os.makedirs(_DOWNLOAD_CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(_DOWNLOAD_CACHE_DIR, info['filename'])

    # 1. 尝试从缓存返回（未过期）
    if os.path.exists(cache_path):
        age = time.time() - os.path.getmtime(cache_path)
        if age < _CACHE_MAX_AGE:
            return _send_file_response(cache_path, info['filename'], info['mime'])

    # 2. 从 GitHub 流式下载（同时写缓存 + 返回用户）
    try:
        resp = requests.get(info['url'], stream=True, timeout=60,
                           headers={'User-Agent': 'XuanjiDownloadProxy/1.0'})
        if resp.status_code == 404:
            return jsonify({'success': False, 'message': '文件尚未构建，请稍后再试'}), 404
        if resp.status_code != 200:
            return jsonify({'success': False, 'message': f'下载失败 (HTTP {resp.status_code})'}), 502

        total_size = resp.headers.get('Content-Length')

        def generate():
            # 边下载边缓存边返回
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
        # GitHub 下载失败，尝试用缓存（即使过期）
        if os.path.exists(cache_path):
            return _send_file_response(cache_path, info['filename'], info['mime'])
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

@app.route('/api/vip/status', methods=['GET'])
def vip_status():
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result
        svc = VipService(USERS_FILE)
        return jsonify(svc.get_status(user, users)), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/vip/watch-ad', methods=['POST'])
def vip_watch_ad():
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result
        svc = VipService(USERS_FILE)
        data, status = svc.watch_ad(user, users, 'personal')
        return jsonify(data), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/vip/bottom-ad', methods=['POST'])
def vip_bottom_ad():
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result
        svc = VipService(USERS_FILE)
        data, status = svc.watch_ad(user, users, 'bottom')
        return jsonify(data), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/vip/checkin', methods=['POST'])
def vip_checkin():
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result
        svc = VipService(USERS_FILE)
        data, status = svc.do_checkin(user, users)
        return jsonify(data), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/vip/redeem', methods=['POST'])
def vip_redeem():
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result
        data_req = request.get_json() or {}
        redeem_type = data_req.get('type', '')
        svc = VipService(USERS_FILE)
        data, status = svc.do_redeem(user, users, redeem_type)
        return jsonify(data), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/vip/wheel', methods=['POST'])
def vip_wheel():
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result
        svc = VipService(USERS_FILE)
        data, status = svc.do_wheel(user, users)
        return jsonify(data), status
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ========== 头像上传（带自动审核）==========
from api.avatar_audit import AvatarAuditor

AVATAR_SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'avatars')
os.makedirs(AVATAR_SAVE_DIR, exist_ok=True)

IDCARD_SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'idcard')
os.makedirs(IDCARD_SAVE_DIR, exist_ok=True)


def _save_idcard_image(user_id, image_data, suffix=''):
    """保存身份证图片（自动缩放），返回URL或None
    
    Args:
        user_id: 用户ID
        image_data: base64图片数据
        suffix: 文件名后缀，如 '_front' / '_back'，用于区分正反面
    """
    try:
        # 移除 base64 前缀
        if 'base64,' in image_data:
            image_data = image_data.split('base64,')[1]
        image_bytes = base64.b64decode(image_data)

        # 限制解码后大小：最大 10MB（压缩前，后续会缩放）
        if len(image_bytes) > 10 * 1024 * 1024:
            return None

        # 用 PIL 缩放身份证图片（保留文字细节，最大宽度 1200px）
        try:
            from PIL import Image
            import io
            img = Image.open(io.BytesIO(image_bytes))
            w, h = img.size
            if w > 1200:
                ratio = 1200.0 / w
                new_w = 1200
                new_h = int(h * ratio)
                img = img.resize((new_w, new_h), Image.LANCZOS)
            # 转 JPEG 保存
            buf = io.BytesIO()
            img_format = img.format or 'JPEG'
            if img_format.upper() == 'PNG' and img.mode in ('RGBA', 'LA', 'P'):
                # PNG 透明通道转白色背景
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            img.save(buf, format='JPEG', quality=85)
            image_bytes = buf.getvalue()
        except Exception:
            pass  # PIL 处理失败则使用原始 bytes

        # 保存图片
        suffix_str = f'_{suffix}' if suffix else ''
        filename = f"{user_id}{suffix_str}_{int(datetime.now().timestamp())}.jpg"
        filepath = os.path.join(IDCARD_SAVE_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(image_bytes)

        return f'/static/idcard/{filename}'
    except Exception:
        return None

@app.route('/api/avatar/upload', methods=['POST'])
def upload_avatar():
    """上传头像（自动审核）"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result
        
        data = request.get_json()
        image_data = data.get('image', '')
        
        if not image_data:
            return jsonify({'success': False, 'message': '请上传图片'}), 400
        
        # 1. 自动审核头像
        audit_result = AvatarAuditor.audit_avatar(image_data)
        
        if audit_result['result'] == 'block':
            return jsonify({
                'success': False, 'message': f'头像审核未通过：{audit_result["reason"]}',
                'audit_result': audit_result
            }), 400
        
        # 2. 审核通过或需复审，处理图片
        # 移除 base64 前缀
        if 'base64,' in image_data:
            image_data = image_data.split('base64,')[1]
        
        image_bytes = base64.b64decode(image_data)
        
        # 3. 缩放头像到标准尺寸
        avatar_bytes = AvatarAuditor.resize_avatar(image_bytes, size=(200, 200))
        
        # 4. 保存头像文件
        avatar_filename = f"{user['id']}_{int(datetime.now().timestamp())}.jpg"
        avatar_path = os.path.join(AVATAR_SAVE_DIR, avatar_filename)
        
        with open(avatar_path, 'wb') as f:
            f.write(avatar_bytes)
        
        # 5. 更新用户头像路径
        avatar_url = f'/static/avatars/{avatar_filename}'
        
        user_index = None
        for i, u in enumerate(users):
            if u['id'] == user['id']:
                user_index = i
                break
        
        if user_index is not None:
            users[user_index]['avatar'] = avatar_url
            save_users(users)
        
        # 6. 返回结果
        response_data = {
            'success': True, 'message': '头像上传成功' if audit_result['result'] == 'pass' else '头像已上传，待人工复审',
            'avatar_url': avatar_url,
            'audit_result': audit_result
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        import traceback
        print(f'[Avatar Upload Error] {traceback.format_exc()}', flush=True)
        return jsonify({'success': False, 'message': f'头像上传失败：{str(e)}'}), 500

@app.route('/api/avatar/set-preset', methods=['POST'])
def set_preset_avatar():
    """设置系统预设头像"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result

        data = request.get_json()
        avatar_type = data.get('type', 'emoji')  # emoji | letter | color
        avatar_value = data.get('value', '')

        if not avatar_value:
            return jsonify({'success': False, 'message': '请选择头像'}), 400

        # 更新用户头像
        user_index = None
        for i, u in enumerate(users):
            if u['id'] == user['id']:
                user_index = i
                break

        if user_index is not None:
            users[user_index]['avatar_type'] = avatar_type
            users[user_index]['avatar_preset'] = avatar_value
            users[user_index]['avatar'] = None  # 清除自定义头像
            save_users(users)

        return jsonify({
            'success': True,
            'message': '头像设置成功',
            'avatar_type': avatar_type,
            'avatar_value': avatar_value
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'头像设置失败：{str(e)}'}), 500

# ========== 收藏功能 ==========
FAVORITES_FILE = os.path.join(DATA_DIR, 'favorites.json')

# 确保收藏文件存在
if not os.path.exists(FAVORITES_FILE):
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """获取用户收藏列表"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            favorites = json.load(f)
        
        user_favorites = favorites.get(user['id'], [])
        
        return jsonify({
            'success': True,
            'favorites': user_favorites
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    """添加收藏"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        data = request.get_json()
        module_id = data.get('module_id', '')
        module_name = data.get('module_name', '')
        
        if not module_id or not module_name:
            return jsonify({'success': False, 'message': '参数不完整'}), 400
        
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            favorites = json.load(f)
        
        if user['id'] not in favorites:
            favorites[user['id']] = []
        
        # 检查是否已收藏
        for item in favorites[user['id']]:
            if item['module_id'] == module_id:
                return jsonify({'success': False, 'message': '已经收藏过了'}), 400
        
        # 添加收藏
        favorites[user['id']].append({
            'module_id': module_id,
            'module_name': module_name,
            'add_time': datetime.now().isoformat()
        })
        
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(favorites, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '收藏成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/favorites', methods=['DELETE'])
def remove_favorite():
    """取消收藏"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        data = request.get_json()
        module_id = data.get('module_id', '')
        
        if not module_id:
            return jsonify({'success': False, 'message': '参数不完整'}), 400
        
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            favorites = json.load(f)
        
        if user['id'] not in favorites:
            return jsonify({'success': False, 'message': '收藏不存在'}), 400
        
        # 移除收藏
        favorites[user['id']] = [item for item in favorites[user['id']] if item['module_id'] != module_id]
        
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(favorites, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '取消收藏成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 分享记录 ==========
SHARES_FILE = os.path.join(DATA_DIR, 'shares.json')

# 确保分享文件存在
if not os.path.exists(SHARES_FILE):
    with open(SHARES_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

@app.route('/api/shares', methods=['GET'])
def get_shares():
    """获取分享记录"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        with open(SHARES_FILE, 'r', encoding='utf-8') as f:
            shares = json.load(f)
        
        user_shares = shares.get(user['id'], [])
        
        return jsonify({
            'success': True,
            'shares': user_shares
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/shares', methods=['POST'])
def add_share():
    """添加分享记录"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        data = request.get_json()
        module_id = data.get('module_id', '')
        module_name = data.get('module_name', '')
        share_platform = data.get('platform', '')  # wechat/weibo/qq/other
        
        with open(SHARES_FILE, 'r', encoding='utf-8') as f:
            shares = json.load(f)
        
        if user['id'] not in shares:
            shares[user['id']] = []
        
        shares[user['id']].append({
            'module_id': module_id,
            'module_name': module_name,
            'platform': share_platform,
            'share_time': datetime.now().isoformat()
        })
        
        with open(SHARES_FILE, 'w', encoding='utf-8') as f:
            json.dump(shares, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '分享记录已保存'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 报告功能 ==========
REPORTS_FILE = os.path.join(DATA_DIR, 'reports.json')

# 确保报告文件存在
if not os.path.exists(REPORTS_FILE):
    with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

@app.route('/api/reports', methods=['GET'])
def get_reports():
    """获取用户报告列表"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
            reports = json.load(f)
        
        user_reports = reports.get(user['id'], [])
        
        return jsonify({
            'success': True,
            'reports': user_reports
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/reports', methods=['POST'])
def save_report():
    """保存算命报告"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        data = request.get_json()
        module_id = data.get('module_id', '')
        module_name = data.get('module_name', '')
        input_data = data.get('input_data', {})
        result_data = data.get('result_data', '')
        
        with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
            reports = json.load(f)
        
        if user['id'] not in reports:
            reports[user['id']] = []
        
        reports[user['id']].append({
            'id': 'report_' + ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
            'module_id': module_id,
            'module_name': module_name,
            'input_data': input_data,
            'result_data': result_data,
            'save_time': datetime.now().isoformat()
        })
        
        with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '报告保存成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/reports/<report_id>', methods=['DELETE'])
def delete_report(report_id):
    """删除报告"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        with open(REPORTS_FILE, 'r', encoding='utf-8') as f:
            reports = json.load(f)
        
        if user['id'] not in reports:
            return jsonify({'success': False, 'message': '报告不存在'}), 400
        
        # 删除报告
        reports[user['id']] = [r for r in reports[user['id']] if r['id'] != report_id]
        
        with open(REPORTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '报告删除成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 占卜历史 ==========
DIVINATION_FILE = os.path.join(DATA_DIR, 'divination_history.json')

if not os.path.exists(DIVINATION_FILE):
    with open(DIVINATION_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

@app.route('/api/divination-history', methods=['GET'])
def get_divination_history():
    """获取用户占卜历史，支持分类/标签/关键词筛选"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        category = request.args.get('category', '').strip()
        tag = request.args.get('tag', '').strip()
        search = request.args.get('search', '').strip()
        
        with open(DIVINATION_FILE, 'r', encoding='utf-8') as f:
            histories = json.load(f)
        
        user_histories = histories.get(user['id'], [])

        # 筛选
        if category:
            user_histories = [h for h in user_histories if h.get('category_id') == category]
        if tag:
            user_histories = [h for h in user_histories if tag in (h.get('tags') or [])]
        if search:
            keyword = search.lower()
            user_histories = [
                h for h in user_histories
                if keyword in (h.get('module_name', '') or '').lower()
                or keyword in (str(h.get('input_data', ''))).lower()
                or keyword in (str(h.get('result_data', ''))).lower()
            ]

        user_histories.sort(key=lambda x: x.get('create_time', ''), reverse=True)
        
        return jsonify({'success': True, 'histories': user_histories}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/divination-history/<history_id>', methods=['GET'])
def get_divination_detail(history_id):
    """获取单个占卜历史详情"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        with open(DIVINATION_FILE, 'r', encoding='utf-8') as f:
            histories = json.load(f)
        
        user_histories = histories.get(user['id'], [])
        for h in user_histories:
            if h['id'] == history_id:
                return jsonify({'success': True, 'history': h}), 200
        
        return jsonify({'success': False, 'message': '记录不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/divination-history/<history_id>', methods=['DELETE'])
def delete_divination_history(history_id):
    """删除占卜历史"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        with open(DIVINATION_FILE, 'r', encoding='utf-8') as f:
            histories = json.load(f)
        
        if user['id'] in histories:
            histories[user['id']] = [h for h in histories[user['id']] if h['id'] != history_id]
            with open(DIVINATION_FILE, 'w', encoding='utf-8') as f:
                json.dump(histories, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '删除成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 通知设置 ==========
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, 'notifications.json')

# 确保通知文件存在
if not os.path.exists(NOTIFICATIONS_FILE):
    with open(NOTIFICATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

@app.route('/api/notifications/settings', methods=['GET'])
def get_notification_settings():
    """获取通知设置"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        with open(NOTIFICATIONS_FILE, 'r', encoding='utf-8') as f:
            notifications = json.load(f)
        
        settings = notifications.get(user['id'], {
            'push_enabled': True,
            'email_enabled': True,
            'sms_enabled': False,
            'daily_fortune': True,
            'vip_expire': True,
            'system_notice': True
        })
        
        return jsonify({
            'success': True,
            'settings': settings
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/notifications/settings', methods=['PUT'])
def update_notification_settings():
    """更新通知设置"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        data = request.get_json()
        
        with open(NOTIFICATIONS_FILE, 'r', encoding='utf-8') as f:
            notifications = json.load(f)
        
        if user['id'] not in notifications:
            notifications[user['id']] = {}
        
        # 更新设置
        notifications[user['id']].update(data)
        
        with open(NOTIFICATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(notifications, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '设置已保存'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 隐私设置 ==========
PRIVACY_FILE = os.path.join(DATA_DIR, 'privacy.json')

# 确保隐私文件存在
if not os.path.exists(PRIVACY_FILE):
    with open(PRIVACY_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

@app.route('/api/privacy/settings', methods=['GET'])
def get_privacy_settings():
    """获取隐私设置"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        with open(PRIVACY_FILE, 'r', encoding='utf-8') as f:
            privacy = json.load(f)
        
        settings = privacy.get(user['id'], {
            'profile_public': True,
            'fortune_public': False,
            'allow_search': True,
            'show_online': False
        })
        
        return jsonify({
            'success': True,
            'settings': settings
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/privacy/settings', methods=['PUT'])
def update_privacy_settings():
    """更新隐私设置"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        data = request.get_json()
        
        with open(PRIVACY_FILE, 'r', encoding='utf-8') as f:
            privacy = json.load(f)
        
        if user['id'] not in privacy:
            privacy[user['id']] = {}
        
        # 更新设置
        privacy[user['id']].update(data)
        
        with open(PRIVACY_FILE, 'w', encoding='utf-8') as f:
            json.dump(privacy, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '隐私设置已保存'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 帮助中心 ==========
@app.route('/api/help/<topic>', methods=['GET'])
def get_help_topic(topic):
    """获取帮助主题内容"""
    try:
        help_topics = {
            'register': {
                'title': '如何注册账号？',
                'content': '点击首页"注册"按钮，输入用户名、密码、邮箱或手机号，完成验证后即可注册成功。'
            },
            'login': {
                'title': '如何登录账号？',
                'content': '点击首页"登录"按钮，输入用户名/邮箱/手机号和密码即可登录。支持记住密码功能。'
            },
            'fortune': {
                'title': '算命结果准确吗？',
                'content': '算命结果仅供参考，不可全信。命运掌握在自己手中，算命只是提供一种思路和方向。'
            },
            'vip': {
                'title': '如何获得VIP会员？',
                'content': '每天登录自动随机获得1-6小时VIP会员时长，每日签到还可额外获得积分和VIP时长奖励。'
            },
            'avatar': {
                'title': '如何上传头像？',
                'content': '进入个人中心，点击头像区域，选择图片上传即可。系统会自动审核头像内容。'
            },
            'contact': {
                'title': '如何联系客服？',
                'content': '发送邮件至 support@xuanji.com，我们的客服团队会在24小时内回复您。'
            }
        }
        
        if topic in help_topics:
            return jsonify({
                'success': True,
                'topic': help_topics[topic]
            }), 200
        else:
            return jsonify({'success': False, 'message': '帮助主题不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 关于我们 ==========
@app.route('/api/about', methods=['GET'])
def get_about():
    """获取关于我们信息"""
    try:
        about_info = {
            'site_name': '玄机算命网',
            'version': '1.0.0',
            'description': '传承千年智慧，揭秘命运玄机。我们致力于为用户提供专业、准确的算命服务。',
            'contact_email': 'support@xuanji.com',
            'website': 'https://xuanji.com',
            'icp': '京ICP备XXXXXXXX号-1',
            'police_icp': '京公网安备 XXXXXXXXXXXXX号',
            'copyright': '© 2026 玄机算命网 版权所有'
        }
        
        return jsonify({
            'success': True,
            'about': about_info
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 亲友档案库 ==========
CONTACTS_FILE = os.path.join(DATA_DIR, 'contacts.json')

if not os.path.exists(CONTACTS_FILE):
    with open(CONTACTS_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)


@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    """获取联系人列表，支持搜索和关系筛选"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        search = request.args.get('search', '').strip()
        relation = request.args.get('relation', '').strip()

        with open(CONTACTS_FILE, 'r', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                contacts_data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        user_contacts = contacts_data.get(user['id'], [])

        # 筛选
        if search:
            user_contacts = [c for c in user_contacts if search.lower() in c.get('name', '').lower()]
        if relation:
            user_contacts = [c for c in user_contacts if c.get('relation') == relation]

        # 按创建时间倒序
        user_contacts.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return jsonify({'success': True, 'contacts': user_contacts}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/contacts/<contact_id>', methods=['GET'])
def get_contact(contact_id):
    """获取单个联系人"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        with open(CONTACTS_FILE, 'r', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                contacts_data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        for c in contacts_data.get(user['id'], []):
            if c['id'] == contact_id:
                return jsonify({'success': True, 'contact': c}), 200

        return jsonify({'success': False, 'message': '联系人不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/contacts', methods=['POST'])
def add_contact():
    """添加联系人"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        data = request.get_json()
        name = (data.get('name', '') or '').strip()
        if not name:
            return jsonify({'success': False, 'message': '请输入姓名'}), 400

        birthday = data.get('birthday', '')
        gender = data.get('gender', '')
        relation = data.get('relation', '')
        notes = data.get('notes', '')

        now = datetime.now().isoformat()
        contact = {
            'id': 'contact_' + ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
            'name': name,
            'birthday': birthday,
            'gender': gender,
            'relation': relation,
            'notes': notes,
            'created_at': now,
            'updated_at': now
        }

        with open(CONTACTS_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                contacts_data = json.load(f)
                if user['id'] not in contacts_data:
                    contacts_data[user['id']] = []
                contacts_data[user['id']].append(contact)
                f.seek(0)
                f.truncate()
                json.dump(contacts_data, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return jsonify({'success': True, 'message': '添加成功', 'contact': contact}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/contacts/<contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """更新联系人"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        data = request.get_json()

        with open(CONTACTS_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                contacts_data = json.load(f)

                user_contacts = contacts_data.get(user['id'], [])
                found = False
                for c in user_contacts:
                    if c['id'] == contact_id:
                        if 'name' in data:
                            c['name'] = data['name'].strip()
                        if 'birthday' in data:
                            c['birthday'] = data['birthday']
                        if 'gender' in data:
                            c['gender'] = data['gender']
                        if 'relation' in data:
                            c['relation'] = data['relation']
                        if 'notes' in data:
                            c['notes'] = data['notes']
                        c['updated_at'] = datetime.now().isoformat()
                        found = True
                        break

                if not found:
                    return jsonify({'success': False, 'message': '联系人不存在'}), 404

                f.seek(0)
                f.truncate()
                json.dump(contacts_data, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return jsonify({'success': True, 'message': '更新成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/contacts/<contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """删除联系人"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        with open(CONTACTS_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                contacts_data = json.load(f)

                if user['id'] in contacts_data:
                    contacts_data[user['id']] = [
                        c for c in contacts_data[user['id']] if c['id'] != contact_id
                    ]

                f.seek(0)
                f.truncate()
                json.dump(contacts_data, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return jsonify({'success': True, 'message': '删除成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ========== 自定义数据表格 ==========
DATASETS_FILE = os.path.join(DATA_DIR, 'datasets.json')

if not os.path.exists(DATASETS_FILE):
    with open(DATASETS_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)


@app.route('/api/datasets', methods=['GET'])
def get_datasets():
    """获取数据集列表"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        with open(DATASETS_FILE, 'r', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                datasets_data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        user_datasets = datasets_data.get(user['id'], [])
        # 返回摘要（不含 records 详情，减少传输量）
        summaries = []
        for ds in user_datasets:
            summaries.append({
                'id': ds['id'],
                'name': ds['name'],
                'description': ds.get('description', ''),
                'fields': ds.get('fields', []),
                'record_count': len(ds.get('records', [])),
                'created_at': ds.get('created_at', ''),
                'updated_at': ds.get('updated_at', '')
            })

        summaries.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return jsonify({'success': True, 'datasets': summaries}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/datasets', methods=['POST'])
def create_dataset():
    """创建数据集"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        data = request.get_json()
        name = (data.get('name', '') or '').strip()
        if not name:
            return jsonify({'success': False, 'message': '请输入数据集名称'}), 400

        description = data.get('description', '')
        fields = data.get('fields', [])
        # 验证字段定义
        valid_types = {'text', 'number', 'date', 'select'}
        for fld in fields:
            if not fld.get('name'):
                return jsonify({'success': False, 'message': '字段名不能为空'}), 400
            if fld.get('type', 'text') not in valid_types:
                return jsonify({'success': False, 'message': f'不支持的字段类型: {fld.get("type")}'}), 400

        now = datetime.now().isoformat()
        dataset = {
            'id': 'ds_' + ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
            'name': name,
            'description': description,
            'fields': fields,
            'records': [],
            'created_at': now,
            'updated_at': now
        }

        with open(DATASETS_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                datasets_data = json.load(f)
                if user['id'] not in datasets_data:
                    datasets_data[user['id']] = []
                datasets_data[user['id']].append(dataset)
                f.seek(0)
                f.truncate()
                json.dump(datasets_data, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return jsonify({'success': True, 'message': '数据集创建成功', 'dataset': {
            'id': dataset['id'], 'name': name, 'description': description,
            'fields': fields, 'record_count': 0, 'created_at': now, 'updated_at': now
        }}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/datasets/<dataset_id>', methods=['PUT'])
def update_dataset(dataset_id):
    """更新数据集（名称、描述、字段）"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        data = request.get_json()

        with open(DATASETS_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                datasets_data = json.load(f)

                user_datasets = datasets_data.get(user['id'], [])
                found = False
                for ds in user_datasets:
                    if ds['id'] == dataset_id:
                        if 'name' in data:
                            ds['name'] = data['name'].strip()
                        if 'description' in data:
                            ds['description'] = data['description']
                        if 'fields' in data:
                            ds['fields'] = data['fields']
                        ds['updated_at'] = datetime.now().isoformat()
                        found = True
                        break

                if not found:
                    return jsonify({'success': False, 'message': '数据集不存在'}), 404

                f.seek(0)
                f.truncate()
                json.dump(datasets_data, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return jsonify({'success': True, 'message': '更新成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/datasets/<dataset_id>', methods=['DELETE'])
def delete_dataset(dataset_id):
    """删除数据集"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        with open(DATASETS_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                datasets_data = json.load(f)

                if user['id'] in datasets_data:
                    datasets_data[user['id']] = [
                        d for d in datasets_data[user['id']] if d['id'] != dataset_id
                    ]

                f.seek(0)
                f.truncate()
                json.dump(datasets_data, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return jsonify({'success': True, 'message': '删除成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/datasets/<dataset_id>/records', methods=['GET'])
def get_dataset_records(dataset_id):
    """获取数据集记录列表"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))

        with open(DATASETS_FILE, 'r', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                datasets_data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        for ds in datasets_data.get(user['id'], []):
            if ds['id'] == dataset_id:
                records = ds.get('records', [])
                total = len(records)
                start = (page - 1) * per_page
                end = start + per_page
                return jsonify({
                    'success': True,
                    'dataset': {'id': ds['id'], 'name': ds['name'], 'fields': ds.get('fields', [])},
                    'records': records[start:end],
                    'total': total,
                    'page': page,
                    'per_page': per_page
                }), 200

        return jsonify({'success': False, 'message': '数据集不存在'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/datasets/<dataset_id>/records', methods=['POST'])
def add_dataset_record(dataset_id):
    """添加记录"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        data = request.get_json()
        record_data = data.get('data', {})

        with open(DATASETS_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                datasets_data = json.load(f)

                for ds in datasets_data.get(user['id'], []):
                    if ds['id'] == dataset_id:
                        record = {
                            'id': 'rec_' + ''.join(random.choices(string.ascii_letters + string.digits, k=16)),
                            'data': record_data,
                            'created_at': datetime.now().isoformat()
                        }
                        ds.setdefault('records', []).append(record)
                        ds['updated_at'] = datetime.now().isoformat()

                        f.seek(0)
                        f.truncate()
                        json.dump(datasets_data, f, ensure_ascii=False, indent=2)
                        return jsonify({'success': True, 'message': '记录添加成功', 'record': record}), 200

                return jsonify({'success': False, 'message': '数据集不存在'}), 404
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/datasets/<dataset_id>/records/<record_id>', methods=['PUT'])
def update_dataset_record(dataset_id, record_id):
    """更新记录"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        data = request.get_json()
        record_data = data.get('data', {})

        with open(DATASETS_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                datasets_data = json.load(f)

                for ds in datasets_data.get(user['id'], []):
                    if ds['id'] == dataset_id:
                        for rec in ds.get('records', []):
                            if rec['id'] == record_id:
                                rec['data'] = record_data
                                ds['updated_at'] = datetime.now().isoformat()
                                f.seek(0)
                                f.truncate()
                                json.dump(datasets_data, f, ensure_ascii=False, indent=2)
                                return jsonify({'success': True, 'message': '记录更新成功'}), 200
                        return jsonify({'success': False, 'message': '记录不存在'}), 404

                return jsonify({'success': False, 'message': '数据集不存在'}), 404
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/datasets/<dataset_id>/records/<record_id>', methods=['DELETE'])
def delete_dataset_record(dataset_id, record_id):
    """删除记录"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        with open(DATASETS_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                datasets_data = json.load(f)

                for ds in datasets_data.get(user['id'], []):
                    if ds['id'] == dataset_id:
                        ds['records'] = [r for r in ds.get('records', []) if r['id'] != record_id]
                        ds['updated_at'] = datetime.now().isoformat()
                        f.seek(0)
                        f.truncate()
                        json.dump(datasets_data, f, ensure_ascii=False, indent=2)
                        return jsonify({'success': True, 'message': '记录删除成功'}), 200

                return jsonify({'success': False, 'message': '数据集不存在'}), 404
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ========== 分类管理 ==========
CATEGORIES_FILE = os.path.join(DATA_DIR, 'categories.json')

if not os.path.exists(CATEGORIES_FILE):
    with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """获取分类列表"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                categories_data = json.load(f)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        user_categories = categories_data.get(user['id'], [])
        user_categories.sort(key=lambda x: x.get('created_at', ''))

        return jsonify({'success': True, 'categories': user_categories}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/categories', methods=['POST'])
def create_category():
    """创建分类"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        data = request.get_json()
        name = (data.get('name', '') or '').strip()
        if not name:
            return jsonify({'success': False, 'message': '请输入分类名称'}), 400

        color = data.get('color', '#ffd700')
        icon = data.get('icon', '📋')

        category = {
            'id': 'cat_' + ''.join(random.choices(string.ascii_letters + string.digits, k=12)),
            'name': name,
            'color': color,
            'icon': icon,
            'created_at': datetime.now().isoformat()
        }

        with open(CATEGORIES_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                categories_data = json.load(f)
                if user['id'] not in categories_data:
                    categories_data[user['id']] = []
                categories_data[user['id']].append(category)
                f.seek(0)
                f.truncate()
                json.dump(categories_data, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return jsonify({'success': True, 'message': '分类创建成功', 'category': category}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/categories/<category_id>', methods=['PUT'])
def update_category(category_id):
    """更新分类"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        data = request.get_json()

        with open(CATEGORIES_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                categories_data = json.load(f)

                for cat in categories_data.get(user['id'], []):
                    if cat['id'] == category_id:
                        if 'name' in data:
                            cat['name'] = data['name'].strip()
                        if 'color' in data:
                            cat['color'] = data['color']
                        if 'icon' in data:
                            cat['icon'] = data['icon']
                        f.seek(0)
                        f.truncate()
                        json.dump(categories_data, f, ensure_ascii=False, indent=2)
                        return jsonify({'success': True, 'message': '分类更新成功'}), 200

                return jsonify({'success': False, 'message': '分类不存在'}), 404
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    """删除分类（同时清除历史记录中对该分类的引用）"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        with open(CATEGORIES_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                categories_data = json.load(f)

                if user['id'] in categories_data:
                    categories_data[user['id']] = [
                        c for c in categories_data[user['id']] if c['id'] != category_id
                    ]

                f.seek(0)
                f.truncate()
                json.dump(categories_data, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        # 清除历史记录中的分类引用
        with open(DIVINATION_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                histories = json.load(f)
                if user['id'] in histories:
                    for h in histories[user['id']]:
                        if h.get('category_id') == category_id:
                            h['category_id'] = ''
                f.seek(0)
                f.truncate()
                json.dump(histories, f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        return jsonify({'success': True, 'message': '分类删除成功'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/divination-history/<history_id>/classify', methods=['PUT'])
def classify_history(history_id):
    """设置历史记录的分类和标签"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result

        data = request.get_json()
        category_id = data.get('category_id', '')
        tags = data.get('tags', [])

        with open(DIVINATION_FILE, 'r+', encoding='utf-8') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                f.seek(0)
                histories = json.load(f)

                if user['id'] in histories:
                    for h in histories[user['id']]:
                        if h['id'] == history_id:
                            h['category_id'] = category_id
                            h['tags'] = tags
                            f.seek(0)
                            f.truncate()
                            json.dump(histories, f, ensure_ascii=False, indent=2)
                            return jsonify({'success': True, 'message': '分类设置成功'}), 200

                return jsonify({'success': False, 'message': '记录不存在'}), 404
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ========== 占卜历史（增强：支持筛选） ==========
# 覆盖原有的 GET /api/divination-history，增加 category/tag/search 参数
# 注意：此路由在之前已注册，这里通过修改原函数逻辑来实现增强
# 由于 Flask 不支持同一路由重复注册，需要修改上方已有的 get_divination_history 函数

# ===== WSGI 支持（PythonAnywhere 部署）=====
# 添加 application 对象（WSGI 标准）
application = app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
