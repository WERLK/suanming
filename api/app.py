import os
import sys

# Fix Python path for gunicorn compatibility (can start from any directory)
api_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(api_dir)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from flask import Flask, request, jsonify, session, make_response, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import hashlib
import smtplib
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
    # 安全过滤：解析真实路径防路径穿越
    import os.path
    safe_path = os.path.realpath(os.path.join(PROJECT_ROOT, filename))
    if not safe_path.startswith(os.path.realpath(PROJECT_ROOT) + os.sep):
        return 'Forbidden', 403
    try:
        return send_from_directory(PROJECT_ROOT, filename)
    except FileNotFoundError:
        return 'Not Found', 404

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
    """用户注册"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
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
        new_user = {
            'id': 'user_' + ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
            'username': username,
            'nickname': generate_random_nickname(),
            'password': hash_password(password),
            'email': email,
            'phone': phone,
            'avatar': '',
            'avatar_type': 'emoji',
            'avatar_preset': generate_random_avatar(),
            'birthday': '',
            'gender': '',
            'create_time': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat(),
            'status': 'active',
            'vip_level': 'basic',
            'vip_expire': None,
            'ad_watch_count': 0,
            'ad_watch_date': ''
        }
        users.append(new_user)
        save_users(users)
        token = generate_token(new_user['id'])
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': new_user['id'],
                'username': new_user['username'],
                'nickname': new_user['nickname'],
                'avatar_type': new_user['avatar_type'],
                'avatar_preset': new_user['avatar_preset']
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
        user['last_login'] = datetime.now().isoformat()
        save_users(users)
        token = generate_token(user['id'])
        response = jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'nickname': user.get('nickname', user['username']),
                'avatar_type': user.get('avatar_type', ''),
                'avatar_preset': user.get('avatar_preset', '')
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
        if not user.get('avatar_type') or not user.get('avatar_preset'):
            user['avatar_type'] = 'emoji'
            user['avatar_preset'] = generate_random_avatar()
            need_save = True
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
            'ad_watch_count': user.get('ad_watch_count', 0)
        }
        return jsonify({'success': True, 'user': user_info}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户信息失败: {str(e)}'}), 500

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
    return jsonify({'success': False, 'message': '微信登录功能开发中，敬请期待...'}), 501

@app.route('/api/qq-login', methods=['POST'])
def qq_login():
    return jsonify({'success': False, 'message': 'QQ登录功能开发中，敬请期待...'}), 501

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


# 自动更新接口
@app.route('/update-secret-2026')
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

# ========== 会员VIP系统 ==========

VIP_LEVELS = {
    'free':      {'name': '免费用户', 'color': '#888',    'max_daily_ads': 3},
    'basic':     {'name': '基础会员', 'color': '#4caf50', 'max_daily_ads': 5},
    'permanent': {'name': '永久会员', 'color': '#ffd700', 'max_daily_ads': 10},
}

AD_REWARD_HOURS = 2
PERMANENT_AD_THRESHOLD = 20


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
        'wheel_date': ''
    }
    for k, v in defaults.items():
        if k not in user:
            user[k] = v
    return user


@app.route('/api/vip/status', methods=['GET'])
def vip_status():
    """获取会员状态"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result
        _ensure_vip_fields(user)

        vip_expire = user.get('vip_expire')
        vip_remaining = None
        if vip_expire:
            expire_dt = _safe_parse_datetime(vip_expire)
            if expire_dt is None:
                user['vip_expire'] = None
                save_users(users)
                vip_expire = None
            else:
                remaining = expire_dt - datetime.now()
                if remaining.total_seconds() <= 0:
                    user['vip_level'] = 'free'
                    user['vip_expire'] = None
                    save_users(users)
                    vip_expire = None
                else:
                    hours = remaining.total_seconds() // 3600
                    minutes = (remaining.total_seconds() % 3600) // 60
                    vip_remaining = f'{int(hours)}小时{int(minutes)}分钟'

        level_info = VIP_LEVELS.get(user.get('vip_level', 'free'), VIP_LEVELS['free'])
        today = _get_today()
        today_ads = user.get('ad_watch_count', 0) if user.get('ad_watch_date') == today else 0
        max_ads = VIP_LEVELS[user.get('vip_level', 'free')]['max_daily_ads']

        total_ad_count = user.get('total_ad_count', 0)

        today_checked_in = (user.get('last_checkin', '') == today)
        wheel_date = user.get('wheel_date', '')
        wheel_spins_today = user.get('wheel_spins_today', 0) if wheel_date == today else 0
        max_wheel_spins = 5
        wheel_spins_remaining = max(0, max_wheel_spins - wheel_spins_today)

        return jsonify({
            'success': True,
            'vip_level': user.get('vip_level', 'free'),
            'vip_level_name': level_info['name'],
            'vip_expire': vip_expire,
            'vip_remaining': vip_remaining,
            'ad_watch_count': user.get('ad_watch_count', 0),
            'ad_watch_date': user.get('ad_watch_date', ''),
            'today_ads': today_ads,
            'max_daily_ads': max_ads,
            'ad_reward_hours': AD_REWARD_HOURS,
            'total_ad_count': total_ad_count,
            'permanent_threshold': PERMANENT_AD_THRESHOLD,
            'points': user.get('points', 0),
            'checkin_streak': user.get('checkin_streak', 0),
            'last_checkin': user.get('last_checkin', ''),
            'today_checked_in': today_checked_in,
            'wheel_spins_remaining': wheel_spins_remaining
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/vip/watch-ad', methods=['POST'])
def vip_watch_ad():
    """观看广告增加会员时长"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result
        _ensure_vip_fields(user)

        # 找到用户在列表中的索引
        user_index = None
        for i, u in enumerate(users):
            if u['id'] == user['id']:
                user_index = i
                break

        today = _get_today()
        ad_date = user.get('ad_watch_date', '')
        today_ads = user.get('ad_watch_count', 0) if ad_date == today else 0
        max_ads = VIP_LEVELS[user.get('vip_level', 'free')]['max_daily_ads']

        if today_ads >= max_ads:
            return jsonify({
                'success': False, 'message': f'今日观看次数已达上限（{max_ads}次），明天再来吧'
            }), 400

        # 递增累计广告观看次数
        total_ad_count = user.get('total_ad_count', 0) + 1
        users[user_index]['total_ad_count'] = total_ad_count

        # 检查是否达到永久会员阈值
        unlocked_permanent = False
        if total_ad_count >= PERMANENT_AD_THRESHOLD:
            users[user_index]['vip_level'] = 'permanent'
            users[user_index]['vip_expire'] = None
            unlocked_permanent = True
        else:
            # 增加会员时长
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

            new_expire = expire_dt + timedelta(hours=AD_REWARD_HOURS)
            users[user_index]['vip_expire'] = new_expire.isoformat()
            users[user_index]['vip_level'] = 'basic'

        # 更新每日广告计数
        if ad_date == today:
            users[user_index]['ad_watch_count'] = today_ads + 1
        else:
            users[user_index]['ad_watch_count'] = 1
            users[user_index]['ad_watch_date'] = today

        save_users(users)

        if unlocked_permanent:
            return jsonify({
                'success': True,
                'message': f'🎉 恭喜！已累计观看{total_ad_count}次广告，解锁永久会员！',
                'vip_level': 'permanent',
                'vip_level_name': '永久会员',
                'vip_remaining': '永久有效',
                'vip_expire': None,
                'today_ads': users[user_index]['ad_watch_count'],
                'max_daily_ads': max_ads,
                'total_ad_count': total_ad_count,
                'permanent_threshold': PERMANENT_AD_THRESHOLD,
                'unlocked_permanent': True
            }), 200
        else:
            remaining = new_expire - datetime.now()
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)

            return jsonify({
                'success': True,
                'message': f'广告观看完成！会员时长已延长{AD_REWARD_HOURS}小时（累计{total_ad_count}/{PERMANENT_AD_THRESHOLD}次，满{PERMANENT_AD_THRESHOLD}次解锁永久会员）',
                'vip_level': 'basic',
                'vip_level_name': '基础会员',
                'vip_remaining': f'{hours}小时{minutes}分钟',
                'vip_expire': new_expire.isoformat(),
                'today_ads': users[user_index]['ad_watch_count'],
                'max_daily_ads': max_ads,
                'total_ad_count': total_ad_count,
                'permanent_threshold': PERMANENT_AD_THRESHOLD
            }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 签到系统 ==========

@app.route('/api/vip/checkin', methods=['POST'])
def vip_checkin():
    """每日签到获取积分和VIP时长"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result
        _ensure_vip_fields(user)
        user_index = next(i for i, u in enumerate(users) if u['id'] == user['id'])

        today = _get_today()
        if user.get('last_checkin', '') == today:
            return jsonify({'success': False, 'message': '今日已签到，明天再来吧'}), 400

        # 检查连续签到
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        if user.get('last_checkin', '') == yesterday:
            streak = user.get('checkin_streak', 0) + 1
        else:
            streak = 1
        users[user_index]['checkin_streak'] = streak
        users[user_index]['last_checkin'] = today

        # 计算奖励：10 基础 + streak 加成（上限30）
        bonus = min(streak - 1, 10) * 2
        earned_points = 10 + bonus
        users[user_index]['points'] = user.get('points', 0) + earned_points

        # 赠送 2 小时 basic VIP
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
        new_expire = expire_dt + timedelta(hours=AD_REWARD_HOURS)
        users[user_index]['vip_expire'] = new_expire.isoformat()
        users[user_index]['vip_level'] = 'basic'

        save_users(users)

        return jsonify({
            'success': True,
            'message': f'签到成功！获得 {earned_points} 积分 + {AD_REWARD_HOURS}小时会员',
            'points_earned': earned_points,
            'total_points': users[user_index]['points'],
            'streak': streak,
            'vip_extended': AD_REWARD_HOURS
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 积分兑换 ==========

@app.route('/api/vip/redeem', methods=['POST'])
def vip_redeem():
    """积分兑换VIP时长/广告次数/永久会员"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result
        _ensure_vip_fields(user)
        user_index = next(i for i, u in enumerate(users) if u['id'] == user['id'])

        data = request.get_json() or {}
        redeem_type = data.get('type', '')

        redeem_options = {
            'ad1': {'points': 20,   'label': '免广卡x1', 'action': 'add_ad'},
            'vip3': {'points': 50,  'label': '3小时会员', 'action': 'extend_vip', 'hours': 3},
            'vip24': {'points': 200, 'label': '24小时会员', 'action': 'extend_vip', 'hours': 24},
            'permanent': {'points': 500, 'label': '永久会员', 'action': 'unlock_permanent'},
        }

        if redeem_type not in redeem_options:
            return jsonify({'success': False, 'message': '无效的兑换类型'}), 400

        opt = redeem_options[redeem_type]
        if user.get('points', 0) < opt['points']:
            return jsonify({'success': False, 'message': f'积分不足，需要 {opt["points"]} 积分'}), 400

        users[user_index]['points'] = user['points'] - opt['points']
        message = ''

        if opt['action'] == 'add_ad':
            users[user_index]['total_ad_count'] = user.get('total_ad_count', 0) + 1
            message = f'兑换成功！获得免广卡x1'
            # 检查是否达到永久阈值
            if users[user_index]['total_ad_count'] >= PERMANENT_AD_THRESHOLD:
                users[user_index]['vip_level'] = 'permanent'
                users[user_index]['vip_expire'] = None
                message += '，并已解锁永久会员！'

        elif opt['action'] == 'extend_vip':
            now = datetime.now()
            vip_expire = user.get('vip_expire')
            if vip_expire:
                expire_dt = datetime.fromisoformat(vip_expire)
                if expire_dt < now:
                    expire_dt = now
            else:
                expire_dt = now
            new_expire = expire_dt + timedelta(hours=opt['hours'])
            users[user_index]['vip_expire'] = new_expire.isoformat()
            users[user_index]['vip_level'] = 'basic'
            message = f'兑换成功！获得 {opt["hours"]} 小时会员'

        elif opt['action'] == 'unlock_permanent':
            users[user_index]['vip_level'] = 'permanent'
            users[user_index]['vip_expire'] = None
            message = '兑换成功！已解锁永久会员'

        save_users(users)

        return jsonify({
            'success': True,
            'message': message,
            'remaining_points': users[user_index]['points'],
            'vip_level': users[user_index]['vip_level']
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ========== 幸运转盘 ==========

@app.route('/api/vip/wheel', methods=['POST'])
def vip_wheel():
    """幸运转盘抽奖"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, users = result
        _ensure_vip_fields(user)
        user_index = next(i for i, u in enumerate(users) if u['id'] == user['id'])

        today = _get_today()
        wheel_date = user.get('wheel_date', '')
        spins_today = user.get('wheel_spins_today', 0) if wheel_date == today else 0
        max_spins = 5

        if spins_today >= max_spins:
            return jsonify({'success': False, 'message': f'今日转盘次数已用完（{max_spins}次）'}), 400

        # 更新转盘计数
        if wheel_date == today:
            users[user_index]['wheel_spins_today'] = spins_today + 1
        else:
            users[user_index]['wheel_spins_today'] = 1
            users[user_index]['wheel_date'] = today

        # 奖品池（无空奖）
        import random
        roll = random.random() * 100
        # 1. 1小时VIP — 25%
        # 2. 2小时VIP — 20%
        # 3. 5积分 — 20%
        # 4. 10积分 — 15%
        # 5. 免广卡x1 — 10%
        # 6. 免广卡x3 — 5%
        # 7. 24小时VIP — 3%
        # 8. 50积分 — 2%
        if roll < 25:
            prize_type, prize_value, prize_name = 'vip_hours', 1, '1小时VIP会员'
        elif roll < 45:
            prize_type, prize_value, prize_name = 'vip_hours', 2, '2小时VIP会员'
        elif roll < 65:
            prize_type, prize_value, prize_name = 'points', 5, '5积分'
        elif roll < 80:
            prize_type, prize_value, prize_name = 'points', 10, '10积分'
        elif roll < 90:
            prize_type, prize_value, prize_name = 'ad_credit', 1, '免广卡x1'
        elif roll < 95:
            prize_type, prize_value, prize_name = 'ad_credit', 3, '免广卡x3'
        elif roll < 98:
            prize_type, prize_value, prize_name = 'vip_hours', 24, '24小时VIP会员'
        else:
            prize_type, prize_value, prize_name = 'points', 50, '50积分'

        # 发放奖品
        if prize_type == 'points':
            users[user_index]['points'] = user.get('points', 0) + prize_value
        elif prize_type == 'vip_hours':
            now = datetime.now()
            vip_expire = user.get('vip_expire')
            if vip_expire:
                expire_dt = datetime.fromisoformat(vip_expire)
                if expire_dt < now:
                    expire_dt = now
            else:
                expire_dt = now
            new_expire = expire_dt + timedelta(hours=prize_value)
            users[user_index]['vip_expire'] = new_expire.isoformat()
            users[user_index]['vip_level'] = 'basic'
        elif prize_type == 'ad_credit':
            users[user_index]['total_ad_count'] = user.get('total_ad_count', 0) + prize_value
            if users[user_index]['total_ad_count'] >= PERMANENT_AD_THRESHOLD:
                users[user_index]['vip_level'] = 'permanent'
                users[user_index]['vip_expire'] = None

        save_users(users)

        remaining = max_spins - users[user_index]['wheel_spins_today']
        message = f'🎰 恭喜获得：{prize_name}！'
        if prize_type == 'ad_credit' and users[user_index]['vip_level'] == 'permanent' and user.get('vip_level') != 'permanent':
            message += ' 累计广告计次已达到永久门槛，已解锁永久会员！'

        return jsonify({
            'success': True,
            'message': message,
            'prize_type': prize_type,
            'prize_value': prize_value,
            'prize_name': prize_name,
            'remaining_spins': remaining,
            'total_points': users[user_index].get('points', 0),
            'vip_level': users[user_index]['vip_level'],
            'unlocked_permanent': (prize_type == 'ad_credit' and users[user_index]['vip_level'] == 'permanent' and user.get('vip_level') != 'permanent')
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ========== 头像上传（带自动审核）==========
from api.avatar_audit import AvatarAuditor

AVATAR_SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'avatars')
os.makedirs(AVATAR_SAVE_DIR, exist_ok=True)

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
    """获取用户占卜历史"""
    try:
        result = _get_auth_user()
        if not result:
            return jsonify({'success': False, 'message': '未登录'}), 401
        user, _ = result
        
        with open(DIVINATION_FILE, 'r', encoding='utf-8') as f:
            histories = json.load(f)
        
        user_histories = histories.get(user['id'], [])
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
                'content': '您可以通过观看广告赚取VIP时长，每次观看广告可获得2小时会员时长。'
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

# ===== WSGI 支持（PythonAnywhere 部署）=====
# 添加 application 对象（WSGI 标准）
application = app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
