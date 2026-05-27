#!/bin/bash
# 玄机算命网 - 一键查看状态脚本
# 用法: bash status.sh

TARGET_DIR="/root/suanming/newapp"
LOG_DIR="${TARGET_DIR}/logs"

echo "========================================="
echo "  玄机算命网 - 运行状态"
echo "========================================="
echo ""

# 1. 检查 gunicorn 是否在运行
echo "【1. Gunicorn 服务状态】"
GUNICORN_PID=$(pgrep -f "gunicorn.*api.app" 2>/dev/null)
if [ -n "$GUNICORN_PID" ]; then
    echo "  ✅ Gunicorn 运行中 (PID: $GUNICORN_PID)"
    # 检查端口
    if netstat -tlnp 2>/dev/null | grep -q ':5000'; then
        echo "  ✅ 端口 5000 已监听"
    else
        echo "  ⚠️  端口 5000 未监听！"
    fi
    # 测试 HTTP
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 2>/dev/null)
    if [ "$HTTP_CODE" = "200" ]; then
        echo "  ✅ HTTP 响应正常 (200)"
    else
        echo "  ⚠️  HTTP 响应异常 (${HTTP_CODE:-无响应})"
    fi
else
    echo "  ❌ Gunicorn 未运行！"
fi
echo ""

# 2. 检查自动更新守护进程
echo "【2. 自动更新守护进程状态】"
AUTO_PID=$(pgrep -f "auto_update_daemon" 2>/dev/null)
if [ -n "$AUTO_PID" ]; then
    echo "  ✅ 自动更新进程运行中 (PID: $AUTO_PID)"
else
    echo "  ⚠️  自动更新进程未运行"
fi
echo ""

# 3. 显示最新日志（自动更新）
echo "【3. 自动更新日志（最新 10 行）】"
if [ -f "${LOG_DIR}/auto_update.log" ]; then
    tail -10 "${LOG_DIR}/auto_update.log" 2>/dev/null | sed 's/^/  /'
else
    echo "  (日志文件不存在)"
fi
echo ""

# 4. 显示 gunicorn 日志最新内容
echo "【4. Gunicorn 日志（最新 5 行）】"
if [ -f "${LOG_DIR}/gunicorn.log" ]; then
    tail -5 "${LOG_DIR}/gunicorn.log" 2>/dev/null | sed 's/^/  /'
else
    echo "  (日志文件不存在)"
fi
echo ""

# 5. 检查代码版本
echo "【5. 当前代码版本】"
if [ -d "${TARGET_DIR}/.git" ]; then
    cd "$TARGET_DIR" 2>/dev/null && \
        echo "  本地 commit: $(git rev-parse --short HEAD 2>/dev/null || echo '未知')" && \
        echo "  本地分支:  $(git branch --show-current 2>/dev/null || echo '未知')"
    cd - > /dev/null 2>&1
else
    echo "  (不是 git 仓库，无法查看版本)"
fi
echo ""

# 6. 磁盘和内存
echo "【6. 系统资源】"
echo "  内存: $(free -h 2>/dev/null | grep Mem | awk '{print $3 "/" $2}')"
echo "  磁盘: $(df -h ${TARGET_DIR} 2>/dev/null | tail -1 | awk '{print $3 "/" $2 " (" $5 " 已用)"}')"
echo ""

echo "========================================="
echo "  查看实时日志: tail -f ${LOG_DIR}/auto_update.log"
echo "  重启服务: cd ${TARGET_DIR} && bash fix.sh"
echo "========================================="
