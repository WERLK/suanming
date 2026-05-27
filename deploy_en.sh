#!/bin/bash
# Xuanji Fortune Telling - One-Click Deployment Script (English Version)
# Server IP: 8.153.90.109

echo "======================================"
echo "  Xuanji Fortune - One-Click Deployment"
echo "  Server IP: 8.153.90.109"
echo "======================================"
echo ""

# 1. Pull latest code
echo "[1] Pulling latest code..."
cd /root/suanming && git pull origin main
if [ $? -eq 0 ]; then
    echo "  ✅ Code pulled successfully"
else
    echo "  ❌ Code pull failed"
    exit 1
fi
echo ""

# 2. Create data files
echo "[2] Creating data files..."
cd /root/suanming

mkdir -p data
echo '{}' > data/favorites.json
echo '{}' > data/shares.json
echo '{}' > data/reports.json
echo '{}' > data/notifications.json
echo '{}' > data/privacy.json

chmod 644 data/*.json

mkdir -p static/avatars
chmod 755 static/avatars

echo "  ✅ Data files created successfully"
echo "      File list:"
ls -lh data/*.json | awk '{print "     ", $9, "("$5")"}'
echo ""
echo "      Directory list:"
ls -ld static/avatars | awk '{print "     ", $9}'
echo ""

# 3. Stop old process
echo "[3] Stopping old process..."
pkill -f gunicorn
sleep 5

if pgrep -f "gunicorn.*app:app" >/dev/null; then
    echo "  ⚠️  Old process still running, force killing..."
    pkill -9 -f gunicorn
    sleep 3
fi

echo "  ✅ Old process stopped"
echo ""

# 4. Start new process
echo "[4] Starting new process (timeout: 300 seconds)..."
cd /root/suanming/api
nohup gunicorn -w 4 -t 300 -b 0.0.0.0:5000 app:app > /root/suanming/logs/gunicorn.log 2>&1 &

sleep 5

if pgrep -f "gunicorn.*app:app" >/dev/null; then
    echo "  ✅ New process started successfully"
    echo "      Process info:"
    ps aux | grep "gunicorn.*app:app" | grep -v grep | head -2 | awk '{print "       PID:", $2, "  Start time:", $9}'
else
    echo "  ❌ New process failed to start"
    echo "      Check log: tail -f /root/suanming/logs/gunicorn.log"
    exit 1
fi
echo ""

# 5. Check service status
echo "[5] Checking service status..."
cd /root/suanming

if [ -f "backend_check.py" ]; then
    python3 backend_check.py
else
    echo "  ⚠️  backend_check.py not found, skipping detailed check"
    echo "      You can manually check: python3 backend_check.py"
fi
echo ""

echo "======================================"
echo "  Deployment completed!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Open browser and visit: http://8.153.90.109"
echo "  2. Test avatar upload (Personal Center)"
echo "  3. Test version display (bottom-right corner)"
echo "  4. Test all features (Favorites, Shares, Reports, etc.)"
echo ""
