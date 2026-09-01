#!/bin/bash
# ============================================================
# 自动更新守护进程 — 通过 auto_update.sh + reload_server.sh 协同工作
#
# 职责:
#   1. 首次启动时执行一次完整更新
#   2. 确保 auto_update.sh 守护进程始终存活
#
# 用法: bash /root/suanming/auto_update_runner.sh &
# ============================================================

BASE_DIR="/root/suanming"
LOG_FILE="$BASE_DIR/logs/auto_update_runner.log"
AUTO_UPDATE_SH="$BASE_DIR/auto_update.sh"
RELOAD_SH="$BASE_DIR/reload_server.sh"
CHECK_INTERVAL=60

log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

mkdir -p "$BASE_DIR/logs"

log "===== 自动更新守护启动 ====="
log "项目目录: $BASE_DIR"
log "检查间隔: ${CHECK_INTERVAL}秒"

# 首次启动：执行一次完整更新
log "执行首次更新检查..."
if [ -f "$RELOAD_SH" ]; then
    bash "$RELOAD_SH" >> "$LOG_FILE" 2>&1
    log "首次更新完成"
else
    log "⚠️  $RELOAD_SH 不存在，跳过首次更新"
fi

# 确保 auto_update.sh 守护进程在运行
start_auto_update() {
    if ! pgrep -f "auto_update.sh start" > /dev/null 2>&1; then
        log "启动 auto_update.sh 守护进程..."
        bash "$AUTO_UPDATE_SH" start >> "$LOG_FILE" 2>&1
        sleep 2
        if pgrep -f "auto_update.sh" > /dev/null 2>&1; then
            log "auto_update.sh 启动成功"
        else
            log "警告: auto_update.sh 启动失败"
        fi
    else
        log "auto_update.sh 已在运行"
    fi
}

start_auto_update

# 主循环：守护 auto_update.sh
while true; do
    if ! pgrep -f "auto_update.sh" > /dev/null 2>&1; then
        log "检测到 auto_update.sh 已停止，正在重启..."
        start_auto_update
    fi
    sleep "$CHECK_INTERVAL"
done
