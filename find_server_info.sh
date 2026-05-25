#!/bin/bash

echo "============================================"
echo "📋 服务器项目信息查找工具"
echo "============================================"
echo ""

# 1. 查找正在运行的 Python/Flask 进程
echo "🔍 1. 正在运行的 Python 进程："
echo "--------------------------------------------"
ps aux | grep -E "(python|gunicorn|flask|uvicorn)" | grep -v grep
echo ""

# 2. 查找项目目录
echo "🔍 2. 查找项目目录（包含 app.py）："
echo "--------------------------------------------"
find /var/www /root /home /tmp -name "app.py" -type f 2>/dev/null | head -10

# 3. 查找 Nginx 配置
echo ""
echo "🔍 3. Nginx 配置文件："
echo "--------------------------------------------"
if [ -d /etc/nginx/sites-enabled ]; then
    for f in /etc/nginx/sites-enabled/*; do
        echo "文件: $f"
        cat "$f" 2>/dev/null | grep -E "(server_name|listen|proxy_pass|root)" | head -10
        echo ""
    done
elif [ -f /etc/nginx/nginx.conf ]; then
    grep -E "(server_name|listen|root)" /etc/nginx/nginx.conf | head -10
fi

# 4. 查找宝塔面板（如果使用宝塔）
echo ""
echo "🔍 4. 宝塔面板："
echo "--------------------------------------------"
if [ -d /www/server/panel ]; then
    echo "✅ 已安装宝塔面板"
    bt version 2>/dev/null || echo "版本查询命令不可用"
else
    echo "❌ 未安装宝塔面板"
fi

# 5. 查找 Supervisor 配置
echo ""
echo "🔍 5. Supervisor 配置："
echo "--------------------------------------------"
if [ -d /etc/supervisor/conf.d ]; then
    ls -la /etc/supervisor/conf.d/
    for f in /etc/supervisor/conf.d/*.conf; do
        [ -f "$f" ] || continue
        echo ""
        echo "--- 文件: $f ---"
        cat "$f" | grep -E "(command|directory|user|numprocs|autostart)" | head -10
    done
elif [ -d /etc/supervisord.d ]; then
    ls -la /etc/supervisord.d/
fi

# 6. 查找运行端口
echo ""
echo "🔍 6. 正在监听的端口："
echo "--------------------------------------------"
if command -v netstat &> /dev/null; then
    netstat -tlnp 2>/dev/null | grep -E "(python|gunicorn|nginx|php)" || echo "没有符合条件的端口"
elif command -v ss &> /dev/null; then
    ss -tlnp 2>/dev/null | grep -E "(python|gunicorn|nginx|php)" || echo "没有符合条件的端口"
else
    echo "没有 netstat 或 ss 命令"
fi

# 7. 查找 Git 仓库
echo ""
echo "🔍 7. Git 仓库："
echo "--------------------------------------------"
find /var/www /root /home -maxdepth 3 -name ".git" -type d 2>/dev/null | while read gitdir; do
    project_dir=$(dirname "$gitdir")
    echo "仓库: $project_dir"
    cd "$project_dir" && git log --oneline -3 2>/dev/null || echo "  (无法读取提交记录)"
    echo ""
done

# 8. 查找 requirements.txt
echo ""
echo "🔍 8. requirements.txt 文件："
echo "--------------------------------------------"
find /var/www /root /home -maxdepth 3 -name "requirements.txt" -type f 2>/dev/null | head -10

echo ""
echo "============================================"
echo "✅ 查找完成！"
echo "============================================"
