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

echo "=== [4/4] Start gunicorn ==="
cd /root/suanming/api
PYPATH=$(pip3 show aliyun-python-sdk-core 2>/dev/null | grep Location | awk '{print $2}')
[ -n "$PYPATH" ] && export PYTHONPATH="${PYPATH}:${PYTHONPATH}"

pkill -f gunicorn 2>/dev/null || true
sleep 3
nohup gunicorn -w 4 -t 300 -b 0.0.0.0:5000 app:app > /root/suanming/logs/gunicorn.log 2>&1 &
sleep 3

echo ""
echo "=== Done ==="
cd /root/suanming && python3 backend_check.py
