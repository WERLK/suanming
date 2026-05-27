#!/usr/bin/env python3
"""
检查后端运行状态的脚本
"""
import subprocess
import os
import json

print("===== 玄机算命网 状态检查 =====")
print()

# 1. 检查 Git 版本
print("[1/4] 检查代码版本...")
result = subprocess.run(['git', 'log', '--oneline', '-1'], 
                        cwd='/root/suanming',
                        capture_output=True, text=True)
if result.returncode == 0:
    commit = result.stdout.strip()
    print(f"✅ 当前版本: {commit}")
    
    # 检查是否是最新版本
    if 'f49c36a' in commit or 'feat: 添加 API 请求限流' in commit:
        print("✅ 已包含 API 限流功能")
    else:
        print("⚠️ 代码可能不是最新版本")
else:
    print("❌ 无法获取 Git 版本")

print()

# 2. 检查后端进程
print("[2/4] 检查后端进程...")
result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
processes = [line for line in result.stdout.split('\n') if 'gunicorn' in line.lower()]

if processes:
    print(f"✅ 发现 {len(processes)} 个 Gunicorn 进程:")
    for proc in processes[:3]:  # 只显示前3个
        parts = proc.split()
        pid = parts[1]
        start_time = parts[8] if len(parts) > 8 else 'unknown'
        print(f"  - PID: {pid}, 启动时间: {start_time}")
else:
    print("❌ 未发现 Gunicorn 进程")

print()

# 3. 检查端口监听
print("[3/4] 检查端口监听...")
result = subprocess.run(['lsof', '-i', ':5000'], 
                        capture_output=True, text=True)
if 'LISTEN' in result.stdout:
    print("✅ 端口 5000 正在监听")
else:
    print("❌ 端口 5000 未监听")

print()

# 4. 测试 API 限流（模拟请求）
print("[4/4] 测试 API 限流...")
print("提示: 需要连续请求 6 次登录接口，第6次应该被限流")
print("手动测试命令:")
print("  for i in {1..6}; do")
print('    curl -s -X POST http://8.153.90.109:5000/api/login \\')
print('      -H "Content-Type: application/json" \\')
print('      -d \'{"username":"test","password":"123"\' ;')
print('    echo ""')
print('    sleep 1')
print('  done')

print()
print("===== 检查完成 =====")

# 5. 显示最近日志
print()
print("最近日志 (最后 10 行):")
log_file = '/root/suanming/logs/gunicorn.log'
if os.path.exists(log_file):
    with open(log_file, 'r') as f:
        lines = f.readlines()
        for line in lines[-10:]:
            print(line.rstrip())
else:
    print("❌ 日志文件不存在")
