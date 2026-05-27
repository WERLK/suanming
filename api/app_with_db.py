"""
Flask 应用入口（数据库版本）
使用 SQLite 数据库替换 JSON 文件
"""
from flask import Flask, request, jsonify, session, make_response, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import json
import os
import random
import string
from datetime import datetime, timedelta
import jwt
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# 创建 Flask 应用
app = Flask(__name__, static_folder='../', static_url_path='')
app.config['SECRET_KEY'] = 'xuanji_fortune_secret_key_2026!!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'xuanji.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)

# 初始化数据库
from models import db, User, UserStats, ResetToken, DivinationHistory, Favorite
db.init_app(app)

# 验证码存储（临时使用内存，建议生产环境使用 Redis）
captcha_store = {}
slider_store = {}

# 确保数据目录存在
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# 初始化数据库表
with app.app_context():
    db.create_all()
    print("✅ 数据库初始化完成")

# 导入密码和 Token 函数
from models import hash_password, verify_password, generate_token, verify_token

# 发送邮件函数（保持不变）
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
                config = json.load(f)
                return config
        except:
            pass
    
    return None

def send_email(to_email, subject, content):
    """发送邮件"""
    config = _get_mail_config()
    
    if not config:
        print("⚠️ 邮件服务未配置，演示模式：直接显示重置链接")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = config['sender_email']
        msg['To'] = to_email
        
        msg.attach(MIMEText(content, 'html', 'utf-8'))
        
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['sender_email'], config['sender_password'])
        server.send_message(msg)
        server.quit()
        
        print(f"✅ 邮件已发送到：{to_email}")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败：{e}")
        return False

# ==================== 用户注册 API ====================
@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    
    # 验证用户名
    if not username or len(username) < 3 or len(username) > 20:
        return jsonify({'error': '用户名长度必须为3-20个字符'}), 400
    
    if not username.isalnum() and '_' not in username:
        return jsonify({'error': '用户名只能包含字母、数字和下划线'}), 400
    
    # 验证密码
    if not password or len(password) < 6:
        return jsonify({'error': '密码长度至少为6个字符'}), 400
    
    # 验证邮箱（可选）
    if email:
        import re
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return jsonify({'error': '邮箱格式不正确'}), 400
    
    # 验证手机号（可选）
    if phone:
        if not phone.isdigit() or len(phone) != 11:
            return jsonify({'error': '手机号必须是11位数字'}), 400
    
    with app.app_context():
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'error': '用户名已存在'}), 400
        
        # 检查邮箱是否已存在
        if email and User.query.filter_by(email=email).first():
            return jsonify({'error': '邮箱已被注册'}), 400
        
        # 检查手机号是否已存在
        if phone and User.query.filter_by(phone=phone).first():
            return jsonify({'error': '手机号已被注册'}), 400
        
        # 创建新用户
        import uuid
        user_id = str(uuid.uuid4())
        password_hash = hash_password(password)
        
        new_user = User(
            id=user_id,
            username=username,
            password_hash=password_hash,
            email=email if email else None,
            phone=phone if phone else None
        )
        
        db.session.add(new_user)
        
        # 创建用户统计记录
        user_stats = UserStats(user_id=user_id)
        db.session.add(user_stats)
        
        db.session.commit()
        
        print(f"✅ 用户注册成功：{username} (ID: {user_id})")
        
        return jsonify({
            'message': '注册成功',
            'user_id': user_id
        }), 201

# ==================== 用户登录 API ====================
@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    remember = data.get('remember', False)
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    with app.app_context():
        # 查找用户（支持用户名/邮箱/手机号登录）
        user = User.query.filter(
            (User.username == username) |
            (User.email == username) |
            (User.phone == username)
        ).first()
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        if user.status == 'disabled':
            return jsonify({'error': '账号已被禁用'}), 403
        
        # 验证密码
        if not verify_password(password, user.password_hash):
            return jsonify({'error': '密码错误'}), 401
        
        # 生成 JWT Token
        token = generate_token(user.id, app.config['SECRET_KEY'])
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        print(f"✅ 用户登录成功：{user.username} (ID: {user.id})")
        
        # 设置 Cookie（httpOnly 防止 XSS 攻击）
        response = jsonify({
            'message': '登录成功',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'phone': user.phone
            }
        })
        
        max_age = 7 * 24 * 3600 if remember else None
        response.set_cookie('token', token, httponly=True, max_age=max_age)
        
        return response, 200

