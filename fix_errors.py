import re

# 读取文件
with open('/workspace/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print('修复前的错误:')
if 'outline' in content:
    print('  - outline 错误')
if 'scalable' in content:
    print('  - scalable 错误')
if 'classList' in content:
    print(f'  - classList 错误 (出现 {content.count("classList")} 次)')
if '`' in content or '`' in content:
    print('  - 弯引号错误')

# 1. 修复CSS中的 outline -> outline
content = content.replace('outline', 'outline')

# 2. 修复viewport中的 scalabel -> scalable
content = content.replace('scalable', 'scalable')

# 3. 修复JavaScript中的 classList -> classList
content = content.replace('classList', 'classList')

# 4. 修复弯引号
content = content.replace('`', "'").replace(''', "'").replace('`', "'").replace(''', "'")

# 5. 检查并修复其他常见问题
if 'var ' in content:
    print('  - 发现 "var " 声明（如果需要let/const可以改）')

print('\n修复完成！正在保存...')

# 保存文件
with open('/workspace/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

# 验证修复
with open('/workspace/index.html', 'r', encoding='utf-8') as f:
    new_content = f.read()

print('\n修复后的检查:')
errors = 0
if 'outline' in new_content:
    print('  ❌ 仍有 outline 错误')
    errors += 1
if 'scalable' in new_content:
    print('  ❌ 仍有 scalable 错误')
    errors += 1
if 'classList' in new_content:
    print(f'  ❌ 仍有 classList 错误 ({new_content.count("classList")} 处)')
    errors += 1
if '`' in new_content or '`' in new_content:
    print('  ❌ 仍有弯引号')
    errors += 1

if errors == 0:
    print('  ✅ 所有错误已修复！')
    
print(f'\n文件大小: {round(len(new_content)/1024, 1)} KB')
