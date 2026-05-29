#!/bin/bash
# One-click deploy script
# Usage: bash start_gunicorn.sh

set -e

PROJECT_DIR="/root/suanming"
LOG_DIR="$PROJECT_DIR/logs"
ENV_FILE="/etc/profile.d/aliyun_sms.sh"

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_DIR/deploy.log"
}

log "========== Deploy started =========="

# [1/6] Pull latest code
log "[1/6] Pulling code..."

# Backup user data before git reset (prevent data loss)
DATA_BACKUP="/tmp/suanming_data_backup"
rm -rf "$DATA_BACKUP"
if [ -d "$PROJECT_DIR/data" ]; then
    cp -r "$PROJECT_DIR/data" "$DATA_BACKUP" 2>/dev/null
    log "Data backed up to $DATA_BACKUP"
fi

cd "$PROJECT_DIR"
git fetch origin main
git reset --hard origin/main

# Restore user data after git reset
if [ -d "$DATA_BACKUP" ]; then
    mkdir -p "$PROJECT_DIR/data"
    cp -f "$DATA_BACKUP"/*.json "$PROJECT_DIR/data/" 2>/dev/null
    log "Data restored from backup"
fi

log "Code updated to $(git rev-parse --short HEAD)"

# [2/6] Init data files
log "[2/6] Initializing data files..."
python3 init_data.py
log "Data files OK"

# [3/6] Run post-deploy fixes (auth.js injection, etc.)
log "[3/6] Running post-deploy fixes..."
bash "$PROJECT_DIR/post_deploy.sh" >> "$LOG_DIR/deploy.log" 2>&1
log "Post-deploy fixes OK"

# [4/6] Load Aliyun SMS env
log "[4/6] Loading environment..."
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
    log "Aliyun SMS env loaded"
else
    log "WARNING: $ENV_FILE not found, SMS will use demo mode"
fi

# [5/6] Install Python deps
log "[5/6] Installing Python dependencies..."
python3 -m pip install aliyun-python-sdk-core aliyun-python-sdk-dysmsapi --quiet 2>/dev/null || true
log "Dependencies OK"

# [6/6] Start gunicorn
log "[6/6] Starting gunicorn..."

# Kill old instances
pkill -f gunicorn 2>/dev/null || true
sleep 3

# Ensure PYTHONPATH covers pyenv site-packages (for Aliyun SDK)
PYENV_SITE="/root/.pyenv/versions/3.11.1/lib/python3.11/site-packages"
if [ -d "$PYENV_SITE" ]; then
    export PYTHONPATH="$PYENV_SITE:${PYTHONPATH}"
    log "PYTHONPATH set: $PYENV_SITE"
fi

cd "$PROJECT_DIR/api"

# Start with python3 -m to avoid path issues
nohup python3 -m gunicorn -w 4 -t 300 -b 0.0.0.0:5000 app:app \
    > "$LOG_DIR/gunicorn.log" 2>&1 &

sleep 4

# Verify
if pgrep -f gunicorn > /dev/null; then
    PID=$(pgrep -f gunicorn | head -1)
    log "Gunicorn running (PID: $PID)"
    
    # Quick health check
    sleep 1
    if curl -sf http://127.0.0.1:5000/api/health > /dev/null 2>&1; then
        log "Health check PASSED"
    else
        log "WARNING: Health check failed, check logs"
    fi
else
    log "ERROR: Gunicorn failed to start!"
    tail -20 "$LOG_DIR/gunicorn.log"
    exit 1
fi

log "========== Deploy complete =========="
echo ""
echo "=> Gunicorn running on port 5000"
echo "=> Log: $LOG_DIR/gunicorn.log"
echo "=> Deploy log: $LOG_DIR/deploy.log"
