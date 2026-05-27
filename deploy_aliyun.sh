#!/bin/bash
# 玄机算命网 - 阿里云一键部署脚本（通用版）
# 功能：自动配置 Python 3.11 + 依赖 + Gunicorn + Systemd 守护
# 使用方法：
#   1. 上传本脚本到阿里云服务器（如 /home/）
#   2. 运行：bash deploy_aliyun.sh
#   3. 访问：http://你的阿里云IP:5000

set -e  # 遇到错误立即退出

echo "=================================================="
echo "🎉 玄机算命网 - 阿里云后端部署脚本"
echo "=================================================="
echo ""

# ========== 配置变量 ==========
PROJECT_NAME="suanming-fix"
PROJECT_DIR="/home/$PROJECT_NAME"
GITHUB_REPO="https://github.com/WERLK/suanming.git"
PYTHON_VERSION="3.11"
PORT=5000
echo "📂 项目目录：$PROJECT_DIR"
echo "🌐 GitHub 仓库：$GITHUB_REPO"
echo "🐍 Python 版本：$PYTHON_VERSION"
echo "🚀 监听端口：$PORT"
echo ""

# ========== 1. 更新系统并安装依赖 ==========
echo "📦 第 1 步：更新系统并安装 Python 3.11..."
apt-get update -y
apt-get install -y python3.11 python3.11-venv python3.11-dev
apt-get install -y git nginx redis-server
echo "✅ 系统依赖安装完成"
echo ""

# ========== 2. 克隆或更新项目 ==========
echo "📦 第 2 步：克隆项目从 GitHub..."
if [ -d "$PROJECT_DIR" ]; then
    echo "⚠️  目录已存在，执行 Git 拉取更新..."
    cd $PROJECT_DIR
    git pull origin main
else
    echo "⚠️  首次克隆项目..."
    git clone $GITHUB_REPO $PROJECT_DIR
    cd $PROJECT_DIR
fi
echo "✅ 项目代码更新完成"
echo ""

# ========== 3. 创建 Python 虚拟环境 ==========
echo "📦 第 3 步：创建 Python 虚拟环境..."
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
fi
source venv/bin/activate
echo "✅ 虚拟环境创建并激活"
echo ""

# ========== 4. 安装 Python 依赖 ==========
echo "📦 第 4 步：安装 Python 依赖..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python 依赖安装完成"
echo ""

# ========== 5. 配置 Gunicorn（生产级 WSGI） ==========
echo "📦 第 5 步：配置 Gunicorn..."
GUNICORN_CONF="/etc/systemd/system/$PROJECT_NAME.service"

# 创建 Systemd 服务文件
cat > $GUNICORN_CONF << EOF
[Unit]
Description=玄机算命网后端 API 服务
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn -c gunicorn_config.py api.app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable $PROJECT_NAME
systemctl restart $PROJECT_NAME
echo "✅ Gunicorn 服务配置完成并已启动"
echo ""

# ========== 6. 配置 Nginx 反向代理（可选） ==========
echo "📦 第 6 步：配置 Nginx 反向代理（可选）..."
cat > /etc/nginx/sites-available/$PROJECT_NAME << EOF
server {
    listen 80;
    server_name _;  # 改成你的域名，如 api.xuanji.com

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    # 静态文件直接由 Nginx 提供（加速）
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        root $PROJECT_DIR;
        expires 30d;
    }
}
EOF

ln -sf /etc/nginx/sites-available/$PROJECT_NAME /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
echo "✅ Nginx 反向代理配置完成"
echo ""

# ========== 7. 配置防火墙（开放端口） ==========
echo "📦 第 7 步：配置防火墙..."
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow $PORT/tcp
echo "✅ 防火墙规则配置完成"
echo ""

# ========== 8. 实时更新配置（Git Webhook） ==========
echo "📦 第 8 步：配置实时更新（Git Webhook）..."
# 创建 Webhook 脚本
cat > $PROJECT_DIR/update_webhook.sh << 'EOF'
#!/bin/bash
cd /home/suanming-fix
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
systemctl restart suanming-fix
echo "✅ 代码已更新并重启服务"
EOF

chmod +x $PROJECT_DIR/update_webhook.sh

# 提示用户如何在 GitHub 配置 Webhook
echo "📝 如需实时更新，请在 GitHub 仓库设置 Webhook："
echo "   URL：http://你的阿里云IP:5000/update-secret-2026"
echo "   Content type：application/json"
echo ""

# ========== 完成 ==========
echo "=================================================="
echo "🎉 部署完成！"
echo "=================================================="
echo ""
echo "📊 服务状态："
systemctl status $PROJECT_NAME --no-pager
echo ""
echo "📈 查看日志："
echo "   journalctl -u $PROJECT_NAME -f"
echo ""
echo "🚀 测试访问："
echo "   curl http://localhost:$PORT/api/fortune/health"
echo ""
echo "🌐 公网访问："
echo "   http://你的阿里云IP:$PORT/api/fortune/health"
echo ""
echo "=================================================="
echo "✅ 脚本执行完成！"
echo "=================================================="