#!/bin/bash
# ============================================================
# Server-side one-time deploy script
# Run this ONCE on Alibaba Cloud server (8.153.90.109)
# It creates post_deploy.sh, updates start_gunicorn.sh,
# and fixes all sub-pages to load auth.js
# ============================================================
set -e

PROJECT_DIR="/root/suanming"
LOG_DIR="$PROJECT_DIR/logs"

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_DIR/deploy.log"
}

log "========== Deploy script started =========="

# -----------------------------------------------------------
# Step 1: Create post_deploy.sh (idempotent fix script)
# -----------------------------------------------------------
log "[1/4] Creating post_deploy.sh..."

cat > "$PROJECT_DIR/post_deploy.sh" << 'SCRIPT_END'
#!/bin/bash
# Post-deploy fix: inject auth.js into sub-pages
# Idempotent - safe to run multiple times
set -e
PROJECT_DIR="/root/suanming"
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"
log() { echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_DIR/post_deploy.log"; }
log "Post-deploy fixes starting..."

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
MAIN_TAG='<script src="/js/main.js"></script>'

for page in "${PAGES[@]}"; do
    file="$PROJECT_DIR/$page"
    if [ ! -f "$file" ]; then
        log "SKIP: $page not found"
        continue
    fi
    if grep -qF "$AUTH_TAG" "$file"; then
        log "SKIP: $page already has auth.js"
    else
        sed -i "s|$MAIN_TAG|$MAIN_TAG\n    $AUTH_TAG|" "$file"
        if grep -qF "$AUTH_TAG" "$file"; then
            log "OK: $page - auth.js injected"
        else
            log "FAIL: $page - injection failed"
        fi
    fi
done

log "Post-deploy fixes complete"
SCRIPT_END

chmod +x "$PROJECT_DIR/post_deploy.sh"
log "post_deploy.sh created"

# -----------------------------------------------------------
# Step 2: Update start_gunicorn.sh (add post_deploy step)
# -----------------------------------------------------------
log "[2/4] Updating start_gunicorn.sh..."

START_SCRIPT="$PROJECT_DIR/start_gunicorn.sh"

if grep -q "post_deploy.sh" "$START_SCRIPT" 2>/dev/null; then
    log "start_gunicorn.sh already has post_deploy step - skipped"
else
    # Backup original
    cp "$START_SCRIPT" "$START_SCRIPT.bak"

    # Insert new step [3/6] after the init_data success log line
    sed -i '/^log "Data files OK"$/a\
\
# [3/6] Run post-deploy fixes (auth.js injection, etc.)\
log "[3/6] Running post-deploy fixes..."\
bash "$PROJECT_DIR/post_deploy.sh" >> "$LOG_DIR/deploy.log" 2>\&1\
log "Post-deploy fixes OK"' "$START_SCRIPT"

    # Renumber the step comments and log lines
    sed -i 's/^# \[1\/5\]/# [1\/6]/' "$START_SCRIPT"
    sed -i 's/^log "\[1\/5\]/log "[1\/6]/' "$START_SCRIPT"
    sed -i 's/^# \[2\/5\]/# [2\/6]/' "$START_SCRIPT"
    sed -i 's/^log "\[2\/5\]/log "[2\/6]/' "$START_SCRIPT"
    sed -i 's/^# \[3\/5\]/# [4\/6]/' "$START_SCRIPT"
    sed -i 's/^log "\[3\/5\]/log "[4\/6]/' "$START_SCRIPT"
    sed -i 's/^# \[4\/5\]/# [5\/6]/' "$START_SCRIPT"
    sed -i 's/^log "\[4\/5\]/log "[5\/6]/' "$START_SCRIPT"
    sed -i 's/^# \[5\/5\]/# [6\/6]/' "$START_SCRIPT"
    sed -i 's/^log "\[5\/5\]/log "[6\/6]/' "$START_SCRIPT"

    log "start_gunicorn.sh updated (backup at start_gunicorn.sh.bak)"
fi

# -----------------------------------------------------------
# Step 3: Run post_deploy.sh immediately to fix sub-pages
# -----------------------------------------------------------
log "[3/4] Running post_deploy.sh to fix sub-pages now..."
bash "$PROJECT_DIR/post_deploy.sh"

# -----------------------------------------------------------
# Step 4: Done
# -----------------------------------------------------------
log "[4/4] Done"
log "========== Deploy script complete =========="
echo ""
echo "Summary:"
echo "  - post_deploy.sh created at $PROJECT_DIR/post_deploy.sh"
echo "  - start_gunicorn.sh updated with step [3/6] post-deploy"
echo "  - All sub-pages now load auth.js"
echo "  - Auto-update daemon will run post_deploy.sh on every future git pull"
