#!/bin/bash
# 玄机算命网 - 一键部署脚本（命令英文，说明中文）
# 服务器 IP：8.153.90.109

echo "======================================"
echo "   玄机算命网 - 一键部署"
echo "   服务器 IP：8.153.90.109"
echo "======================================"
echo ""

# 1. 拉取最新代码
echo "【1】拉取最新代码..."
cd /root/suanming && git pull origin main
if [ $? -eq 0 ]; then
    echo "  ✅ 代码拉取成功"
else
    echo "  ❌ 代码拉取失败"
    exit 1
fi
echo ""

# 2. 创建数据文件
echo "【2】创建数据文件..."
cd /root/suanming

mkdir -p data
echo '{}' > data/favorites.json
echo '{}' > data/shares.json
echo '{}' > data/reports.json
echo '{}' > data/notifications.json
echo '{}' > data/privacy.json

chmod 644 data/*.json

mkdir -p static/avatars
chmod 755 static/avatars/

echo "  ✅ 数据文件创建成功"
echo "      文件列表："
ls -lh data/*.json | awk '{print "       ", $9, "("$5")"}'
echo ""
echo "      目录列表："
ls -ld static/avatars/ | awk '{print "       ", $9}'
echo ""

# 3. 清除旧日志
echo "【3】清除旧日志..."
cd /root/suanming

if [ -f "logs/gunicorn.log" ]; then
    # 备份旧日志（可选）
    cp logs/gunicorn.log logs/gunicorn.log.bak.$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo "  ⚠️  旧日志备份失败，继续..."
    
    # 清除日志
    > logs/gunicorn.log
    echo "  ✅ 旧日志已清除"
    echo "      新日志大小："
    ls -lh logs/gunicorn.log | awk '{print "         ", $5}'
else
    echo "  ⚠️  日志文件不存在，将创建新文件"
    mkdir -p logs
    touch logs/gunicorn.log
fi
echo ""

# 4. 停止旧进程
echo "【4】停止旧进程..."
pkill -f gunicorn
sleep 5

if pgrep -f "gunicorn.*app:app" >/dev/null; then
    echo "  ⚠️  旧进程仍在运行，强制终止..."
    pkill -9 -f gunicorn
    sleep 3
fi

echo "  ✅ 旧进程已停止"
echo ""

# 5. 启动新进程
echo "【5】启动新进程（超时时间：300 秒）..."
cd /root/suanming/api
nohup gunicorn -w 4 -t 300 -b 0.0.0.0:5000 app:app > /root/suanming/logs/gunicorn.log 2>&1 &

sleep 5

if pgrep -f "gunicorn.*app:app" >/dev/null; then
    echo "  ✅ 新进程启动成功"
    echo "      进程信息："
    ps aux | grep "gunicorn.*app:app" | grep -v grep | head -2 | awk '{print "         PID:", $2, "  启动时间:", $9}'
else
    echo "  ❌ 新进程启动失败"
    echo "      请检查日志：tail -f /root/suanming/logs/gunicorn.log"
    exit 1
fi
echo ""

# 6. 检查服务状态
echo "【6】检查服务状态..."
cd /root/suanming

if [ -f "backend_check.py" ]; then
    python3 backend_check.py
else
    echo "  ⚠️  backend_check.py 不存在，跳过详细检查"
    echo "      你可以手动检查：python3 backend_check.py"
fi
echo ""

echo "======================================"
echo "  部署完成！"
echo "======================================"
echo ""
echo "📝 后续操作建议："
echo ""
echo "1️⃣  在浏览器中打开："
echo "      http://8.153.90.109"
echo ""
echo "2️⃣  测试头像上传功能（个人中心）"
echo ""
echo "3️⃣  测试版本号显示（右下角）"
echo ""
echo "4️⃣  测试所有功能（收藏、分享、报告、设置等）"
echo ""
echo "5️⃣  查看日志："
echo "      tail -f /root/suanming/logs/gunicorn.log"
echo ""
