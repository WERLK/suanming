#!/bin/bash
# Auto-update daemon - checks GitHub every 5 minutes and updates if needed
# Start: nohup bash auto_update_daemon.sh > /root/suanming/logs/auto_update.log 2>&1 &

PROJECT_DIR="/root/suanming"
LOG_FILE="$PROJECT_DIR/logs/auto_update.log"
CHECK_INTERVAL=300  # 5 minutes

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "Auto-update daemon started (check interval: ${CHECK_INTERVAL}s)"

while true; do
    cd "$PROJECT_DIR" || exit 1
    
    # Get current local commit
    LOCAL_HASH=$(git rev-parse HEAD 2>/dev/null)
    
    # Get remote commit without pulling
    git fetch origin main 2>/dev/null
    REMOTE_HASH=$(git rev-parse origin/main 2>/dev/null)
    
    if [ "$LOCAL_HASH" != "$REMOTE_HASH" ] && [ -n "$REMOTE_HASH" ]; then
        log "New commits detected: $LOCAL_HASH -> $REMOTE_HASH"
        log "Pulling latest code..."
        
        if git reset --hard origin/main 2>/dev/null; then
            log "Code updated successfully"
            
            # Restart gunicorn
            log "Restarting gunicorn..."
            pkill -f gunicorn
            sleep 5
            
            cd "$PROJECT_DIR/api"
            nohup gunicorn -w 4 -t 300 -b 0.0.0.0:5000 app:app \
                > "$PROJECT_DIR/logs/gunicorn.log" 2>&1 &
            
            sleep 3
            log "Gunicorn restarted"
        else
            log "ERROR: Failed to pull code"
        fi
    fi
    
    sleep "$CHECK_INTERVAL"
done
