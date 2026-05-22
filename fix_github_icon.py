# 读取文件
with open('/workspace/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换图标
content = content.replace('>📱 微信登录<', '>🟢 微信登录<')
content = content.replace('>💬 QQ登录<', '>💙 QQ登录<')
content = content.replace('>🐙 GitHub登录<', '>🐱 GitHub登录<')

# 写回文件
with open('/workspace/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 已修复第三方登录图标")
print("   微信: 📱 → 🟢")
print("   QQ: 💬 → 💙")
print("   GitHub: 🐙 → 🐱")
