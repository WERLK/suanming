#!/bin/bash
# 玄机算命网 - 服务器自动更新状态检查脚本
# 服务器 IP：8.153.90.109

echo "======================================"
echo "  玄机算命网 - 自动更新状态检查"
echo " 服务器 IP：8.153.90.109"
echo "======================================"
echo ""

# 1. 检查代码版本
echo "【1】检查代码版本..."
cd /root/suanming 2>/dev/null && {
    LOCAL_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "无")
    REMOTE_COMMIT=$(git ls-remote origin main 2>/dev/null | awk '{print $1}' || echo "无")
    
    if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
        echo "  ✅ 代码已是最新版本"
        echo "     本地提交：${LOCAL_COMMIT:0:7}"
    else
        echo "  ⚠️  代码不是最新版本"
        echo "     本地提交：${LOCAL_COMMIT:0:7}"
        echo "     远程提交：${REMOTE_COMMIT:0:7}"
        echo "     → 请执行：cd /root/suanming && git pull origin main"
    fi
} || {
    echo "  ❌ 项目目录不存在"
}
echo ""

# 2. 检查 Gunicorn 进程
echo "【2】检查后端服务..."
if pgrep -f "gunicorn.*app:app" >/dev/null; then
    echo "  ✅ Gunicorn 正在运行"
    echo "     进程信息："
    ps aux | grep "gunicorn.*app:app" | grep -v grep | head -2 | awk '{print "       PID:", $2, "  启动时间:", $9}'
else
    echo "  ❌ Gunicorn 未运行"
    echo "     → 请执行启动命令"
fi
echo ""

# 3. 检查端口监听
echo "【3】检查端口监听..."
if netstat -tuln 2>/dev/null | grep -q ":5000 "; then
    echo "  ✅ 端口 5000 正在监听"
else
    echo "  ❌ 端口 5000 未监听"
fi
echo ""

# 4. 测试健康检查端点
echo "【4】测试健康检查端点..."
HEALTH_CHECK=$(curl -s http://localhost:5000/api/health 2>/dev/null)
if echo "$HEALTH_CHECK" | grep -q '"status".* "ok"'; then
    echo "  ✅ 健康检查通过"
    echo "     响应：$HEALTH_CHECK" | python3 -m json.tool 2>/dev/null || echo "     $HEALTH_CHECK"
else
    echo "  ❌ 健康检查失败"
    echo "     响应：$HEALTH_CHECK"
fi
echo ""

# 5. 检查自动更新端点
echo "【5】检查自动更新端点..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/update-secret-2026 2>/dev/null)
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "500" ]; then
    echo "  ✅ 自动更新端点存在 (HTTP $HTTP_CODE)"
    echo "     → 触发更新：curl http://localhost:5000/update-secret-2026"
else
    echo "  ❌ 自动更新端点不存在 (HTTP $HTTP_CODE)"
    echo "     → 需要先部署最新代码"
fi
echo ""

# 6. 检查日志文件
echo "【6】检查日志文件..."
if [ -f "/root/suanming/logs/gunicorn.log" ]; then
    LOG_SIZE=$(du -h /root/suanming/logs/gunicorn.log 2>/dev/null | awk '{print $1}' || echo "未知")
    echo "  ✅ 日志文件存在"
    echo "     大小：$LOG_SIZE"
    echo ""
    echo "  最近 10 行日志："
    tail -10 /root/suanming/logs/gunicorn.log 2>/dev/null | sed 's/^/     /' || echo "     无日志"
else
    echo "  ⚠️  日志文件不存在"
    echo "     → 需要先启动服务生成日志"
fi
echo ""

echo "======================================"
echo "  检查完成！"
echo "======================================"
echo ""

# 7. 给出建议
echo "📝 后续操作建议："
echo ""

if ! pgrep -f "gunicorn.*app:app" >/dev/null; then
    echo "1️⃣  启动后端服务："
    echo "   cd /root/suanming/api"
    echo "   nohup gunicorn -w 4 -t 300 -b 0.0.0.0:5000 app:app > /root/suanming/logs/gunicorn.log 2>&1 &"
    echo ""
fi

if ! curl -s http://localhost:5000/api/health 2>/dev/null | grep -q '"status".* "ok"'; then
    echo "2️⃣  检查后端是否启动成功："
    echo "   cd /root/suanming"
    echo "   python3 backend_check.py"
    echo ""
fi

echo "3️⃣  如果需要强制更新（紧急情况）："
echo "   cd /root/suanming"
echo "   git fetch origin"
echo "   git reset --hard origin/main"
echo "   pkill -f gunicorn"
echo "   cd api && nohup gunicorn -w 4 -t 300 -b 0.0.0.0:5000 app:app > ../logs/gunicorn.log 2>&1 &"
echo ""
