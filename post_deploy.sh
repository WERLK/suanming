#!/bin/bash
# Post-deploy fix script: applied after git pull, before gunicorn restart
# Idempotent - safe to run multiple times

set -e

PROJECT_DIR="/root/suanming"
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_DIR/post_deploy.log"
}

log "Post-deploy fixes starting..."

# Fix 1: Inject auth.js into sub-pages that need authentication
PAGES=(
    "profile.html"
    "favorites.html"
    "history.html"
    "shares.html"
    "notifications.html"
    "edit-profile.html"
    "privacy.html"
)

AUTH_TAG='<script src="/js/auth.js"></script>'
MAIN_JS_TAG='<script src="/js/main.js"></script>'

for page in "${PAGES[@]}"; do
    file="$PROJECT_DIR/$page"
    if [ ! -f "$file" ]; then
        log "SKIP: $page not found"
        continue
    fi
    
    if grep -qF "$AUTH_TAG" "$file"; then
        log "SKIP: $page already has auth.js"
    else
        sed -i "s|$MAIN_JS_TAG|$MAIN_JS_TAG\n    $AUTH_TAG|" "$file"
        if grep -qF "$AUTH_TAG" "$file"; then
            log "OK: $page - auth.js injected"
        else
            log "FAIL: $page - injection failed"
        fi
    fi
done

log "Post-deploy fixes complete"

# ── Ensure Nginx config is correct (idempotent) ──
if [ -f "$PROJECT_DIR/setup_nginx.sh" ]; then
    log "Checking Nginx config..."
    bash "$PROJECT_DIR/setup_nginx.sh" >> "$LOG_DIR/post_deploy.log" 2>&1 || log "WARN: Nginx setup had issues, but continuing"
fi
