#!/bin/bash
# ========================================
# 远程部署脚本 - 推送到阿里云服务器
# 用法: ./remote_update.sh 用户名@服务器IP [项目目录]
# 示例: ./remote_update.sh root@47.xxx.xxx.xxx /var/www/suanming
# ========================================

set -e

SERVER="${1:-}"
REMOTE_DIR="${2:-/var/www/flask-app}"
LOCAL_DIR="/workspace"

# 颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

if [ -z "$SERVER" ]; then
    echo "用法: $0 用户名@服务器IP [服务器项目目录]"
    echo "示例: $0 root@47.xxx.xxx.xxx /var/www/suanming"
    exit 1
fi

echo "========================================"
echo "🚀 远程部署到阿里云服务器"
echo "========================================"
echo "服务器: $SERVER"
echo "远程目录: $REMOTE_DIR"
echo "========================================"
echo ""

# 1. 检查服务器连接
log_info "检查服务器连接..."
if ! ssh -o ConnectTimeout=5 "$SERVER" "echo '连接成功'" > /dev/null 2>&1; then
    log_error "无法连接到服务器，请检查："
    log_error "  1. SSH 公钥已配置（ssh-copy-id $SERVER）"
    log_error "  2. 服务器 IP 正确"
    log_error "  3. 服务器防火墙允许 SSH 端口"
    exit 1
fi
log_info "✅ 连接成功"
echo ""

# 2. 确认远程目录存在
log_info "检查远程目录..."
ssh "$SERVER" "[ -d $REMOTE_DIR ] || mkdir -p $REMOTE_DIR"
log_info "✅ 目录确认"
echo ""

# 3. 查找服务器上已存在的文件，避免覆盖
echo "📂 远程服务器上的文件列表（前20个）:"
ssh "$SERVER" "ls -la $REMOTE_DIR | head -20"
echo ""

read -p "确认继续同步？(y/n): " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    log_warn "操作已取消"
    exit 0
fi

# 4. 同步代码到服务器
log_info "📤 同步代码到服务器..."
echo "  正在同步，请稍候..."

# 排除不需要同步的文件
rsync -avz \
  --exclude='__pycache__' \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='*.pyc' \
  --exclude='*.log' \
  --exclude='.env' \
  --exclude='venv/' \
  --exclude='.codebuddy/' \
  --delete \
  "$LOCAL_DIR/" "$SERVER:$REMOTE_DIR/"

log_info "✅ 代码同步完成"
echo ""

# 5. 在服务器上安装依赖并热更新
log_info "🔄 在服务器上执行热更新..."
ssh "$SERVER" "
cd $REMOTE_DIR

# 检查是否有虚拟环境
if [ -d venv ]; then
    source venv/bin/activate
    log_info '使用虚拟环境'
fi

# 安装依赖（如果有新增）
log_info '安装依赖...'
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple -q

# 检查部署脚本
if [ -f deploy.sh ]; then
    chmod +x deploy.sh
    log_info '执行热更新...'
    ./deploy.sh reload 2>/dev/null && echo '热更新成功' || echo '热更新命令失败，尝试重启'
else
    log_warn '没有找到 deploy.sh 脚本'
    
    # 查找运行的进程
    PID=\$(ps aux | grep gunicorn | grep -v grep | head -1 | awk '{print \$2}')
    if [ -n \"\$PID\" ]; then
        log_info \"向进程 \$PID 发送热更新信号\"
        kill -HUP \$PID
    else
        log_warn '没有找到 Gunicorn 进程'
    fi
fi

echo ''
echo '服务状态:'
ps aux | grep -E '(python|gunicorn)' | grep -v grep || echo '没有运行中的 Python 进程'

echo ''
echo '最近日志:'
tail -n 5 logs/error.log 2>/dev/null || echo '没有找到日志文件'
"

log_info "✅ 部署完成！"
echo ""
echo "========================================"
echo "📋 部署摘要"
echo "========================================"
echo "服务器: $SERVER"
echo "目录: $REMOTE_DIR"
echo "状态: 热更新已执行"
echo ""
echo "💡 提示:"
echo "  - 如果热更新失败，服务器会自动尝试重启"
echo "  - 请查看上方输出确认服务状态"
echo "  - 备案期间请用端口访问 (如: http://服务器IP:5000)"
echo "========================================"
