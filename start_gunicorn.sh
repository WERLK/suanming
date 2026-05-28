#!/bin/bash
cd /root/suanming/api

# Auto-detect pip site-packages and add to PYTHONPATH
PYPATH=$(pip3 show aliyun-python-sdk-core 2>/dev/null | grep Location | awk '{print $2}')
if [ -n "$PYPATH" ]; then
    export PYTHONPATH="${PYPATH}:${PYTHONPATH}"
fi

# Aliyun SMS env vars must be set before running this script
# export ALIYUN_ACCESS_KEY_ID='your_key_id'
# export ALIYUN_ACCESS_KEY_SECRET='your_key_secret'

pkill -f gunicorn
sleep 3
nohup gunicorn -w 4 -t 300 -b 0.0.0.0:5000 app:app > /root/suanming/logs/gunicorn.log 2>&1 &
sleep 3
echo "Gunicorn started, PID: $(pgrep -f 'gunicorn.*app:app' | head -1)"
