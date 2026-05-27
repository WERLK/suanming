"""
数据库配置和模型
使用 SQLite 作为数据库（轻量级，无需额外安装）
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import jwt
import hashlib
import random
import string

# 创建 SQLAlchemy 实例
db = SQLAlchemy()

class User(db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(64), primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True, index=True)
    phone = db.Column(db.String(11), unique=True, nullable=True, index=True)
    avatar = db.Column(db.String(255), nullable=True)
    birthday = db.Column(db.Date, nullable=True)
    gender = db.Column(db.Enum('male', 'female', 'other'), nullable=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.Enum('active', 'disabled'), default='active')
    
    # 关系
    stats = db.relationship('UserStats', backref='user', uselist=False, cascade='all, delete-orphan')
    tokens = db.relationship('ResetToken', backref='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'


class UserStats(db.Model):
    """用户统计表"""
    __tablename__ = 'user_stats'
    
    user_id = db.Column(db.String(64), db.ForeignKey('users.id'), primary_key=True)
    divination_count = db.Column(db.Integer, default=0)
    favorite_count = db.Column(db.Integer, default=0)
    last_update = db.Column(db.DateTime, default=datetime.utcnow)


class ResetToken(db.Model):
    """重置密码 Token 表"""
    __tablename__ = 'reset_tokens'
    
    token = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey('users.id'), nullable=False)
    expire_time = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)


class DivinationHistory(db.Model):
    """算命历史记录表"""
    __tablename__ = 'divination_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey('users.id'), nullable=False, index=True)
    module_name = db.Column(db.String(50), nullable=False)  # 模块名称（如：bazi, tarot）
    module_title = db.Column(db.String(100), nullable=False)  # 模块标题（如：八字算命）
    input_data = db.Column(db.Text, nullable=True)  # 输入数据（JSON 格式）
    result_data = db.Column(db.Text, nullable=True)  # 结果数据（JSON 格式）
    create_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        db.Index('idx_user_module', 'user_id', 'module_name'),
    )


class Favorite(db.Model):
    """收藏表"""
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(64), db.ForeignKey('users.id'), nullable=False, index=True)
    module_name = db.Column(db.String(50), nullable=False)
    module_title = db.Column(db.String(100), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'module_name', name='uniq_user_module'),
    )


# 密码加密函数
def hash_password(password, salt=None):
    """加密密码"""
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
    """验证密码"""
    try:
        salt, _ = hashed.split('$')
        return hash_password(password, salt) == hashed
    except:
        return False


# JWT Token 函数
def generate_token(user_id, secret_key):
    """生成 JWT Token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


def verify_token(token, secret_key):
    """验证 JWT Token"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload['user_id']
    except Exception:
        return None


# 数据库初始化函数
def init_db(app):
    """初始化数据库"""
    db.init_app(app)
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        
        # 检查是否需要从 JSON 文件迁移数据
        import os
        from flask import current_app
        
        json_file = os.path.join(app.config['DATA_DIR'], 'users.json')
        if os.path.exists(json_file):
            import json
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    users_data = json.load(f)
                
                # 迁移用户数据
                for user_data in users_data:
                    user = User.query.get(user_data['id'])
                    if user is None:
                        user = User(
                            id=user_data['id'],
                            username=user_data['username'],
                            password_hash=user_data['password'],
                            email=user_data.get('email'),
                            phone=user_data.get('phone'),
                            create_time=datetime.fromisoformat(user_data['create_time']) if user_data.get('create_time') else datetime.utcnow()
                        )
                        db.session.add(user)
                
                db.session.commit()
                print(f"✅ 成功迁移 {len(users_data)} 个用户到数据库")
                
                # 备份 JSON 文件
                backup_file = json_file + '.backup'
                os.rename(json_file, backup_file)
                print(f"✅ JSON 文件已备份到: {backup_file}")
                
            except Exception as e:
                print(f"❌ 数据迁移失败: {e}")
                db.session.rollback()
