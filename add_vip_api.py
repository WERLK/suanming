#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加会员开通API到server.py
"""

with open('/workspace/server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 在logout API后添加upgrade_vip API
upgrade_vip_code = '''
# ===== 10. 开通会员 =====
@app.route('/api/upgrade_vip', methods=['POST'])
def upgrade_vip():
    """
    开通/续费会员
    
    请求参数：
    - phone: 手机号
    - duration: 时长（月）
    - pay_method: 支付方式（wechat/alipay/qq）
    - amount: 支付金额
    
    返回：
    - code: 200成功
    - data: 更新后的用户信息
    """
    phone = request.json.get('phone', '').strip()
    duration = request.json.get('duration', 1)
    pay_method = request.json.get('pay_method', 'wechat')
    amount = request.json.get('amount', 0)
    
    # 验证参数
    if not phone:
        return jsonify({"code": 400, "msg": "手机号不能为空"}), 200
    
    if duration not in [1, 3, 12]:
        return jsonify({"code": 400, "msg": "时长只能是1/3/12个月"}), 200
    
    # 查找用户
    db = read_db()
    user = next((u for u in db['users'] if u['phone'] == phone), None)
    
    if not user:
        return jsonify({"code": 400, "msg": "用户不存在"}), 200
    
    # 计算新的过期时间
    current_time = time.time()
    
    # 如果已经是VIP且未过期，延长有效期；否则从当前时间计算
    if user.get('is_vip') and user.get('vip_expire', 0) > current_time:
        new_expire = user['vip_expire'] + duration * 30 * 24 * 3600
    else:
        new_expire = current_time + duration * 30 * 24 * 3600
    
    # 更新用户信息
    user['is_vip'] = True
    user['vip_expire'] = new_expire
    
    # 根据时长设置会员类型
    if duration == 1:
        user['vip_type'] = '月度会员'
    elif duration == 3:
        user['vip_type'] = '季度会员'
    else:
        user['vip_type'] = '年度会员'
    
    # 记录支付信息（实际项目中应写入支付记录表）
    if 'pay_history' not in user:
        user['pay_history'] = []
    
    user['pay_history'].append({
        "amount": amount,
        "duration": duration,
        "pay_method": pay_method,
        "pay_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "vip_type": user['vip_type']
    })
    
    # 保存数据库
    write_db(db)
    
    # 模拟支付成功（实际项目中应调用支付API）
    print(f"\\n【模拟支付】手机号 {phone} 支付 ¥{amount} 开通 {user['vip_type']}")
    print(f"【模拟支付】支付方式：{pay_method}")
    print(f"【模拟支付】有效期至：{time.strftime('%Y-%m-%d', time.localtime(new_expire))}\\n")
    
    return jsonify({
        "code": 200,
        "msg": "会员开通成功",
        "data": {
            "phone": user['phone'],
            "name": user['name'],
            "avatar": user['avatar'],
            "is_vip": user['is_vip'],
            "vip_expire": user['vip_expire'],
            "vip_type": user['vip_type'],
            "free_count": user.get('free_count', 0)
        }
    }), 200

'''

# 在logout API后插入（在# ===== 8. 腾讯云登录前）
insertion_point = '# ===== 8. 腾讯云登录（微信）====='
content = content.replace(insertion_point, upgrade_vip_code + insertion_point)

# 更新API文档注释
old_doc = '''"""
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
"""'''

new_doc = '''"""
Mock API Server for 玄机算命网
提供以下接口：
1. POST /api/sendCode         - 发送验证码
2. POST /api/login             - 验证码登录
3. POST /api/password_login   - 密码登录
4. POST /api/register          - 验证码注册
5. POST /api/forgot_password  - 找回密码（重置密码）
6. GET  /api/user/<phone>    - 获取用户信息
7. POST /api/logout            - 退出登录
8. POST /api/upgrade_vip      - 开通会员
9. POST /api/tencent_login    - 腾讯云登录（微信）
10. POST /api/qq_login         - QQ登录
11. POST /api/github_login     - GitHub登录
"""'''

content = content.replace(old_doc, new_doc)

# 写回文件
with open('/workspace/server.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 后端会员开通API已添加")
print("  - 新增 /api/upgrade_vip 接口")
print("  - 支持1/3/12个月时长")
print("  - 支持微信/支付宝/QQ支付")
print("  - 自动计算会员有效期")
print("  - 记录支付历史")
