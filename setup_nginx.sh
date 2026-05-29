#!/bin/bash
# Nginx setup script for xuanjisuanming.top
# Idempotent - safe to run multiple times
# Usage: sudo bash setup_nginx.sh

set -e

DOMAIN="xuanjisuanming.top"
WWW_DOMAIN="www.xuanjisuanming.top"
NGINX_SITE="/etc/nginx/sites-available/xjsm"
NGINX_ENABLED="/etc/nginx/sites-enabled/xjsm"
PROXY_PORT="5000"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "[$(date '+%H:%M:%S')] $1"; }

# ── Check if running as root or has sudo ──
if [ "$(id -u)" -ne 0 ]; then
    log "${RED}ERROR: This script must be run as root or with sudo${NC}"
    exit 1
fi

# ── Ensure nginx is installed ──
if ! command -v nginx &>/dev/null; then
    log "${YELLOW}Nginx not found, installing...${NC}"
    apt update -qq && apt install nginx -y
fi

# ── Write Nginx config ──
log "Writing Nginx config to $NGINX_SITE..."

cat > "$NGINX_SITE" << 'NGINX_EOF'
# HTTP server block
server {
    listen 80;
    server_name xuanjisuanming.top www.xuanjisuanming.top;

    client_max_body_size 10M;

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 10s;
    }

    # Static files served directly
    location /static/ {
        alias /root/suanming/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Health check
    location /health {
        return 200 "OK";
        add_header Content-Type text/plain;
    }
}
NGINX_EOF

# ── Enable site, disable default ──
log "Enabling site..."
ln -sf "$NGINX_SITE" "$NGINX_ENABLED"
rm -f /etc/nginx/sites-enabled/default

# ── Test and reload ──
log "Testing Nginx config..."
if nginx -t 2>&1; then
    log "${GREEN}Config OK, reloading Nginx...${NC}"
    systemctl reload nginx 2>/dev/null || systemctl restart nginx
    log "${GREEN}Nginx setup complete!${NC}"
    log "Site should be accessible at: http://$DOMAIN"
else
    log "${RED}Nginx config test FAILED. Check $NGINX_SITE${NC}"
    exit 1
fi
