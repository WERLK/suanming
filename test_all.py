#!/usr/bin/env python3
"""
玄机算命网 - 登录注册功能自动化测试脚本
测试所有API接口和前端页面
"""

import requests
import json
import sys
import time
import os
from datetime import datetime

# 配置
BASE_URL = 'http://localhost:8080'
API_URL = 'http://localhost:5000'

class Color:
    """终端颜色"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(test_name, passed, message=''):
    """打印测试结果"""
    if passed:
        status = f"{Color.GREEN}✓ 通过{Color.END}"
    else:
        status = f"{Color.RED}✗ 失败{Color.END}"
    
    print(f"  {status} {test_name}: {message}")
    return passed

def test_api_register():
    """测试注册接口"""
    print(f"\n{Color.BLUE}测试1: 用户注册 API{Color.END}")
    
    # 测试1.1: 正常注册
    data = {
        'username': 'testuser123',
        'password': 'Test@123456',
        'email': 'test123@example.com',
        'phone': '13800138000'
    }
    
    try:
        response = requests.post(f'{API_URL}/api/register', json=data)
        result = response.json()
        
        if response.status_code == 201 and result.get('success'):
            print_test("正常注册", True, f"用户ID: {result['user']['id'][:20]}...")
        else:
            print_test("正常注册", False, result.get('message', '未知错误'))
            return False
    except Exception as e:
        print_test("正常注册", False, f"异常: {str(e)}")
        return False
    
    # 测试1.2: 重复用户名
    try:
        response = requests.post(f'{API_URL}/api/register', json=data)
        result = response.json()
        
        if not result.get('success') and '已存在' in result.get('message', ''):
            print_test("重复用户名检查", True, "正确拒绝重复用户名")
        else:
            print_test("重复用户名检查", False, "应拒绝重复用户名")
    except Exception as e:
        print_test("重复用户名检查", False, f"异常: {str(e)}")
    
    # 测试1.3: 密码过短
    data2 = {
        'username': 'testuser456',
        'password': '123',
        'email': 'test456@example.com'
    }
    
    try:
        response = requests.post(f'{API_URL}/api/register', json=data2)
        result = response.json()
        
        if not result.get('success'):
            print_test("密码长度验证", True, "正确拒绝短密码")
        else:
            print_test("密码长度验证", False, "应拒绝短密码")
    except Exception as e:
        print_test("密码长度验证", False, f"异常: {str(e)}")
    
    return True

def test_api_login():
    """测试登录接口"""
    print(f"\n{Color.BLUE}测试2: 用户登录 API{Color.END}")
    
    # 测试2.1: 正常登录
    data = {
        'username': 'testuser123',
        'password': 'Test@123456',
        'remember': True
    }
    
    try:
        response = requests.post(f'{API_URL}/api/login', json=data)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print_test("正常登录", True, f"Token长度: {len(result['token'])}")
            return result['token']
        else:
            print_test("正常登录", False, result.get('message', '未知错误'))
            return None
    except Exception as e:
        print_test("正常登录", False, f"异常: {str(e)}")
        return None

def test_api_profile(token):
    """测试获取用户信息接口"""
    print(f"\n{Color.BLUE}测试3: 获取用户信息 API{Color.END}")
    
    if not token:
        print_test("获取用户信息", False, "无token，跳过测试")
        return False
    
    # 测试3.1: 使用有效token
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{API_URL}/api/profile', headers=headers)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print_test("获取用户信息（有效token）", True, f"用户名: {result['user']['username']}")
        else:
            print_test("获取用户信息（有效token）", False, result.get('message', '未知错误'))
    except Exception as e:
        print_test("获取用户信息（有效token）", False, f"异常: {str(e)}")
    
    # 测试3.2: 使用无效token
    try:
        headers = {'Authorization': 'Bearer invalid_token'}
        response = requests.get(f'{API_URL}/api/profile', headers=headers)
        result = response.json()
        
        if response.status_code == 401 and not result.get('success'):
            print_test("获取用户信息（无效token）", True, "正确拒绝无效token")
        else:
            print_test("获取用户信息（无效token）", False, "应拒绝无效token")
    except Exception as e:
        print_test("获取用户信息（无效token）", False, f"异常: {str(e)}")
    
    return True

def test_api_update_profile(token):
    """测试更新用户信息接口"""
    print(f"\n{Color.BLUE}测试4: 更新用户信息 API{Color.END}")
    
    if not token:
        print_test("更新用户信息", False, "无token，跳过测试")
        return False
    
    try:
        headers = {'Authorization': f'Bearer {token}'}
        data = {
            'username': 'testuser123_updated',
            'email': 'updated@example.com',
            'gender': 'male'
        }
        
        response = requests.put(f'{API_URL}/api/profile', json=data, headers=headers)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print_test("更新用户信息", True, f"新用户名: {result['user']['username']}")
        else:
            print_test("更新用户信息", False, result.get('message', '未知错误'))
    except Exception as e:
        print_test("更新用户信息", False, f"异常: {str(e)}")
    
    return True

def test_api_forgot_password():
    """测试忘记密码接口"""
    print(f"\n{Color.BLUE}测试5: 忘记密码 API{Color.END}")
    
    # 测试5.1: 有效邮箱
    data = {'email': 'updated@example.com'}
    
    try:
        response = requests.post(f'{API_URL}/api/forgot-password', json=data)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print_test("忘记密码（有效邮箱）", True, "重置链接已生成")
            return result.get('reset_link', '').split('token=')[1] if 'reset_link' in result else None
        else:
            print_test("忘记密码（有效邮箱）", False, result.get('message', '未知错误'))
            return None
    except Exception as e:
        print_test("忘记密码（有效邮箱）", False, f"异常: {str(e)}")
        return None

def test_api_reset_password(token):
    """测试重置密码接口"""
    print(f"\n{Color.BLUE}测试6: 重置密码 API{Color.END}")
    
    if not token:
        print_test("重置密码", False, "无token，跳过测试")
        return False
    
    try:
        data = {
            'token': token,
            'password': 'NewPassword@789'
        }
        
        response = requests.post(f'{API_URL}/api/reset-password', json=data)
        result = response.json()
        
        if response.status_code == 200 and result.get('success'):
            print_test("重置密码", True, "密码已重置")
        else:
            print_test("重置密码", False, result.get('message', '未知错误'))
    except Exception as e:
        print_test("重置密码", False, f"异常: {str(e)}")
    
    return True

def test_frontend_pages():
    """测试前端页面访问"""
    print(f"\n{Color.BLUE}测试7: 前端页面访问{Color.END}")
    
    pages = [
        ('/', '首页'),
        ('/login.html', '登录页面'),
        ('/register.html', '注册页面'),
        ('/profile.html', '个人中心页面'),
        ('/forgot-password.html', '忘记密码页面'),
        ('/index.html', '首页（完整路径）')
    ]
    
    all_passed = True
    
    for path, name in pages:
        try:
            response = requests.get(f'{BASE_URL}{path}')
            
            if response.status_code == 200 and '<html' in response.text.lower():
                print_test(f"页面访问 - {name}", True, f"HTTP {response.status_code}")
            else:
                print_test(f"页面访问 - {name}", False, f"HTTP {response.status_code}")
                all_passed = False
        except Exception as e:
            print_test(f"页面访问 - {name}", False, f"异常: {str(e)}")
            all_passed = False
    
    return all_passed

def test_javascript_syntax():
    """测试JavaScript语法"""
    print(f"\n{Color.BLUE}测试8: JavaScript语法检查{Color.END}")
    
    import subprocess
    
    html_files = [
        'login.html',
        'register.html',
        'profile.html',
        'forgot-password.html',
        'reset-password.html'
    ]
    
    all_passed = True
    
    for filename in html_files:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 提取所有script标签内容
            import re
            scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
            
            for i, script in enumerate(scripts):
                try:
                    # 将JavaScript代码写入临时文件，然后使用node检查语法
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                        f.write(script)
                        temp_file = f.name
                    
                    # 使用Node.js检查语法
                    result = subprocess.run(
                        ['node', '--check', temp_file],
                        capture_output=True,
                        text=True
                    )
                    
                    # 删除临时文件
                    os.unlink(temp_file)
                    
                    if result.returncode == 0:
                        print_test(f"JS语法 - {filename} (script {i+1})", True, "语法正确")
                    else:
                        print_test(f"JS语法 - {filename} (script {i+1})", False, result.stderr[:100])
                        all_passed = False
                except Exception as e:
                    print_test(f"JS语法 - {filename} (script {i+1})", False, f"异常: {str(e)}")
                    all_passed = False
        except Exception as e:
            print_test(f"JS语法 - {filename}", False, f"无法读取文件: {str(e)}")
            all_passed = False
    
    return all_passed

def print_summary(results):
    """打印测试总结"""
    print(f"\n{Color.BOLD}{'='*60}{Color.END}")
    print(f"{Color.BOLD}测试总结{Color.END}")
    print(f"{Color.BOLD}{'='*60}{Color.END}\n")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    for test_name, result in results.items():
        status = f"{Color.GREEN}✓ 通过{Color.END}" if result else f"{Color.RED}✗ 失败{Color.END}"
        print(f"  {status} {test_name}")
    
    print(f"\n{Color.BOLD}{'-'*60}{Color.END}")
    print(f"  总测试数: {total}")
    print(f"  {Color.GREEN}通过: {passed}{Color.END}")
    print(f"  {Color.RED}失败: {failed}{Color.END}")
    
    if passed == total:
        print(f"\n  {Color.GREEN}{Color.BOLD}🎉 所有测试通过！{Color.END}")
    else:
        print(f"\n  {Color.YELLOW}{Color.BOLD}⚠️  有 {failed} 个测试失败，请检查{Color.END}")
    
    print(f"\n{Color.BOLD}{'='*60}{Color.END}\n")

def main():
    """主函数"""
    print(f"\n{Color.BOLD}{Color.BLUE}")
    print("="*60)
    print("  玄机算命网 - 登录注册功能自动化测试")
    print("="*60)
    print(f"{Color.END}\n")
    
    print(f"  后端API地址: <{API_URL}>")
    print(f"  前端页面地址: <{BASE_URL}>")
    print(f"  测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    print(f"{Color.BOLD}{'-'*60}{Color.END}\n")
    
    # 检查结果
    results = {}
    
    # 测试1: 注册接口
    try:
        results['用户注册API'] = test_api_register()
    except Exception as e:
        results['用户注册API'] = False
        print(f"\n{Color.RED}测试1异常: {str(e)}{Color.END}")
    
    # 测试2: 登录接口
    token = None
    try:
        token = test_api_login()
        results['用户登录API'] = token is not None
    except Exception as e:
        results['用户登录API'] = False
        print(f"\n{Color.RED}测试2异常: {str(e)}{Color.END}")
    
    # 测试3: 获取用户信息接口
    try:
        results['获取用户信息API'] = test_api_profile(token)
    except Exception as e:
        results['获取用户信息API'] = False
        print(f"\n{Color.RED}测试3异常: {str(e)}{Color.END}")
    
    # 测试4: 更新用户信息接口
    try:
        results['更新用户信息API'] = test_api_update_profile(token)
    except Exception as e:
        results['更新用户信息API'] = False
        print(f"\n{Color.RED}测试4异常: {str(e)}{Color.END}")
    
    # 测试5: 忘记密码接口
    reset_token = None
    try:
        reset_token = test_api_forgot_password()
        results['忘记密码API'] = reset_token is not None
    except Exception as e:
        results['忘记密码API'] = False
        print(f"\n{Color.RED}测试5异常: {str(e)}{Color.END}")
    
    # 测试6: 重置密码接口
    try:
        results['重置密码API'] = test_api_reset_password(reset_token)
    except Exception as e:
        results['重置密码API'] = False
        print(f"\n{Color.RED}测试6异常: {str(e)}{Color.END}")
    
    # 测试7: 前端页面访问
    try:
        results['前端页面访问'] = test_frontend_pages()
    except Exception as e:
        results['前端页面访问'] = False
        print(f"\n{Color.RED}测试7异常: {str(e)}{Color.END}")
    
    # 测试8: JavaScript语法检查
    try:
        results['JavaScript语法'] = test_javascript_syntax()
    except Exception as e:
        results['JavaScript语法'] = False
        print(f"\n{Color.RED}测试8异常: {str(e)}{Color.END}")
    
    # 打印总结
    print_summary(results)
    
    # 返回退出码
    return 0 if all(results.values()) else 1

if __name__ == '__main__':
    sys.exit(main())
