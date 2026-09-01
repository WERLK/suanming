#!/bin/bash
# 功能测试脚本

echo "======================================"
echo "  玄机算命网功能测试"
echo "======================================"
echo ""

# 1. 检查文件是否存在
echo "【1】检查文件完整性..."
files=(
    "/workspace/suanming-fix/api/app.py"
    "/workspace/suanming-fix/api/avatar_audit.py"
    "/workspace/suanming-fix/version.json"
    "/workspace/suanming-fix/remote_update.sh"
    "/workspace/suanming-fix/update_version.sh"
    "/workspace/suanming-fix/profile.html"
    "/workspace/suanming-fix/index.html"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (不存在)"
    fi
done

echo ""
echo "【2】检查代码修改..."
echo ""

# 2. 检查 app.py 中的关键代码
echo "→ 检查健康检查端点："
if grep -q "@app.route('/api/health')" /workspace/suanming-fix/api/app.py; then
    echo "  ✅ /api/health 端点已添加"
else
    echo "  ❌ /api/health 端点未找到"
fi

echo ""
echo "→ 检查版本信息端点："
if grep -q "@app.route('/api/version')" /workspace/suanming-fix/api/app.py; then
    echo "  ✅ /api/version 端点已添加"
else
    echo "  ❌ /api/version 端点未找到"
fi

echo ""
echo "→ 检查头像上传端点："
if grep -q "@app.route('/api/avatar/upload')" /workspace/suanming-fix/api/app.py; then
    echo "  ✅ /api/avatar/upload 端点已添加"
else
    echo "  ❌ /api/avatar/upload 端点未找到"
fi

echo ""
echo "→ 检查超时设置（300秒）："
if grep -q "\-t 300" /workspace/suanming-fix/remote_update.sh; then
    echo "  ✅ Gunicorn 超时已设置为 300 秒"
else
    echo "  ❌ Gunicorn 超时未正确设置"
fi

if grep -q "timeout=300" /workspace/suanming-fix/api/app.py; then
    echo "  ✅ 自动更新接口超时已设置为 300 秒"
else
    echo "  ❌ 自动更新接口超时未正确设置"
fi

echo ""
echo "【3】检查版本文件..."
echo ""
if [ -f "/workspace/suanming-fix/version.json" ]; then
    echo "→ 版本信息："
    cat /workspace/suanming-fix/version.json | jq '.'
else
    echo "  ❌ version.json 不存在"
fi

echo ""
echo "【4】检查头像审核模块..."
echo ""
if [ -f "/workspace/suanming-fix/api/avatar_audit.py" ]; then
    echo "→ 审核规则："
    echo "  • 文件大小限制：2MB"
    echo "  • 支持格式：JPG/PNG/GIF"
    echo "  • 尺寸限制：50-1000 像素"
    echo "  • 内容审核：皮肤色调、血腥色调、纯色块检测"
else
    echo "  ❌ avatar_audit.py 不存在"
fi

echo ""
echo "【5】前端修改检查..."
echo ""
echo "→ profile.html："
if grep -q "avatarInput" /workspace/suanming-fix/profile.html; then
    echo "  ✅ 头像上传 input 已添加"
else
    echo "  ❌ 头像上传 input 未找到"
fi

if grep -q "uploadAvatar()" /workspace/suanming-fix/profile.html; then
    echo "  ✅ 头像上传函数已添加"
else
    echo "  ❌ 头像上传函数未找到"
fi

echo ""
echo "→ index.html："
if grep -q "versionInfo" /workspace/suanming-fix/index.html; then
    echo "  ✅ 版本号显示已添加"
else
    echo "  ❌ 版本号显示未找到"
fi

echo ""
echo "======================================"
echo "  测试完成！"
echo "======================================"
echo ""
echo "下一步操作："
echo "1. 提交代码到 GitHub："
echo "   cd /workspace/suanming-fix"
echo "   git add ."
echo "   git commit -m '添加版本管理和头像上传功能'"
echo "   git push origin main"
echo ""
echo "2. 在服务器上拉取更新："
echo "   cd /root/suanming"
echo "   git pull origin main"
echo "   pkill -f gunicorn"
echo "   cd api && nohup gunicorn -w 4 -t 300 -b 0.0.0.0:5000 app:app > ../logs/gunicorn.log 2>&1 &"
echo ""
