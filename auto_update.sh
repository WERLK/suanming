#!/bin/bash
# Auto-update daemon: watches git repo, redeploys on new commits
# Usage: bash auto_update.sh start|stop|status|restart

PROJECT_DIR="/root/suanming"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$LOG_DIR/auto_update.pid"
CHECK_INTERVAL=300  # check every 5 minutes

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_DIR/auto_update.log"
}

get_pid() {
    if [ -f "$PID_FILE" ]; then
        cat "$PID_FILE"
    fi
}

is_running() {
    local pid
    pid=$(get_pid)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        return 0
    fi
    return 1
}

start_daemon() {
    if is_running; then
        echo "Auto-update daemon already running (PID: $(get_pid))"
        return 1
    fi

    echo "Starting auto-update daemon..."

    # Run the loop in background
    (
        log "Daemon started, check interval: ${CHECK_INTERVAL}s"

        while true; do
            cd "$PROJECT_DIR" 2>/dev/null || { log "ERROR: $PROJECT_DIR not found"; sleep "$CHECK_INTERVAL"; continue; }

            # Check for updates
            git fetch origin main 2>/dev/null
            LOCAL=$(git rev-parse HEAD 2>/dev/null)
            REMOTE=$(git rev-parse origin/main 2>/dev/null)

            if [ -n "$LOCAL" ] && [ -n "$REMOTE" ] && [ "$LOCAL" != "$REMOTE" ]; then
                log "New commits detected: ${LOCAL:0:7} -> ${REMOTE:0:7}"
                
                # Also check if gunicorn is running; if not, force redeploy
                if pgrep -f gunicorn > /dev/null 2>&1; then
                    log "Gunicorn is running, redeploying..."
                else
                    log "Gunicorn is DOWN, starting recovery deploy..."
                fi
                
                bash "$PROJECT_DIR/start_gunicorn.sh" >> "$LOG_DIR/auto_update.log" 2>&1
                log "Redeploy finished"
            elif ! pgrep -f gunicorn > /dev/null 2>&1; then
                log "Gunicorn not running, attempting recovery..."
                bash "$PROJECT_DIR/start_gunicorn.sh" >> "$LOG_DIR/auto_update.log" 2>&1
                log "Recovery deploy finished"
            fi

            sleep "$CHECK_INTERVAL"
        done
    ) &

    echo $! > "$PID_FILE"
    echo "Daemon started (PID: $(cat "$PID_FILE"))"
}

stop_daemon() {
    local pid
    pid=$(get_pid)
    if [ -n "$pid" ]; then
        kill -9 "$pid" 2>/dev/null || true
        rm -f "$PID_FILE"
        echo "Daemon stopped (PID: $pid)"
    else
        pkill -9 -f "auto_update.*start" 2>/dev/null || true
        echo "Daemon stopped (fallback)"
    fi
}

status_daemon() {
    if is_running; then
        echo "Running (PID: $(get_pid))"
        echo "--- Last 5 log lines ---"
        tail -5 "$LOG_DIR/auto_update.log" 2>/dev/null || echo "(no log yet)"
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
