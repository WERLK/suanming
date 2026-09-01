#!/bin/bash
# Simple script to manage backend

APP_DIR="/workspace/suanming-fix"
PID_FILE="$APP_DIR/backend.pid"

start() {
    echo "Starting backend..."
    cd "$APP_DIR/api"
    nohup gunicorn -w 4 -b 0.0.0.0:5000 app:app > "$APP_DIR/logs/gunicorn.log" 2>&1 &
    echo $! > "$PID_FILE"
    sleep 2
    echo "Backend started (PID: $(cat $PID_FILE))"
}

stop() {
    echo "Stopping backend..."
    if [ -f "$PID_FILE" ]; then
        kill $(cat "$PID_FILE") 2>/dev/null
        rm -f "$PID_FILE"
        echo "Backend stopped"
    else
        echo "Backend not running"
    fi
}

status() {
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if ps -p "$pid" >/dev/null 2>&1; then
            echo "Backend is running (PID: $pid)"
        else
            echo "Backend not running (stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        echo "Backend not running"
    fi
}

case "$1" in
    start) start ;;
    stop) stop ;;
    restart) stop; sleep 2; start ;;
    status) status ;;
    *) echo "Usage: $0 {start|stop|restart|status}" ;;
esac
