#!/bin/bash
# Install systemd service for permanent auto-start

cat > /etc/systemd/system/suanming.service << 'SERV'
[Unit]
Description=Suanming Fortune API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/suanming/api
Environment=PYTHONPATH=/root/.pyenv/versions/3.11.1/lib/python3.11/site-packages
EnvironmentFile=-/etc/profile.d/aliyun_sms.sh
ExecStartPre=/bin/bash -c 'cd /root/suanming && git fetch origin main && git reset --hard origin/main && python3 init_data.py'
ExecStart=/usr/bin/python3 -m gunicorn -w 4 -t 300 -b 0.0.0.0:5000 app:app
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=append:/root/suanming/logs/gunicorn.log
StandardError=append:/root/suanming/logs/gunicorn.log

[Install]
WantedBy=multi-user.target
SERV

systemctl daemon-reload
systemctl enable suanming.service
systemctl start suanming.service
sleep 3
systemctl status suanming.service --no-pager
