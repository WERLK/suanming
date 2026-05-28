#!/bin/bash
# Unified auto-update daemon for suanming project
# Usage: bash auto_update.sh start|stop|status|restart

PROJECT_DIR="/root/suanming"
LOG_FILE="$PROJECT_DIR/logs/auto_update.log"
PID_FILE="$PROJECT_DIR/logs/auto_update.pid"
CHECK_INTERVAL=300  # 5 minutes

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

start_daemon() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "Auto-update daemon already running (PID: $(cat "$PID_FILE"))"
        return 1
    fi
    
    echo "Starting auto-update daemon..."
    nohup bash -c '
        PROJECT_DIR="/root/suanming"
        LOG_FILE="$PROJECT_DIR/logs/auto_update.log"
        CHECK_INTERVAL=300
        
        log() {
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $1" >> "$LOG_FILE"
        }
        
        log "Daemon started (interval: ${CHECK_INTERVAL}s)"
        
        while true; do
            cd "$PROJECT_DIR" || exit 1
            
            LOCAL_HASH=$(git rev-parse HEAD 2>/dev/null)
            git fetch origin main 2>/dev/null
            REMOTE_HASH=$(git rev-parse origin/main 2>/dev/null)
            
            if [ "$LOCAL_HASH" != "$REMOTE_HASH" ] && [ -n "$REMOTE_HASH" ]; then
                log "New commits: $LOCAL_HASH -> $REMOTE_HASH"
                if git reset --hard origin/main 2>/dev/null; then
                    log "Code updated"
                    log "Restarting gunicorn..."
                    pkill -f gunicorn
                    sleep 5
                    cd "$PROJECT_DIR/api"
                    nohup gunicorn -w 4 -t 300 -b 0.0.0.0:5000 app:app \
                        > "$PROJECT_DIR/logs/gunicorn.log" 2>&1 &
                    sleep 3
                    log "Gunicorn restarted"
                else
                    log "ERROR: Pull failed"
                fi
            fi
            
            sleep "$CHECK_INTERVAL"
        done
    ' > /dev/null 2>&1 &
    
    echo $! > "$PID_FILE"
    echo "Daemon started (PID: $(cat "$PID_FILE"))"
}

stop_daemon() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill -9 "$PID" 2>/dev/null
            echo "Daemon stopped (PID: $PID)"
        else
            echo "Daemon not running"
        fi
        rm -f "$PID_FILE"
    else
        # Fallback: kill all auto_update processes
        pkill -9 -f "auto_update" 2>/dev/null
        echo "Daemon stopped (fallback)"
    fi
}

status_daemon() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo "Running (PID: $(cat "$PID_FILE"))"
        echo "Last log:"
        tail -5 "$LOG_FILE" 2>/dev/null || echo "No log yet"
    else
        echo "Not running"
    fi
}

case "${1:-start}" in
    start)
        start_daemon
        ;;
    stop)
        stop_daemon
        ;;
    restart)
        stop_daemon
        sleep 2
        start_daemon
        ;;
    status)
        status_daemon
        ;;
    *)
        echo "Usage: bash auto_update.sh {start|stop|restart|status}"
        exit 1
        ;;
esac
