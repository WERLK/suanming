from flask import Flask, request, jsonify, session, make_response
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

# 导入短信验证码扩展
try:
    from api.sms_extension import register_sms_routes, sms_captcha_store
    # 注册短信验证码路由
    register_sms_routes(app)
    print("✅ 短信验证码扩展已加载")
except Exception as e:
    print(f"⚠️ 短信验证码扩展加载失败: {e}")

app = Flask(__name__)
app.secret_key = 'xuanji_fortune_secret_key_2026'
CORS(app)

# 验证码存储（实际项目中应使用Redis或数据库）
captcha_store = {}

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
    
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    
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
    except:
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
def send_email(to_email, subject, body):
    # 配置邮件服务器（需要修改为实际的邮件配置）
    smtp_server = 'smtp.example.com'
    smtp_port = 587
    sender_email = 'your_email@example.com'
    sender_password = 'your_password'
    
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False

# 验证码API路由

@app.route('/api/captcha/generate', methods=['GET'])
def generate_captcha():
    """生成图片验证码"""
    try:
        # 生成随机字符串（4位字母和数字）
        captcha_text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        # 创建图片
        width, height = 120, 40
        image = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 绘制背景噪点
        for _ in range(100):
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            color = (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))
            draw.point((x, y), fill=color)
        
        # 绘制文字
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
        except:
            font = ImageFont.load_default()
        
        # 每个字符随机颜色和位置
        for i, char in enumerate(captcha_text):
            color = (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))
            x = 10 + i * 25 + random.randint(-3, 3)
            y = random.randint(5, 15)
            draw.text((x, y), char, font=font, fill=color)
        
        # 绘制干扰线
        for _ in range(3):
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line([(x1, y1), (x2, y2)], fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), width=2)
        
        # 保存图片到内存
        img_io = io.BytesIO()
        image.save(img_io, 'PNG')
        img_io.seek(0)
        
        # 生成唯一ID并存储验证码
        captcha_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        captcha_store[captcha_id] = {
            'text': captcha_text,
            'expire_time': (datetime.now() + timedelta(minutes=5)).isoformat()  # 5分钟有效期
        }
        
        # 返回图片和ID
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
        
        # 检查验证码是否存在
        if captcha_id not in captcha_store:
            return jsonify({'success': False, 'message': '验证码已失效，请刷新'}), 400
        
        # 检查是否过期
        captcha_data = captcha_store[captcha_id]
        expire_time = datetime.fromisoformat(captcha_data['expire_time'])
        
        if datetime.now() > expire_time:
            del captcha_store[captcha_id]
            return jsonify({'success': False, 'message': '验证码已过期，请刷新'}), 400
        
        # 验证验证码
        if captcha_data['text'] != captcha_text:
            return jsonify({'success': False, 'message': '验证码错误'}), 400
        
        # 验证成功，删除验证码
        del captcha_store[captcha_id]
        
        return jsonify({'success': True, 'message': '验证成功'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'验证验证码失败: {str(e)}'}), 500

@app.route('/api/slider/generate', methods=['GET'])
def generate_slider():
    """生成滑块验证码"""
    try:
        # 生成随机位置
        target_x = random.randint(20, 80)  # 目标位置百分比
        target_y = random.randint(30, 70)  # 垂直位置百分比
        
        # 生成唯一ID
        slider_id = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        
        # 存储滑块数据
        slider_store[slider_id] = {
            'target_x': target_x,
            'target_y': target_y,
            'expire_time': (datetime.now() + timedelta(minutes=5)).isoformat()
        }
        
        # 返回滑块数据
        return jsonify({
            'success': True,
            'slider_id': slider_id,
            'target_y': target_y,
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
        slider_x = data.get('slider_x', 0)  # 用户滑动的位置百分比
        
        if not slider_id or slider_x is None:
            return jsonify({'success': False, 'message': '参数不完整'}), 400
        
        # 检查滑块数据是否存在
        if slider_id not in slider_store:
            return jsonify({'success': False, 'message': '滑块验证码已失效，请刷新'}), 400
        
        # 检查是否过期
        slider_data = slider_store[slider_id]
        expire_time = datetime.fromisoformat(slider_data['expire_time'])
        
        if datetime.now() > expire_time:
            del slider_store[slider_id]
            return jsonify({'success': False, 'message': '滑块验证码已过期，请刷新'}), 400
        
        # 验证滑块位置（允许±5%误差）
        target_x = slider_data['target_x']
        if abs(slider_x - target_x) <= 5:
            # 验证成功，删除滑块数据
            del slider_store[slider_id]
            return jsonify({'success': True, 'message': '验证成功'}), 200
        else:
            return jsonify({'success': False, 'message': '请再试一次'}), 400
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'验证滑块验证码失败: {str(e)}'}), 500

# 滑块验证码存储（实际项目中应使用Redis或数据库）
slider_store = {}

