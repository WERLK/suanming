#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整的注册+登录流程
"""
import requests, time, json, re

BASE_URL = "http://localhost:5000"

print("\n" + "="*60)
print("🧪 测试完整的注册+登录流程")
print("="*60)

# 1. 发送验证码
print("\n【1】发送验证码...")
resp = requests.post(f"{BASE_URL}/api/sendCode", 
                    json={"phone": "13800138000"})
data = resp.json()
print(f"响应：{data}")
assert data['code'] == 200, "发送验证码失败！"
print("✅ 验证码发送成功")

# 2. 读取验证码（从文件）
with open('/workspace/latest_code.txt', 'r') as f:
    content = f.read()
    code = re.search(r'验证码：(\d+)', content).group(1)
print(f"📂 验证码（从文件）：{code}")

# 3. 注册
print("\n【2】注册用户...")
resp = requests.post(f"{BASE_URL}/api/register",
                    json={"phone": "13800138000", "code": code, "password": "123456"})
data = resp.json()
print(f"响应：{data}")
assert data['code'] == 200, f"注册失败：{data['msg']}"
print(f"✅ 注册成功！用户：{data['data']['name']}")
print(f"   免费测算次数：{data['data']['free_count']}")

# 4. 重新发送验证码（用于登录）
print("\n【3】重新发送验证码（用于登录）...")
resp = requests.post(f"{BASE_URL}/api/sendCode",
                    json={"phone": "13800138000"})
data = resp.json()
assert data['code'] == 200
print("✅ 验证码重新发送成功")

# 5. 读取新验证码
time.sleep(1)
with open('/workspace/latest_code.txt', 'r') as f:
    content = f.read()
    new_code = re.search(r'验证码：(\d+)', content).group(1)
print(f"📂 新验证码（从文件）：{new_code}")

# 6. 登录
print("\n【4】验证码登录...")
resp = requests.post(f"{BASE_URL}/api/login",
                    json={"phone": "13800138000", "code": new_code})
data = resp.json()
print(f"响应：{data}")
assert data['code'] == 200, f"登录失败：{data['msg']}"
print(f"✅ 登录成功！用户：{data['data']['name']}")
print(f"   免费测算次数：{data['data']['free_count']}")

print("\n" + "="*60)
print("🎉 所有测试通过！API对接成功！")
print("="*60 + "\n")
