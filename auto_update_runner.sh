#!/bin/bash
# 自动更新守护进程 - 带自动重启
# 用法: bash /root/suanming/auto_update_runner.sh &

BASE_DIR="/root/suanming"
LOG_FILE="$BASE_DIR/logs/auto_update_runner.log"
DAEMON_SCRIPT="$BASE_DIR/auto_update_daemon.py"
CHECK_INTERVAL=60  # 每60秒检查一次守护进程是否存活

log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

mkdir -p "$BASE_DIR/logs"

log "===== 自动更新守护启动 ====="
log "项目目录: $BASE_DIR"
log "检查间隔: ${CHECK_INTERVAL}秒"

# 先确保一次更新
log "执行首次更新检查..."
cd "$BASE_DIR" || exit 1
git fetch origin main 2>&1 | tee -a "$LOG_FILE"
LOCAL=$(git rev-parse HEAD 2>/dev/null)
REMOTE=$(git rev-parse origin/main 2>/dev/null)
if [ "$LOCAL" != "$REMOTE" ] && [ -n "$REMOTE" ]; then
    log "发现新提交: ${LOCAL:0:7} -> ${REMOTE:0:7}"
    git reset --hard origin/main 2>&1 | tee -a "$LOG_FILE"
    log "代码更新完成，重启服务..."
    pkill -f gunicorn 2>/dev/null
    sleep 2
    nohup python3 -m gunicorn -c gunicorn_config.py api.app:app > logs/gunicorn.log 2>&1 &
    sleep 3
    log "服务重启完成"
else
    log "已是最新版本"
fi

# 启动 auto_update_daemon.py（如果没在运行）
start_daemon() {
    if ! pgrep -f "auto_update_daemon.py" > /dev/null 2>&1; then
        log "启动 auto_update_daemon.py..."
        cd "$BASE_DIR" || return 1
        nohup python3 "$DAEMON_SCRIPT" > logs/auto_update.log 2>&1 &
        sleep 2
        if pgrep -f "auto_update_daemon.py" > /dev/null 2>&1; then
            log "auto_update_daemon.py 启动成功, PID: $(pgrep -f 'auto_update_daemon.py' | head -1)"
        else
            log "警告: auto_update_daemon.py 启动失败"
        fi
    fi
}

start_daemon

# 主循环：每 CHECK_INTERVAL 秒检查一次守护进程
while true; do
    if ! pgrep -f "auto_update_daemon.py" > /dev/null 2>&1; then
        log "检测到 auto_update_daemon.py 已停止，正在重启..."
        start_daemon
    fi
    sleep "$CHECK_INTERVAL"
done