# ==================== 获取用户信息 API ====================
@app.route('/api/profile', methods=['GET'])
def get_profile():
    """获取用户信息"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        token = request.cookies.get('token')
    
    if not token:
        return jsonify({'error': '未登录'}), 401
    
    user_id = verify_token(token, app.config['SECRET_KEY'])
    
    if not user_id:
        return jsonify({'error': 'Token 无效或已过期'}), 401
    
    with app.app_context():
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 获取用户统计
        stats = UserStats.query.get(user_id)
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'avatar': user.avatar,
            'birthday': user.birthday.isoformat() if user.birthday else None,
            'gender': user.gender,
            'create_time': user.create_time.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'stats': {
                'divination_count': stats.divination_count if stats else 0,
                'favorite_count': stats.favorite_count if stats else 0
            }
        }), 200

# ==================== 更新用户信息 API ====================
@app.route('/api/profile', methods=['PUT'])
def update_profile():
    """更新用户信息"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        token = request.cookies.get('token')
    
    if not token:
        return jsonify({'error': '未登录'}), 401
    
    user_id = verify_token(token, app.config['SECRET_KEY'])
    
    if not user_id:
        return jsonify({'error': 'Token 无效或已过期'}), 401
    
    data = request.get_json()
    
    with app.app_context():
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 更新用户名
        if 'username' in data:
            new_username = data['username'].strip()
            if new_username and new_username != user.username:
                if User.query.filter_by(username=new_username).first():
                    return jsonify({'error': '用户名已存在'}), 400
                user.username = new_username
        
        # 更新邮箱
        if 'email' in data:
            new_email = data['email'].strip()
            if new_email != user.email:
                if new_email and User.query.filter_by(email=new_email).first():
                    return jsonify({'error': '邮箱已被使用'}), 400
                user.email = new_email if new_email else None
        
        # 更新手机号
        if 'phone' in data:
            new_phone = data['phone'].strip()
            if new_phone != user.phone:
                if new_phone and User.query.filter_by(phone=new_phone).first():
                    return jsonify({'error': '手机号已被使用'}), 400
                user.phone = new_phone if new_phone else None
        
        # 更新生日
        if 'birthday' in data:
            try:
                from datetime import date
                user.birthday = date.fromisoformat(data['birthday']) if data['birthday'] else None
            except:
                pass
        
        # 更新性别
        if 'gender' in data:
            if data['gender'] in ['male', 'female', 'other']:
                user.gender = data['gender']
        
        db.session.commit()
        
        print(f"✅ 用户信息更新成功：{user.username} (ID: {user.id})")
        
        return jsonify({'message': '更新成功'}), 200

# ==================== 忘记密码 API ====================
@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    """忘记密码"""
    data = request.get_json()
    
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({'error': '邮箱不能为空'}), 400
    
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({'error': '邮箱未注册'}), 404
        
        # 生成重置 Token
        import secrets
        token = secrets.token_urlsafe(64)
        
        # 设置过期时间（1小时）
        expire_time = datetime.utcnow() + timedelta(hours=1)
        
        # 保存 Token 到数据库
        reset_token = ResetToken(
            token=token,
            user_id=user.id,
            expire_time=expire_time
        )
        
        db.session.add(reset_token)
        db.session.commit()
        
        # 发送重置邮件
        reset_url = f"http://{request.host}/reset-password.html?token={token}"
        
        email_content = f"""
        <html>
        <body>
            <h2>玄机算命网 - 密码重置</h2>
            <p>亲爱的 {user.username}，</p>
            <p>您请求重置密码，请点击以下链接（1小时内有效）：</p>
            <p><a href="{reset_url}">{reset_url}</a></p>
            <p>如果这不是您的操作，请忽略此邮件。</p>
        </body>
        </html>
        """
        
        send_email(email, '玄机算命网 - 密码重置', email_content)
        
        print(f"✅ 密码重置链接已生成：{reset_url}")
        
        return jsonify({
            'message': '密码重置链接已发送到您的邮箱',
            'reset_url': reset_url  # 演示模式：直接返回链接
        }), 200

