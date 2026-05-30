#!/bin/bash
# ============================================================
# 服务器热更新脚本 — 拉取最新代码 + 重启 gunicorn
# 被 auto_update.sh 守护进程自动调用
#
# 用法: bash reload_server.sh
# ============================================================

set -e

PROJECT_DIR="/root/suanming"
LOG_DIR="$PROJECT_DIR/logs"

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_DIR/reload.log"
}

log "========== 代码更新 + 服务重启 =========="

# ---- Step 1: 拉取最新代码 ----
log "Step 1/3: 拉取最新代码..."
cd "$PROJECT_DIR"

git fetch origin main 2>&1 | tee -a "$LOG_DIR/reload.log"
LOCAL=$(git rev-parse HEAD 2>/dev/null)
git reset --hard origin/main 2>&1 | tee -a "$LOG_DIR/reload.log"
REMOTE=$(git rev-parse HEAD 2>/dev/null)

log "代码更新: ${LOCAL:0:7} -> ${REMOTE:0:7}"

# ---- Step 2: 停止旧进程 ----
log "Step 2/3: 停止旧 gunicorn 进程..."
pkill -f gunicorn 2>/dev/null || true
sleep 2

# 确保彻底杀掉
if pgrep -f gunicorn > /dev/null 2>&1; then
    log "强制杀掉残留进程..."
    pkill -9 -f gunicorn 2>/dev/null || true
    sleep 1
fi

log "旧进程已停止"

# ---- Step 3: 启动新 gunicorn ----
log "Step 3/3: 启动 gunicorn..."
cd "$PROJECT_DIR"

nohup gunicorn -w 4 -b 0.0.0.0:5000 api.app:app \
    --timeout 120 \
    --access-logfile "$LOG_DIR/access.log" \
    --error-logfile "$LOG_DIR/error.log" \
    > "$LOG_DIR/gunicorn.log" 2>&1 &

sleep 3

# ---- 验证 ----
if pgrep -f gunicorn > /dev/null 2>&1; then
    PID=$(pgrep -f gunicorn | head -1)
    log "✅ Gunicorn 启动成功 (PID: $PID)"

    # 快速健康检查
    sleep 1
    if curl -sf http://127.0.0.1:5000/ > /dev/null 2>&1; then
        log "✅ 健康检查通过"
    else
        log "⚠️  健康检查失败，请查看日志"
    fi
else
    log "❌ Gunicorn 启动失败！查看日志: $LOG_DIR/gunicorn.log"
    tail -20 "$LOG_DIR/gunicorn.log" | tee -a "$LOG_DIR/reload.log"
    exit 1
fi

log "========== 完成 =========="
