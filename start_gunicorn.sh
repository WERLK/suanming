#!/bin/bash
# One-click deploy: pull -> init data -> load env -> start gunicorn
cd /root/suanming

echo "=== [1/4] Pull code ==="
git pull origin main

echo "=== [2/4] Init data files ==="
python3 init_data.py

echo "=== [3/4] Load env ==="
if [ -f /etc/profile.d/aliyun_sms.sh ]; then
    source /etc/profile.d/aliyun_sms.sh
fi

echo "=== [4/4] Install SDK + start gunicorn ==="
cd /root/suanming/api

# Ensure aliyun SDK is installed for the correct python3
python3 -m pip install aliyun-python-sdk-core aliyun-python-sdk-dysmsapi --quiet 2>/dev/null

pkill -f gunicorn 2>/dev/null || true
sleep 3
nohup gunicorn -w 4 -t 300 -b 0.0.0.0:5000 app:app > /root/suanming/logs/gunicorn.log 2>&1 &
sleep 3

echo ""
echo "=== Done ==="
cd /root/suanming && python3 backend_check.py
