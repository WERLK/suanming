#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为 server.py 添加密码登录和找回密码接口
"""

# 读取原文件
with open('/workspace/server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ===== 1. 添加密码登录接口（在验证码登录前）=====
# 找到 "def login():" 的位置，在其前面插入 password_login()
insert_pos = content.find('@app.route(\'/api/login\'')

new_password_login = '''
# ===== 2. 密码登录 =====
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

'''

content = content[:insert_pos] + new_password_login + content[insert_pos:]

# ===== 2. 添加找回密码接口 =====
# 在 register 函数后插入 forgot_password()
insert_pos2 = content.find('@app.route(\'/api/user/')

new_forgot_password = '''
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

'''

content = content[:insert_pos2] + new_forgot_password + content[insert_pos2:]

# ===== 3. 更新接口列表注释 =====
old_doc = '''提供以下接口：
1. POST /api/sendCode    - 发送验证码
2. POST /api/login      - 验证码登录
3. POST /api/register   - 验证码注册
4. GET  /api/user/<phone> - 获取用户信息
5. POST /api/logout     - 退出登录'''

new_doc = '''提供以下接口：
1. POST /api/sendCode         - 发送验证码
2. POST /api/login             - 验证码登录
3. POST /api/password_login   - 密码登录
4. POST /api/register          - 验证码注册
5. POST /api/forgot_password  - 找回密码（重置密码）
6. GET  /api/user/<phone>    - 获取用户信息
7. POST /api/logout            - 退出登录'''

content = content.replace(old_doc, new_doc)

# 写回文件
with open('/workspace/server.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ server.py 已更新')
print('  - 添加：POST /api/password_login (密码登录)')
print('  - 添加：POST /api/forgot_password (找回密码)')
print('  - 更新接口列表注释')