# ==================== 重置密码 API ====================
@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    """重置密码"""
    data = request.get_json()
    
    token = data.get('token', '').strip()
    new_password = data.get('password', '')
    
    if not token or not new_password:
        return jsonify({'error': 'Token 和新密码不能为空'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': '新密码长度至少为6个字符'}), 400
    
    with app.app_context():
        # 查找 Token
        reset_token = ResetToken.query.filter_by(token=token, used=False).first()
        
        if not reset_token:
            return jsonify({'error': 'Token 无效或已使用'}), 400
        
        # 检查是否过期
        if datetime.utcnow() > reset_token.expire_time:
            return jsonify({'error': 'Token 已过期'}), 400
        
        # 查找用户
        user = User.query.get(reset_token.user_id)
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 更新密码
        user.password_hash = hash_password(new_password)
        
        # 标记 Token 已使用
        reset_token.used = True
        
        db.session.commit()
        
        print(f"✅ 密码重置成功：{user.username} (ID: {user.id})")
        
        return jsonify({'message': '密码重置成功'}), 200

# ==================== 健康监测 API ====================
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康监测"""
    try:
        # 检查数据库连接
        db.session.execute('SELECT 1')
        db_status = 'ok'
    except:
        db_status = 'error'
    
    return jsonify({
        'status': 'ok',
        'service': '玄机算命网-大数据联网实时分析系统',
        'version': '2.2.0',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# ==================== 算命历史记录 API ====================
@app.route('/api/divination-history', methods=['GET'])
def get_divination_history():
    """获取算命历史记录"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        token = request.cookies.get('token')
    
    if not token:
        return jsonify({'error': '未登录'}), 401
    
    user_id = verify_token(token, app.config['SECRET_KEY'])
    
    if not user_id:
        return jsonify({'error': 'Token 无效或已过期'}), 401
    
    with app.app_context():
        histories = DivinationHistory.query.filter_by(user_id=user_id).order_by(DivinationHistory.create_time.desc()).limit(50).all()
        
        return jsonify({
            'histories': [{
                'id': h.id,
                'module_name': h.module_name,
                'module_title': h.module_title,
                'input_data': json.loads(h.input_data) if h.input_data else None,
                'result_data': json.loads(h.result_data) if h.result_data else None,
                'create_time': h.create_time.isoformat()
            } for h in histories]
        }), 200

@app.route('/api/divination-history', methods=['POST'])
def add_divination_history():
    """添加算命历史记录"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        token = request.cookies.get('token')
    
    if not token:
        return jsonify({'error': '未登录'}), 401
    
    user_id = verify_token(token, app.config['SECRET_KEY'])
    
    if not user_id:
        return jsonify({'error': 'Token 无效或已过期'}), 401
    
    data = request.get_json()
    
    module_name = data.get('module_name', '')
    module_title = data.get('module_title', '')
    input_data = data.get('input_data')
    result_data = data.get('result_data')
    
    if not module_name or not module_title:
        return jsonify({'error': '模块名称和标题不能为空'}), 400
    
    with app.app_context():
        history = DivinationHistory(
            user_id=user_id,
            module_name=module_name,
            module_title=module_title,
            input_data=json.dumps(input_data, ensure_ascii=False) if input_data else None,
            result_data=json.dumps(result_data, ensure_ascii=False) if result_data else None
        )
        
        db.session.add(history)
        
        # 更新用户统计
        stats = UserStats.query.get(user_id)
        if stats:
            stats.divination_count += 1
            stats.last_update = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': '记录添加成功'}), 201

# ==================== 收藏 API ====================
@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """获取收藏列表"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        token = request.cookies.get('token')
    
    if not token:
        return jsonify({'error': '未登录'}), 401
    
    user_id = verify_token(token, app.config['SECRET_KEY'])
    
    if not user_id:
        return jsonify({'error': 'Token 无效或已过期'}), 401
    
    with app.app_context():
        favorites = Favorite.query.filter_by(user_id=user_id).order_by(Favorite.create_time.desc()).all()
        
        return jsonify({
            'favorites': [{
                'id': f.id,
                'module_name': f.module_name,
                'module_title': f.module_title,
                'create_time': f.create_time.isoformat()
            } for f in favorites]
        }), 200

@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    """添加收藏"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        token = request.cookies.get('token')
    
    if not token:
        return jsonify({'error': '未登录'}), 401
    
    user_id = verify_token(token, app.config['SECRET_KEY'])
    
    if not user_id:
        return jsonify({'error': 'Token 无效或已过期'}), 401
    
    data = request.get_json()
    
    module_name = data.get('module_name', '')
    module_title = data.get('module_title', '')
    
    if not module_name or not module_title:
        return jsonify({'error': '模块名称和标题不能为空'}), 400
    
    with app.app_context():
        # 检查是否已收藏
        existing = Favorite.query.filter_by(user_id=user_id, module_name=module_name).first()
        
        if existing:
            return jsonify({'error': '已经收藏过了'}), 400
        
        favorite = Favorite(
            user_id=user_id,
            module_name=module_name,
            module_title=module_title
        )
        
        db.session.add(favorite)
        
        # 更新用户统计
        stats = UserStats.query.get(user_id)
        if stats:
            stats.favorite_count += 1
            stats.last_update = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': '收藏成功'}), 201

@app.route('/api/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    """删除收藏"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        token = request.cookies.get('token')
    
    if not token:
        return jsonify({'error': '未登录'}), 401
    
    user_id = verify_token(token, app.config['SECRET_KEY'])
    
    if not user_id:
        return jsonify({'error': 'Token 无效或已过期'}), 401
    
    with app.app_context():
        favorite = Favorite.query.filter_by(id=favorite_id, user_id=user_id).first()
        
        if not favorite:
            return jsonify({'error': '收藏记录不存在'}), 404
        
        db.session.delete(favorite)
        
        # 更新用户统计
        stats = UserStats.query.get(user_id)
        if stats and stats.favorite_count > 0:
            stats.favorite_count -= 1
            stats.last_update = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': '取消收藏成功'}), 200

# ==================== Webhook API（用于 GitHub 自动更新）====================
@app.route('/update-secret-2026', methods=['POST'])
def auto_update():
    """自动更新端点（GitHub Webhook）"""
    import subprocess
    
    try:
        # 拉取最新代码
        result = subprocess.run(
            ['git', 'pull', 'origin', 'main'],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✅ 代码更新成功：{result.stdout}")
            
            # 重启服务（生产环境应由 systemd 或其他进程管理器处理）
            # os.system('systemctl restart xuanji-backend')
            
            return jsonify({
                'status': 'success',
                'message': '代码已更新',
                'output': result.stdout
            }), 200
        else:
            print(f"❌ 代码更新失败：{result.stderr}")
            return jsonify({
                'status': 'error',
                'message': '代码更新失败',
                'error': result.stderr
            }), 500
    except Exception as e:
        print(f"❌ 自动更新异常：{e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ==================== 主函数 ====================
if __name__ == '__main__':
    # 创建数据库表
    with app.app_context():
        db.create_all()
        print("✅ 数据库表已创建")
    
    # 启动应用
    app.run(host='0.0.0.0', port=5000, debug=True)
