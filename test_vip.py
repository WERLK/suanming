#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试会员开通功能
"""

import requests
import time
import os

BASE_URL = "<NAL_URL>"

print("=== 测试会员开通功能 ===\n")

# 1. 发送验证码
print("[1] 发送验证码...")
resp = requests.post(f"{BASE_URL}/api/sendCode", json={"phone": "13800138000"})
print(f"  状态: {resp.status_code}")
print(f"  响应: {resp.json()}")

# 2. 读取验证码
time.sleep(1)
with open('/workspace/latest_code.txt', 'r') as f:
    content = f.read()
    code = content.split('验证码：')[1].split('\n')[0].strip()
    print(f"\n[2] 验证码: {code}")

# 3. 登录
print("\n[3] 验证码登录...")
resp = requests.post(f"{BASE_URL}/api/login", json={"phone": "13800138000", "code": code})
result = resp.json()
print(f"  状态: {resp.status_code}")
print(f"  响应: {result}")

if result.get('code') == 200:
    user = result.get('data')
    print(f"\n  用户信息:")
    print(f"  - 手机号: {user.get('phone')}")
    print(f"  - 姓名: {user.get('name')}")
    print(f"  - 是否VIP: {user.get('is_vip')}")
    print(f"  - VIP类型: {user.get('vip_type')}")
    print(f"  - VIP过期: {user.get('vip_expire')}")

# 4. 测试会员开通API
print("\n[4] 测试会员开通API...")
resp = requests.post(f"{BASE_URL}/api/upgrade_vip", json={
    "phone": "13800138000",
    "duration": 1,
    "pay_method": "wechat",
    "amount": 29
})
result = resp.json()
print(f"  状态: {resp.status_code}")
print(f"  响应: {result}")

if result.get('code') == 200:
    data = result.get('data')
    print(f"\n  开通结果:")
    print(f"  - 是否VIP: {data.get('is_vip')}")
    print(f"  - VIP类型: {data.get('vip_type')}")
    print(f"  - VIP过期: {data.get('vip_expire')}")

print("\n=== 测试完成 ===")
