#!/usr/bin/env python3
"""测试api/app.py中的验证码生成函数"""
import sys
import os
import traceback

# 添加api目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("正在导入api/app.py...")
    from api.app import app, generate_captcha, generate_slider
    
    print("✓ 导入成功！")
    print("✓ 所有函数都可正常导入")
    
    # 测试验证码生成函数
    print("\n测试验证码生成函数...")
    with app.test_client() as client:
        response = client.get('/api/captcha/generate')
        print(f"  状态码: {response.status_code}")
        data = response.get_json()
        print(f"  响应: {data}")
        
        if response.status_code == 200 and data.get('success'):
            print("  ✓ 验证码生成成功！")
        else:
            print("  ✗ 验证码生成失败！")
            sys.exit(1)
    
    # 测试滑块验证码生成函数
    print("\n测试滑块验证码生成函数...")
    with app.test_client() as client:
        response = client.get('/api/slider/generate')
        print(f"  状态码: {response.status_code}")
        data = response.get_json()
        print(f"  响应: {data}")
        
        if response.status_code == 200 and data.get('success'):
            print("  ✓ 滑块验证码生成成功！")
        else:
            print("  ✗ 滑块验证码生成失败！")
            sys.exit(1)
    
    print("\n🎉 所有测试通过！")
    sys.exit(0)
    
except Exception as e:
    print(f"\n✗ 错误: {e}")
    traceback.print_exc()
    sys.exit(1)