# API路由

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        
        # 验证输入
        if not username or len(username) < 3 or len(username) > 20:
            return jsonify({'success': False, 'message': '用户名长度应为3-20个字符'}), 400
        
        if not password or len(password) < 6:
            return jsonify({'success': False, 'message': '密码长度至少6个字符'}), 400
        
        if not username.isalnum() and '_' not in username:
            return jsonify({'success': False, 'message': '用户名只能包含字母、数字和下划线'}), 400
        
        # 读取用户数据
        users = load_users()
        
        # 检查用户名是否已存在
        if any(u['username'] == username for u in users):
            return jsonify({'success': False, 'message': '用户名已存在'}), 400
        
        # 检查邮箱是否已存在
        if email and any(u.get('email') == email for u in users):
            return jsonify({'success': False, 'message': '邮箱已注册'}), 400
        
        # 检查手机号是否已存在
        if phone and any(u.get('phone') == phone for u in users):
            return jsonify({'success': False, 'message': '手机号已注册'}), 400
        
        # 创建新用户
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
            'status': 'active'
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
        
        # 验证输入
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'}), 400
        
        # 读取用户数据
        users = load_users()
        
        # 查找用户
        user = None
        for u in users:
            if u['username'] == username or u.get('email') == username or u.get('phone') == username:
                user = u
                break
        
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 验证密码
        if not verify_password(password, user['password']):
            return jsonify({'success': False, 'message': '密码错误'}), 401
        
        # 检查用户状态
        if user.get('status') != 'active':
            return jsonify({'success': False, 'message': '账户已被禁用'}), 403
        
        # 更新最后登录时间
        user['last_login'] = datetime.now().isoformat()
        save_users(users)
        
        # 生成token
        token = generate_token(user['id'])
        
        # 返回用户信息（不包含密码）
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
        
        # 设置cookie
        if remember:
            response.set_cookie('token', token, max_age=7*24*3600, httponly=True)  # 7天
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
        
        # 读取用户数据
        users = load_users()
        
        user = None
        for u in users:
            if u['id'] == user_id:
                user = u
                break
        
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 返回用户信息（不包含密码）
        user_info = {
            'id': user['id'],
            'username': user['username'],
            'email': user.get('email', ''),
            'phone': user.get('phone', ''),
            'avatar': user.get('avatar', ''),
            'birthday': user.get('birthday', ''),
            'gender': user.get('gender', ''),
            'create_time': user.get('create_time', ''),
            'last_login': user.get('last_login', '')
        }
        
        return jsonify({
            'success': True,
            'user': user_info
        }), 200
        
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
        
        # 读取用户数据
        users = load_users()
        
        user_index = None
        for i, u in enumerate(users):
            if u['id'] == user_id:
                user_index = i
                break
        
        if user_index is None:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 更新用户信息
        allowed_fields = ['username', 'email', 'phone', 'avatar', 'birthday', 'gender']
        for field in allowed_fields:
            if field in data:
                users[user_index][field] = data[field]
        
        save_users(users)
        
        # 返回更新后的用户信息
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
        
        return jsonify({
            'success': True,
            'message': '更新成功',
            'user': user_info
        }), 200
        
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
        
        # 读取用户数据
        users = load_users()
        
        # 查找用户
        user = None
        for u in users:
            if u.get('email') == email:
                user = u
                break
        
        if not user:
            return jsonify({'success': False, 'message': '邮箱未注册'}), 404
        
        # 生成重置token
        reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
        
        # 保存重置token（实际项目中应使用数据库或Redis）
        tokens = json.load(open(TOKENS_FILE, 'r', encoding='utf-8'))
        tokens[reset_token] = {
            'user_id': user['id'],
            'expire_time': (datetime.now() + timedelta(hours=1)).isoformat()  # 1小时有效期
        }
        json.dump(tokens, open(TOKENS_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        
        # 发送重置邮件（实际项目中应发送邮件）
        reset_link = f"http://localhost:8080/reset-password.html?token={reset_token}"
        email_body = f"""
        <h2>重置密码</h2>
        <p>请点击以下链接重置您的密码（1小时内有效）：</p>
        <a href="{reset_link}">{reset_link}</a>
        <p>如果您没有请求重置密码，请忽略此邮件。</p>
        """
        
        # 实际项目中应取消注释以下代码发送邮件
        # send_email(email, '重置密码 - 玄机算命网', email_body)
        
        return jsonify({
            'success': True,
            'message': '重置链接已发送到您的邮箱（实际项目中会发送邮件，当前为演示模式）',
            'reset_link': reset_link  # 演示模式下直接返回链接
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
        
        # 验证重置token
        tokens = json.load(open(TOKENS_FILE, 'r', encoding='utf-8'))
        
        if token not in tokens:
            return jsonify({'success': False, 'message': '重置链接无效'}), 400
        
        token_data = tokens[token]
        expire_time = datetime.fromisoformat(token_data['expire_time'])
        
        if datetime.now() > expire_time:
            del tokens[token]
            json.dump(tokens, open(TOKENS_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
            return jsonify({'success': False, 'message': '重置链接已过期'}), 400
        
        # 读取用户数据
        users = load_users()
        
        user_index = None
        for i, u in enumerate(users):
            if u['id'] == token_data['user_id']:
                user_index = i
                break
        
        if user_index is None:
            return jsonify({'success': False, 'message': '用户不存在'}), 404
        
        # 更新密码
        users[user_index]['password'] = hash_password(new_password)
        save_users(users)
        
        # 删除重置token
        del tokens[token]
        json.dump(tokens, open(TOKENS_FILE, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        
        return jsonify({'success': True, 'message': '密码重置成功'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'重置密码失败: {str(e)}'}), 500

# 微信登录（演示接口）
@app.route('/api/wechat-login', methods=['POST'])
def wechat_login():
    """微信登录（演示）"""
    return jsonify({
        'success': False,
        'message': '微信登录功能开发中，敬请期待...'
    }), 501

# QQ登录（演示接口）
@app.route('/api/qq-login', methods=['POST'])
def qq_login():
    """QQ登录（演示）"""
    return jsonify({
        'success': False,
        'message': 'QQ登录功能开发中，敬请期待...'
    }), 501

# 注册短信验证码路由
try:
    from api.sms_extension import register_sms_routes
    register_sms_routes(app)
    print("✅ 短信验证码扩展已加载")
except Exception as e:
    print(f"⚠️ 短信验证码扩展加载失败: {e}")

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
