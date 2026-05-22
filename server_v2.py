#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mock API Server for 玄机算命网
提供以下接口：
1. POST /api/sendCode         - 发送验证码
2. POST /api/login             - 验证码登录
3. POST /api/password_login   - 密码登录
4. POST /api/register          - 验证码注册
5. POST /api/forgot_password  - 找回密码（重置密码）
6. GET  /api/user/<phone>    - 获取用户信息
7. POST /api/logout            - 退出登录
8. POST /api/tencent_login    - 腾讯云登录（微信）
9. POST /api/qq_login         - QQ登录
10. POST /api/github_login     - GitHub登录
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json, time, random, os

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # 允许跨域

# ===== 数据文件 =====
DB_FILE = '/workspace/users.json'
CODE_FILE = '/workspace/latest_code.txt'  # 存储最新验证码（方便测试）

def read_db():
    """读取数据库"""
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        # 如果文件不存在，创建空数据库
        return {"users": [], "codes": {}}

def write_db(data):
    """写入数据库"""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ===== 1. 发送验证码 =====
@app.route('/api/sendCode', methods=['POST'])
def send_code():
    phone = request.json.get('phone', '').strip()
    
    # 验证手机号
    if not phone or len(phone) != 11 or not phone.isdigit():
        return jsonify({"code": 400, "msg": "手机号格式错误"}), 200
    
    # 生成6位验证码
    code = str(random.randint(100000, 999999))
    
    # 存储验证码（5分钟有效）
    db = read_db()
    db['codes'][phone] = {
        'code': code,
        'expire': time.time() + 300  # 5分钟后过期
    }
    write_db(db)
    
    # 写入文件（方便测试查看）
    with open(CODE_FILE, 'w') as f:
        f.write(f"手机号：{phone}\n验证码：{code}\n有效期：5分钟\n时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 模拟发送短信（实际项目中应调用短信服务商的API）
    print(f"\n【模拟短信】手机号 {phone} 的验证码是：{code}")
    print(f"【模拟短信】验证码5分钟内有效\n")
    
    return jsonify({"code": 200, "msg": "验证码已发送"}), 200

# ===== 2. 验证码登录 =====
@app.route('/api/login', methods=['POST'])
def login():
    phone = request.json.get('phone', '').strip()
    code = request.json.get('code', '').strip()
    
    # 验证参数
    if not phone or not code:
        return jsonify({"code": 400, "msg": "手机号和验证码不能为空"}), 200
    
    # 检查验证码
    db = read_db()
    record = db['codes'].get(phone)
    
    if not record:
        return jsonify({"code": 400, "msg": "请先获取验证码"}), 200
    
    if record['code'] != code:
        return jsonify({"code": 400, "msg": "验证码错误"}), 200
    
    if time.time() > record['expire']:
        return jsonify({"code": 400, "msg": "验证码已过期，请重新获取"}), 200
    
    # 检查用户是否存在
    user = next((u for u in db['users'] if u['phone'] == phone), None)
    
    if not user:
        return jsonify({"code": 400, "msg": "用户不存在，请先注册"}), 200
    
    # 登录成功，删除验证码（一次性）
    del db['codes'][phone]
    write_db(db)
    
    return jsonify({
        "code": 200,
        "msg": "登录成功",
        "data": {
            "phone": user['phone'],
            "name": user['name'],
            "avatar": user['avatar'],
            "free_count": user.get('free_count', 0)
        }
    }), 200

# ===== 3. 密码登录 =====
@app.route('/api/password_login', methods=['POST'])
def password_login():
    phone = request.json.get('phone', '').strip()
    password = request.json.get('password', '')
    
    # 验证参数
    if not phone or not password:
        return jsonify({"code": 400, "msg": "手机号和密码不能为空"}), 200
    
    # 检查用户是否存在
    db = read_db()
    user = next((u for u in db['users'] if u['phone'] == phone), None)
    
    if not user:
        return jsonify({"code": 400, "msg": "用户不存在，请先注册"}), 200
    
    # 验证密码（实际项目中应使用 bcrypt 验证）
    if user.get('password') != password:
        return jsonify({"code": 400, "msg": "密码错误"}), 200
    
    return jsonify({
        "code": 200,
        "msg": "登录成功",
        "data": {
            "phone": user['phone'],
            "name": user['name'],
            "avatar": user['avatar'],
            "free_count": user.get('free_count', 0)
        }
    }), 200

# ===== 4. 验证码注册 =====
@app.route('/api/register', methods=['POST'])
def register():
    phone = request.json.get('phone', '').strip()
    code = request.json.get('code', '').strip()
    password = request.json.get('password', '')
    
    # 验证参数
    if not phone or not code or not password:
        return jsonify({"code": 400, "msg": "手机号、验证码和密码不能为空"}), 200
    
    if len(password) < 6:
        return jsonify({"code": 400, "msg": "密码至少6位"}), 200
    
    # 检查验证码
    db = read_db()
    record = db['codes'].get(phone)
    
    if not record:
        return jsonify({"code": 400, "msg": "请先获取验证码"}), 200
    
    if record['code'] != code:
        return jsonify({"code": 400, "msg": "验证码错误"}), 200
    
    if time.time() > record['expire']:
        return jsonify({"code": 400, "msg": "验证码已过期，请重新获取"}), 200
    
    # 检查用户是否已存在
    if any(u['phone'] == phone for u in db['users']):
        return jsonify({"code": 400, "msg": "该手机号已注册，请直接登录"}), 200
    
    # 创建新用户
    new_user = {
        "phone": phone,
        "name": "用户" + phone[-4:],  # 默认用户名（后4位）
        "avatar": "👤",
        "password": password,  # 注意：实际项目中密码应加密存储
        "free_count": 3,  # 新用户送3次免费测算
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    db['users'].append(new_user)
    
    # 删除验证码（一次性）
    del db['codes'][phone]
    
    write_db(db)
    
    return jsonify({
        "code": 200,
        "msg": "注册成功，送3次免费测算",
        "data": {
            "phone": new_user['phone'],
            "name": new_user['name'],
            "avatar": new_user['avatar'],
            "free_count": new_user['free_count']
        }
    }), 200

# ===== 5. 获取用户信息 =====
@app.route('/api/user/<phone>', methods=['GET'])
def get_user(phone):
    db = read_db()
    user = next((u for u in db['users'] if u['phone'] == phone), None)
    
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 200
    
    return jsonify({
        "code": 200,
        "msg": "获取成功",
        "data": {
            "phone": user['phone'],
            "name": user['name'],
            "avatar": user['avatar'],
            "free_count": user.get('free_count', 0)
        }
    }), 200

# ===== 6. 找回密码（重置密码）=====
@app.route('/api/forgot_password', methods=['POST'])
def forgot_password():
    phone = request.json.get('phone', '').strip()
    code = request.json.get('code', '').strip()
    new_password = request.json.get('new_password', '')
    
    # 验证参数
    if not phone or not code or not new_password:
        return jsonify({"code": 400, "msg": "手机号、验证码和新密码不能为空"}), 200
    
    if len(new_password) < 6:
        return jsonify({"code": 400, "msg": "新密码至少6位"}), 200
    
    # 检查验证码
    db = read_db()
    record = db['codes'].get(phone)
    
    if not record:
        return jsonify({"code": 400, "msg": "请先获取验证码"}), 200
    
    if record['code'] != code:
        return jsonify({"code": 400, "msg": "验证码错误"}), 200
    
    if time.time() > record['expire']:
        return jsonify({"code": 400, "msg": "验证码已过期，请重新获取"}), 200
    
    # 检查用户是否存在
    user = next((u for u in db['users'] if u['phone'] == phone), None)
    
    if not user:
        return jsonify({"code": 400, "msg": "用户不存在"}), 200
    
    # 更新密码
    user['password'] = new_password
    
    # 删除验证码（一次性）
    del db['codes'][phone]
    
    write_db(db)
    
    return jsonify({"code": 200, "msg": "密码重置成功，请使用新密码登录"}), 200

# ===== 7. 退出登录 =====
@app.route('/api/logout', methods=['POST'])
def logout():
    return jsonify({"code": 200, "msg": "退出成功"}), 200

# ===== 8. 腾讯云登录（微信）=====
@app.route('/api/tencent_login', methods=['POST'])
def tencent_login():
    """
    腾讯云登录接口（示例实现）
    
    实际对接时需要的步骤：
    1. 在腾讯云官网注册账号：https://cloud.tencent.com/
    2. 开通"云开发"服务，获取环境ID
    3. 在小程序/Web端集成腾讯云SDK
    4. 前端调用 wx.login() 获取code，传给后端
    5. 后端用code调用腾讯云API换取openid和session_key
    6. 根据openid查找或创建用户
    
    文档：https://cloud.tencent.com/document/product/378
    """
    code = request.json.get('code', '')
    encrypted_data = request.json.get('encryptedData', '')
    iv = request.json.get('iv', '')
    
    if not code:
        return jsonify({"code": 400, "msg": "code不能为空"}), 200
    
    try:
        # TODO: 实际项目中，这里应该调用腾讯云API
        # 示例代码（需要安装 tencentcloud-sdk-python）：
        #
        # from tencentcloud.common import credential
        # from tencentcloud.scf.v20180416 import scf_client, models
        # 
        # cred = credential.Credential(secret_id, secret_key)
        # client = scf_client.ScfClient(cred, "ap-guangzhou")
        # req = models.InvokeRequest()
        # req.FunctionName = "login-with-code"
        # resp = client.Invoke(req)
        
        # 模拟成功响应
        mock_openid = "oXZYA5XXXXXXXXXXXXXX"
        mock_session_key = "XXXXXXXXXXXX=="
        
        # 查找或创建用户
        db = read_db()
        user = next((u for u in db['users'] if u.get('openid') == mock_openid), None)
        
        if not user:
            # 创建新用户
            new_user = {
                "phone": "tmp_" + mock_openid[-8:],
                "name": "微信用户" + str(random.randint(1000, 9999)),
                "avatar": "👤",
                "password": "",
                "openid": mock_openid,
                "session_key": mock_session_key,
                "free_count": 3,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            db['users'].append(new_user)
            write_db(db)
            user = new_user
        
        return jsonify({
            "code": 200,
            "msg": "登录成功（腾讯云Mock）",
            "data": {
                "phone": user['phone'],
                "name": user['name'],
                "avatar": user['avatar'],
                "free_count": user.get('free_count', 0)
            }
        }), 200
        
    except Exception as e:
        print(f"腾讯云登录失败: {str(e)}")
        return jsonify({"code": 500, "msg": f"登录失败: {str(e)}"}), 200

# ===== 9. QQ登录 =====
@app.route('/api/qq_login', methods=['POST'])
def qq_login():
    """
    QQ登录接口（示例实现）
    
    实际对接时需要的步骤：
    1. 在QQ互联注册应用：https://connect.qq.com/
    2. 获取APP_ID和APP_KEY
    3. 前端引导用户跳转到QQ授权页面
    4. 用户授权后，QQ回调并带上code
    5. 后端用code换取access_token和openid
    6. 根据openid查找或创建用户
    
    文档：https://wiki.connect.qq.com/oauth2.0/
    """
    access_token = request.json.get('access_token', '')
    openid = request.json.get('openid', '')
    
    if not access_token or not openid:
        return jsonify({"code": 400, "msg": "access_token和openid不能为空"}), 200
    
    try:
        # TODO: 实际项目中，这里应该调用QQ互联API
        # 示例代码：
        # import requests
        # url = f"https://graph.qq.com/user/get_user_info?access_token={access_token}&oauth_consumer_key={APP_ID}&openid={openid}"
        # resp = requests.get(url)
        # user_info = resp.json()
        # nickname = user_info.get('nickname', '')
        # avatar = user_info.get('figureurl_qq_2', '')
        
        # 模拟成功响应
        mock_nickname = "QQ用户" + str(random.randint(1000, 9999))
        mock_avatar = "🐧"
        
        # 查找或创建用户
        db = read_db()
        user = next((u for u in db['users'] if u.get('openid') == openid), None)
        
        if not user:
            # 创建新用户
            new_user = {
                "phone": "qq_" + openid[-8:],
                "name": mock_nickname,
                "avatar": mock_avatar,
                "password": "",
                "openid": openid,
                "free_count": 3,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            db['users'].append(new_user)
            write_db(db)
            user = new_user
        
        return jsonify({
            "code": 200,
            "msg": "登录成功（QQ Mock）",
            "data": {
                "phone": user['phone'],
                "name": user['name'],
                "avatar": user['avatar'],
                "free_count": user.get('free_count', 0)
            }
        }), 200
        
    except Exception as e:
        print(f"QQ登录失败: {str(e)}")
        return jsonify({"code": 500, "msg": f"登录失败: {str(e)}"}), 200

# ===== 10. GitHub登录 =====
@app.route('/api/github_login', methods=['POST'])
def github_login():
    """
    GitHub登录接口（示例实现）
    
    实际对接时需要的步骤：
    1. 在GitHub注册OAuth App：https://github.com/settings/developers
    2. 获取Client ID和Client Secret
    3. 前端引导用户跳转到GitHub授权页面
    4. 用户授权后，GitHub回调并带上code
    5. 后端用code换取access_token
    6. 用access_token调用GitHub API获取用户信息
    7. 根据GitHub ID查找或创建用户
    
    文档：https://docs.github.com/en/developers/apps/building-oauth-apps
    """
    code = request.json.get('code', '')
    
    if not code:
        return jsonify({"code": 400, "msg": "code不能为空"}), 200
    
    try:
        # TODO: 实际项目中，这里应该调用GitHub API
        # 示例代码：
        # import requests
        # # 1. 用code换取access_token
        # token_url = "https://github.com/login/oauth/access_token"
        # token_data = {
        #     "client_id": CLIENT_ID,
        #     "client_secret": CLIENT_SECRET,
        #     "code": code
        # }
        # token_resp = requests.post(token_url, data=token_data)
        # access_token = token_resp.json().get('access_token')
        # 
        # # 2. 获取用户信息
        # user_url = "https://api.github.com/user"
        # headers = {"Authorization": f"token {access_token}"}
        # user_resp = requests.get(user_url, headers=headers)
        # user_info = user_resp.json()
        # github_id = user_info['id']
        # github_name = user_info['name'] or user_info['login']
        # github_avatar = user_info['avatar_url']
        
        # 模拟成功响应
        mock_github_id = random.randint(10000, 99999)
        mock_name = "GitHub用户" + str(mock_github_id)
        mock_avatar = "🐙"
        
        # 查找或创建用户
        db = read_db()
        user = next((u for u in db['users'] if u.get('github_id') == mock_github_id), None)
        
        if not user:
            # 创建新用户
            new_user = {
                "phone": "gh_" + str(mock_github_id),
                "name": mock_name,
                "avatar": mock_avatar,
                "password": "",
                "github_id": mock_github_id,
                "free_count": 3,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            db['users'].append(new_user)
            write_db(db)
            user = new_user
        
        return jsonify({
            "code": 200,
            "msg": "登录成功（GitHub Mock）",
            "data": {
                "phone": user['phone'],
                "name": user['name'],
                "avatar": user['avatar'],
                "free_count": user.get('free_count', 0)
            }
        }), 200
        
    except Exception as e:
        print(f"GitHub登录失败: {str(e)}")
        return jsonify({"code": 500, "msg": f"登录失败: {str(e)}"}), 200

# ===== 健康检查 =====
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"code": 200, "msg": "API服务正常"}), 200

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 玄机算命网 - Mock API服务器启动中...")
    print("="*60)
    print(f"📁 数据库文件：{DB_FILE}")
    print(f"📂 验证码文件：{CODE_FILE}")
    print(f"🌐 API地址：<ADDRESS_REMOVED>
    print("="*60 + "\n")
    
    # 确保数据库文件存在
    if not os.path.exists(DB_FILE):
        write_db({"users": [], "codes": {}})
        print(f"✅ 已创建数据库文件：{DB_FILE}\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
