#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试密码登录和找回密码接口
"""
import requests, json, time, re

BASE = "http://localhost:5000"

print("\n" + "="*60)
print("🧪 测试密码登录和找回密码")
print("="*60)

# ===== 1. 测试密码登录 =====
print("\n【1】测试密码登录...")
resp = requests.post(f"{BASE}/api/password_login",
                    json={"phone": "13800138000", "password": "123456"})
data = resp.json()
print(f"响应：{data}")
assert data['code'] == 200, f"密码登录失败：{data['msg']}"
print(f"✅ 密码登录成功！用户：{data['data']['name']}")
print(f"   免费测算次数：{data['data']['free_count']}")

# ===== 2. 测试找回密码（需要先发送验证码）=====
print("\n【2】测试找回密码...")

# 2.1 发送验证码
print("  2.1 发送验证码...")
resp = requests.post(f"{BASE}/api/sendCode",
                    json={"phone": "13800138000"})
data = resp.json()
assert data['code'] == 200
print(f"  ✅ 验证码发送成功")

# 2.2 读取验证码
time.sleep(1)
with open('/workspace/latest_code.txt', 'r') as f:
    content = f.read()
    code = re.search(r'验证码：(\d+)', content).group(1)
print(f"  📂 验证码（从文件）：{code}")

# 2.3 找回密码（重置密码）
new_pwd = "newpassword123"
print(f"  2.2 重置密码为：{new_pwd}...")
resp = requests.post(f"{BASE}/api/forgot_password",
                    json={"phone": "13800138000", "code": code, "new_password": new_pwd})
data = resp.json()
print(f"  响应：{data}")
assert data['code'] == 200, f"找回密码失败：{data['msg']}"
print(f"  ✅ 密码重置成功！")

# 2.4 使用新密码登录
print(f"\n【3】使用新密码登录...")
resp = requests.post(f"{BASE}/api/password_login",
                    json={"phone": "13800138000", "password": new_pwd})
data = resp.json()
assert data['code'] == 200, f"新密码登录失败：{data['msg']}"
print(f"✅ 新密码登录成功！用户：{data['data']['name']}")

# ===== 3. 恢复原来的密码（方便后续测试）=====
print("\n【4】恢复原来的密码...")
# 发送验证码
resp = requests.post(f"{BASE}/api/sendCode",
                    json={"phone": "13800138000"})
data = resp.json()
assert data['code'] == 200

# 读取验证码
time.sleep(1)
with open('/workspace/latest_code.txt', 'r') as f:
    content = f.read()
    code = re.search(r'验证码：(\d+)', content).group(1)

# 重置为原密码
resp = requests.post(f"{BASE}/api/forgot_password",
                    json={"phone": "13800138000", "code": code, "new_password": "123456"})
data = resp.json()
assert data['code'] == 200
print(f"✅ 密码已恢复为：123456")

print("\n" + "="*60)
print("🎉 所有测试通过！")
print("="*60 + "\n")

# 打印所有API接口
print("📡 所有API接口列表：")
print("  1. POST /api/sendCode        - 发送验证码")
print("  2. POST /api/login            - 验证码登录")
print("  3. POST /api/password_login  - 密码登录")
print("  4. POST /api/register         - 验证码注册")
print("  5. POST /api/forgot_password - 找回密码（重置密码）")
print("  6. GET  /api/user/<phone>   - 获取用户信息")
print("  7. POST /api/logout           - 退出登录")
print("  8. GET  /api/health          - 健康检查\n")
