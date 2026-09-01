#!/bin/bash
# 玄机算命网 - 生产环境启动脚本
# 自动加载短信和邮件配置，启动Gunicorn服务

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔮 玄机算命网 - 生产环境启动"

# =============================================
# 1. 加载短信验证码配置
# =============================================
SMS_ENV_FILE="$SCRIPT_DIR/api/.env.sms"
if [ -f "$SMS_ENV_FILE" ]; then
    echo "📱 加载短信配置..."
    set -a
    source "$SMS_ENV_FILE"
    set +a
    echo "   ✅ 短信配置已加载"
else
    echo "   ⚠️  未找到 api/.env.sms，短信将使用演示模式"
fi

# =============================================
# 2. 安装依赖
# =============================================
echo "📦 检查依赖..."
pip3 install -q alibabacloud_dypnsapi20170525 2>/dev/null || true

# =============================================
# 3. 创建必要目录
# =============================================
mkdir -p "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/data"

# =============================================
# 4. 停止旧进程
# =============================================
echo "🛑 停止旧服务..."
pkill -f gunicorn 2>/dev/null || true
pkill -f auto_update_daemon 2>/dev/null || true
sleep 2

# =============================================
# 5. 启动后端API (Gunicorn)
# =============================================
echo "🚀 启动后端API（Gunicorn，端口5000）..."
cd "$SCRIPT_DIR/api"
nohup python3 -m gunicorn \
    -w 2 \
    -b 0.0.0.0:5000 \
    app:app \
    --timeout 120 \
    --access-logfile "$SCRIPT_DIR/logs/access.log" \
    --error-logfile "$SCRIPT_DIR/logs/error.log" \
    > "$SCRIPT_DIR/logs/gunicorn.log" 2>&1 &
echo "   ✅ Gunicorn已启动 (PID: $!)"

# =============================================
# 6. 启动自动更新守护（可选）
# =============================================
cd "$SCRIPT_DIR"
if [ -f "auto_update_runner.sh" ]; then
    echo "🔄 启动自动更新守护..."
    bash auto_update_runner.sh &
    echo "   ✅ 自动更新守护已启动"
fi

sleep 2

# =============================================
# 7. 状态检查
# =============================================
echo ""
echo "=========================================="
echo "  ✅ 所有服务已启动！"
echo "=========================================="
echo "  后端API:   http://localhost:5000"
echo "  日志目录:  $SCRIPT_DIR/logs/"
echo "  短信模式:  $( [ -n \"$ALIBABA_CLOUD_ACCESS_KEY_ID\" ] && echo '真实模式' || echo '演示模式' )"
echo ""
echo "  📋 管理命令："
echo "     查看日志: tail -f logs/gunicorn.log"
echo "     停止服务: pkill -f gunicorn"
echo "=========================================="
