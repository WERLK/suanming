from flask import Flask, request, jsonify, session, make_response, send_from_directory
from flask_cors import CORS
import json
import hashlib
import os
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

app = Flask(__name__, static_folder='../', static_url_path='')
app.secret_key = 'xuanji_fortune_secret_key_2026!!'  # 32+ chars for HS256
CORS(app)

# 验证码存储（实际项目中应使用Redis或数据库）
captcha_store = {}
slider_store = {}

# 用户数据存储文件（使用绝对路径）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
TOKENS_FILE = os.path.join(DATA_DIR, 'tokens.json')

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)

# 初始化用户数据文件
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)

if not os.path.exists(TOKENS_FILE):
    with open(TOKENS_FILE, 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False, indent=2)

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

# 读取用户数据
def load_users():
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# 保存用户数据
def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

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
        captcha_store[captcha_id] = {
            'text': captcha_text,
            'expire_time': (datetime.now() + timedelta(minutes=5)).isoformat()
        }
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
            return jsonify({'success': False, 'message': '参数不完整'}), 400
        if captcha_id not in captcha_store:
            return jsonify({'success': False, 'message': '验证码已失效，请刷新'}), 400
        captcha_data = captcha_store[captcha_id]
        expire_time = datetime.fromisoformat(captcha_data['expire_time'])
        if datetime.now() > expire_time:
            del captcha_store[captcha_id]
            return jsonify({'success': False, 'message': '验证码已过期，请刷新'}), 400
        if captcha_data['text'] != captcha_text:
            return jsonify({'success': False, 'message': '验证码错误'}), 400
        del captcha_store[captcha_id]
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
        slider_store[slider_id] = {
            'target_x': target_x,
            'target_y': target_y,
            'expire_time': (datetime.now() + timedelta(minutes=5)).isoformat()
        }
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
            return jsonify({'success': False, 'message': '参数不完整'}), 400
        if slider_id not in slider_store:
            return jsonify({'success': False, 'message': '滑块验证码已失效，请刷新'}), 400
        slider_data = slider_store[slider_id]
        expire_time = datetime.fromisoformat(slider_data['expire_time'])
        if datetime.now() > expire_time:
            del slider_store[slider_id]
            return jsonify({'success': False, 'message': '滑块验证码已过期，请刷新'}), 400
        target_x = slider_data['target_x']
        if abs(slider_x - target_x) <= 5:
            del slider_store[slider_id]
            return jsonify({'success': True, 'message': '验证成功'}), 200
        else:
            return jsonify({'success': False, 'message': '请再试一次'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'验证滑块验证码失败: {str(e)}'}), 500

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
            'password': hash_password(password),
            'email': email,
            'phone': phone,
            'avatar': '',
            'birthday': '',
            'gender': '',
            'create_time': datetime.now().isoformat(),
            'last_login': datetime.now().isoformat(),
            'status': 'active',
            'vip_level': 'free',
            'vip_expire': None,
            'ad_watch_count': 0,
            'ad_watch_date': ''
        }
        users.append(new_user)
        save_users(users)
        return jsonify({
            'success': True,
            'message': '注册成功',
            'user': {
                'id': new_user['id'],
                'username': new_user['username'],
                'email': new_user['email'],
                'phone': new_user['phone']
            }
        }), 201
    except Exception as e:
        return jsonify({'success': False, 'message': f'注册失败: {str(e)}'}), 500

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
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        if not verify_password(password, user['password']):
            return jsonify({'success': False, 'message': '密码错误'}), 401
        if user.get('status') != 'active':
            return jsonify({'success': False, 'message': '账户已被禁用'}), 403
        user['last_login'] = datetime.now().isoformat()
        save_users(users)
        token = generate_token(user['id'])
        user_info = {
            'id': user['id'],
            'username': user['username'],
            'email': user.get('email', ''),
            'phone': user.get('phone', ''),
            'avatar': user.get('avatar', ''),
            'birthday': user.get('birthday', ''),
            'gender': user.get('gender', '')
        }
        response = jsonify({
            'success': True,
            'message': '登录成功',
            'user': user_info,
            'token': token
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
        user_info = {
            'id': user['id'],
            'username': user['username'],
            'email': user.get('email', ''),
            'phone': user.get('phone', ''),
            'avatar': user.get('avatar', ''),
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
        allowed_fields = ['username', 'email', 'phone', 'avatar', 'birthday', 'gender']
        for field in allowed_fields:
            if field in data:
                users[user_index][field] = data[field]
        save_users(users)
        user = users[user_index]
        user_info = {
            'id': user['id'],
            'username': user['username'],
            'email': user.get('email', ''),
            'phone': user.get('phone', ''),
            'avatar': user.get('avatar', ''),
            'birthday': user.get('birthday', ''),
            'gender': user.get('gender', '')
        }
        return jsonify({'success': True, 'message': '更新成功', 'user': user_info}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新用户信息失败: {str(e)}'}), 500

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
                'success': True,
                'message': '重置链接已发送到您的邮箱，请注意查收',
            }), 200
        else:
            return jsonify({
                'success': True,
                'message': '重置链接已生成（邮件服务未配置，请使用以下链接）',
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
        cwd = '/root/suanming/suanming'
        r1 = subprocess.run(['git', 'fetch', 'origin'], cwd=cwd, capture_output=True, text=True, timeout=30)
        r2 = subprocess.run(['git', 'reset', '--hard', 'origin/master'], cwd=cwd, capture_output=True, text=True, timeout=30)
        r3 = subprocess.run(['pkill', '-f', 'gunicorn'], capture_output=True, text=True, timeout=10)
        import time
        time.sleep(2)
        subprocess.Popen(['python3', '-m', 'gunicorn', '-c', 'gunicorn_config.py', 'api.app:app'],
                        cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f'更新成功！{r2.stdout}', 200
    except Exception as e:
        return f'更新失败：{str(e)}', 500

# ========== 会员VIP系统 ==========

VIP_LEVELS = {
    'free': {'name': '免费用户', 'color': '#888', 'max_daily_ads': 3},
    'basic': {'name': '基础会员', 'color': '#4caf50', 'max_daily_ads': 5},
    'premium': {'name': '高级会员', 'color': '#ffd700', 'max_daily_ads': 10},
}

AD_REWARD_HOURS = 2  # 每次看广告赠送2小时会员


def _get_today():
    return datetime.now().strftime('%Y-%m-%d')


def _get_auth_user():
    """获取当前登录用户"""
    token = request.cookies.get('token') or request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None
    user_id = verify_token(token)
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
        'ad_watch_date': ''
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
            expire_dt = datetime.fromisoformat(vip_expire)
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
            'ad_reward_hours': AD_REWARD_HOURS
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
                'success': False,
                'message': f'今日观看次数已达上限（{max_ads}次），明天再来吧'
            }), 400

        # 增加会员时长
        now = datetime.now()
        vip_expire = user.get('vip_expire')
        if vip_expire:
            expire_dt = datetime.fromisoformat(vip_expire)
            if expire_dt < now:
                expire_dt = now
        else:
            expire_dt = now

        new_expire = expire_dt + timedelta(hours=AD_REWARD_HOURS)

        users[user_index]['vip_expire'] = new_expire.isoformat()
        users[user_index]['vip_level'] = 'basic'

        # 更新广告计数
        if ad_date == today:
            users[user_index]['ad_watch_count'] = today_ads + 1
        else:
            users[user_index]['ad_watch_count'] = 1
            users[user_index]['ad_watch_date'] = today

        save_users(users)

        remaining = new_expire - datetime.now()
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)

        return jsonify({
            'success': True,
            'message': f'广告观看完成！会员时长已延长{AD_REWARD_HOURS}小时',
            'vip_level': 'basic',
            'vip_level_name': '基础会员',
            'vip_remaining': f'{hours}小时{minutes}分钟',
            'vip_expire': new_expire.isoformat(),
            'today_ads': users[user_index]['ad_watch_count'],
            'max_daily_ads': max_ads
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
