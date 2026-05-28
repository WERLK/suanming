#!/bin/bash
# Install systemd service for permanent auto-start

# Convert bash-style env file to systemd-compatible format
BASH_ENV="/etc/profile.d/aliyun_sms.sh"
SYSTEMD_ENV="/etc/suanming.env"

if [ -f "$BASH_ENV" ]; then
    # Remove 'export ', remove quotes around values
    sed "s/^export //" "$BASH_ENV" | sed "s/'//g" > "$SYSTEMD_ENV"
    echo "Created $SYSTEMD_ENV from $BASH_ENV"
else
    echo "WARNING: $BASH_ENV not found, SMS will use demo mode"
    rm -f "$SYSTEMD_ENV"
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
EnvironmentFile=-$SYSTEMD_ENV
ExecStartPre=/bin/bash -c 'cd /root/suanming && git fetch origin main && git reset --hard origin/main && python3 init_data.py'
ExecStart=/usr/bin/python3 -m gunicorn -w 4 -t 300 -b 0.0.0.0:5000 app:app
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
