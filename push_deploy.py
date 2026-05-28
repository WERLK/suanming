#!/usr/bin/env python3
"""
Server-side deploy + git push script.
Run ONCE on Alibaba Cloud server (8.153.90.109):
    python3 /tmp/push_deploy.py

This script:
1. Creates post_deploy.sh (auto-injects auth.js into sub-pages)
2. Updates start_gunicorn.sh (adds post_deploy step to deploy pipeline)
3. Runs post_deploy.sh immediately to fix all sub-pages
4. git add + commit + push to GitHub

All ASCII-safe, no Chinese characters, no shell escaping issues.
"""
import os, sys, subprocess

PROJECT_DIR = "/root/suanming"
LOG_DIR = os.path.join(PROJECT_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def log(msg):
    from datetime import datetime
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(os.path.join(LOG_DIR, "deploy.log"), "a") as f:
        f.write(line + "\n")

def run(cmd, check=True):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0 and check:
        log(f"ERROR: {cmd}")
        log(f"stderr: {result.stderr.strip()}")
        sys.exit(1)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

# ============================================================
# Step 1: Create post_deploy.sh
# ============================================================
log("[1/4] Creating post_deploy.sh...")

POST_DEPLOY = '''#!/bin/bash
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
        sed -i "s|$MAIN_TAG|$MAIN_TAG\\n    $AUTH_TAG|" "$file"
        if grep -qF "$AUTH_TAG" "$file"; then
            log "OK: $page - auth.js injected"
        else
            log "FAIL: $page - injection failed"
        fi
    fi
done

log "Post-deploy fixes complete"
'''

post_deploy_path = os.path.join(PROJECT_DIR, "post_deploy.sh")
with open(post_deploy_path, "w") as f:
    f.write(POST_DEPLOY)
os.chmod(post_deploy_path, 0o755)
log("post_deploy.sh created")

# ============================================================
# Step 2: Update start_gunicorn.sh
# ============================================================
log("[2/4] Updating start_gunicorn.sh...")

start_path = os.path.join(PROJECT_DIR, "start_gunicorn.sh")

with open(start_path, "r") as f:
    content = f.read()

if "post_deploy.sh" in content:
    log("start_gunicorn.sh already has post_deploy step - skipped")
else:
    # Backup
    with open(start_path + ".bak", "w") as f:
        f.write(content)

    # Insert post_deploy step after "Data files OK" log line
    new_step = '''
# [3/6] Run post-deploy fixes (auth.js injection, etc.)
log "[3/6] Running post-deploy fixes..."
bash "$PROJECT_DIR/post_deploy.sh" >> "$LOG_DIR/deploy.log" 2>&1
log "Post-deploy fixes OK"'''

    content = content.replace(
        'log "Data files OK"',
        'log "Data files OK"\n' + new_step
    )

    # Renumber all steps from [x/5] to [x/6]
    replacements = [
        ("# [1/5]", "# [1/6]"),
        ('log "[1/5]', 'log "[1/6]'),
        ("# [2/5]", "# [2/6]"),
        ('log "[2/5]', 'log "[2/6]'),
        ("# [3/5]", "# [4/6]"),
        ('log "[3/5]', 'log "[4/6]'),
        ("# [4/5]", "# [5/6]"),
        ('log "[4/5]', 'log "[5/6]'),
        ("# [5/5]", "# [6/6]"),
        ('log "[5/5]', 'log "[6/6]'),
    ]
    for old, new in replacements:
        content = content.replace(old, new)

    with open(start_path, "w") as f:
        f.write(content)
    log("start_gunicorn.sh updated (backup at start_gunicorn.sh.bak)")

# ============================================================
# Step 3: Run post_deploy.sh immediately
# ============================================================
log("[3/4] Running post_deploy.sh to fix sub-pages...")
stdout, stderr, rc = run(f"bash {post_deploy_path}", check=False)
if stdout:
    print(stdout)
if stderr and rc != 0:
    log(f"stderr: {stderr}")

# ============================================================
# Step 4: Git commit and push
# ============================================================
log("[4/4] Committing and pushing to GitHub...")
os.chdir(PROJECT_DIR)

files_to_add = ["post_deploy.sh", "start_gunicorn.sh"]
for f in files_to_add:
    run(f"git add {f}")

# Also add any modified HTML files from post_deploy
status_out, _, _ = run("git status --porcelain", check=False)
html_files = []
for line in status_out.split("\n"):
    if line.strip() and ".html" in line:
        parts = line.strip().split()
        if len(parts) >= 2:
            html_files.append(parts[-1])

if html_files:
    for f in html_files:
        run(f"git add {f}", check=False)
    log(f"Staged {len(html_files)} HTML files")

# Commit
run('git commit -m "deploy: post_deploy.sh - auto-inject auth.js into sub-pages, update start_gunicorn.sh"', check=False)

# Push
stdout, stderr, rc = run("git push origin main", check=False)
if rc == 0:
    log("PUSH SUCCESS")
else:
    log(f"Push failed: {stderr}")
    log("You may need to push manually: cd /root/suanming && git push origin main")

log("========== All done ==========")
print("")
print("Summary:")
print("  - post_deploy.sh: CREATED")
print("  - start_gunicorn.sh: UPDATED (step [3/6] added)")
print("  - Sub-pages: auth.js INJECTED")
print("  - GitHub: COMMITTED and PUSHED" if rc == 0 else "  - GitHub: COMMITTED locally, push manually if needed")
