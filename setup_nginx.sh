#!/bin/bash
# Nginx setup script for xuanjisuanming.top (HTTP + HTTPS)
# Idempotent - safe to run multiple times
# Usage: sudo bash setup_nginx.sh

set -e

DOMAIN="xuanjisuanming.top"
WWW_DOMAIN="www.xuanjisuanming.top"
NGINX_SITE="/etc/nginx/sites-available/xjsm"
NGINX_ENABLED="/etc/nginx/sites-enabled/xjsm"

# certbot may append -0001 suffix, auto-detect the directory
CERT_BASE=$(ls -d /etc/letsencrypt/live/${DOMAIN}* 2>/dev/null | head -1)
CERT_FILE="${CERT_BASE}/fullchain.pem"
KEY_FILE="${CERT_BASE}/privkey.pem"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "[$(date '+%H:%M:%S')] $1"; }

# Check root
if [ "$(id -u)" -ne 0 ]; then
    log "${RED}ERROR: This script must be run as root or with sudo${NC}"
    exit 1
fi

# Ensure nginx is installed
if ! command -v nginx &>/dev/null; then
    log "${YELLOW}Nginx not found, installing...${NC}"
    apt update -qq && apt install nginx -y
fi

# Enable site, disable default
ln -sf "$NGINX_SITE" "$NGINX_ENABLED"
rm -f /etc/nginx/sites-enabled/default

# Detect HTTPS capability
if [ -f "$CERT_FILE" ]; then
    log "${GREEN}SSL certificate found: ${CERT_BASE}${NC}"

    cat > "$NGINX_SITE" << NGINX_EOF
# HTTP -> HTTPS redirect
server {
    listen 80;
    server_name xuanjisuanming.top www.xuanjisuanming.top;
    return 301 https://\$host\$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name xuanjisuanming.top www.xuanjisuanming.top;

    ssl_certificate ${CERT_FILE};
    ssl_certificate_key ${KEY_FILE};
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 10s;
    }

    location /static/ {
        alias /root/suanming/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /health {
        return 200 "OK";
        add_header Content-Type text/plain;
    }
}
NGINX_EOF

else
    log "${YELLOW}No SSL certificate found, writing HTTP-only config...${NC}"
    log "${YELLOW}To enable HTTPS, run: sudo certbot --nginx -d $DOMAIN -d $WWW_DOMAIN${NC}"

    cat > "$NGINX_SITE" << 'NGINX_EOF'
server {
    listen 80;
    server_name xuanjisuanming.top www.xuanjisuanming.top;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 10s;
    }

    location /static/ {
        alias /root/suanming/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /health {
        return 200 "OK";
        add_header Content-Type text/plain;
    }
}
NGINX_EOF

fi

# Test and reload
log "Testing Nginx config..."
if nginx -t 2>&1; then
    log "${GREEN}Config OK, reloading Nginx...${NC}"
    systemctl reload nginx 2>/dev/null || systemctl restart nginx
    if [ -f "$CERT_FILE" ]; then
        log "${GREEN}Site: https://$DOMAIN${NC}"
    else
        log "${GREEN}Site: http://$DOMAIN${NC}"
    fi
else
    log "${RED}Nginx config test FAILED${NC}"
    exit 1
fi
