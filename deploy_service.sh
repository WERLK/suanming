#!/bin/bash
# Install systemd service for permanent auto-start

# Source existing env file (contains AccessKey from server)
BASH_ENV="/etc/profile.d/aliyun_sms.sh"
ENV_FILE="/etc/suanming.env"

if [ -f "$BASH_ENV" ]; then
    source "$BASH_ENV"
    # Convert to systemd format (KEY=value, no export, no quotes)
    {
        echo "ALIYUN_ACCESS_KEY_ID=${ALIYUN_ACCESS_KEY_ID}"
        echo "ALIYUN_ACCESS_KEY_SECRET=${ALIYUN_ACCESS_KEY_SECRET}"
        echo "ALIYUN_SIGN_NAME=速通互联验证码"
        echo "ALIYUN_TEMPLATE_CODE=100001"
    } > "$ENV_FILE"
    echo "Created $ENV_FILE from $BASH_ENV"
else
    echo "WARNING: $BASH_ENV not found, SMS will use demo mode"
    rm -f "$ENV_FILE"
fi

cat > /etc/systemd/system/suanming.service << SERV
[Unit]
Description=Suanming Fortune API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/suanming/api
Environment=PYTHONPATH=/root/.pyenv/versions/3.11.1/lib/python3.11/site-packages
EnvironmentFile=$ENV_FILE
ExecStartPre=/bin/bash -c 'cd /root/suanming && git fetch origin main && git reset --hard origin/main && python3 init_data.py'
ExecStart=python3 -m gunicorn -w 4 -t 300 -b 0.0.0.0:5000 app:app
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=5
StandardOutput=append:/root/suanming/logs/gunicorn.log
StandardError=append:/root/suanming/logs/gunicorn.log

[Install]
WantedBy=multi-user.target
SERV

systemctl daemon-reload
systemctl enable suanming.service
systemctl restart suanming.service
sleep 3
systemctl status suanming.service --no-pager
