#!/bin/bash
# 玄机算命网 - 一键修复/部署脚本
# 支持: 首次部署(空目录) 或 热更新(已有代码)
# 用法: cd 到项目目录后执行 bash fix.sh

set -e

# 使用当前目录作为目标目录（不再硬编码）
TARGET_DIR="$(pwd)"

echo "=== 目标目录: $TARGET_DIR ==="

# ========== 1. 检查核心文件是否存在 ==========
if [ ! -f "api/app.py" ]; then
    echo "=== 首次部署: 从 GitHub 克隆完整代码 ==="
    TMP_DIR="/tmp/suanming_clone_$$"
    rm -rf "$TMP_DIR"
    git clone --depth=1 https://github.com/WERLK/suanming.git "$TMP_DIR"
    # 移动文件到当前目录
    cp -r "$TMP_DIR"/* "$TARGET_DIR/" 2>/dev/null || true
    cp -r "$TMP_DIR"/.[!.]* "$TARGET_DIR/" 2>/dev/null || true
    rm -rf "$TMP_DIR"
    echo "代码克隆完成"
else
    # ========== 2. 热更新: 只覆盖核心文件 ==========
    echo "=== 热更新: 下载最新核心文件 ==="
    rm -rf api/__pycache__
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/api/app.py -O api/app.py
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/api/__init__.py -O api/__init__.py
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/gunicorn_config.py -O gunicorn_config.py
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/icon-192.png -O icon-192.png
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/manifest.json -O manifest.json
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/auto_update_daemon.py -O auto_update_daemon.py
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/index.html -O index.html
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/js/main.js -O js/main.js
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/css/style.css -O css/style.css
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/modules/tarot.html -O modules/tarot.html
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/modules/fengshui.html -O modules/fengshui.html
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/modules/shengxiao.html -O modules/shengxiao.html
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/modules/ziwei.html -O modules/ziwei.html
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/more.html -O more.html
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/profile.html -O profile.html
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/login.html -O login.html
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/register.html -O register.html
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/modules/bazi.html -O modules/bazi.html
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/modules/xingzuo.html -O modules/xingzuo.html
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/login_backup_v2.html -O login_backup_v2.html
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/login_with_sms.html -O login_with_sms.html
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/register_backup.html -O register_backup.html
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/register_with_captcha.html -O register_with_captcha.html
    wget -q https://raw.githubusercontent.com/WERLK/suanming/main/sms_login_patch.html -O sms_login_patch.html
    echo "热更新完成"
fi

# ========== 3. 安装依赖 ==========
echo "=== 检查依赖 ==="
pip3 install flask flask-cors gunicorn pillow pyjwt 2>/dev/null || true
echo "OK"

# ========== 4. 停止旧进程 ==========
echo "=== 停止旧进程 ==="
pkill -f auto_update 2>/dev/null || true
pkill -f gunicorn 2>/dev/null || true
sleep 2
echo "OK"

# ========== 5. 验证代码 ==========
echo "=== 验证代码 ==="
python3 -c "from api.app import app; print('导入成功')"
echo "OK"

# ========== 6. 启动服务 ==========
echo "=== 启动服务 ==="
mkdir -p logs
nohup python3 -m gunicorn -c gunicorn_config.py api.app:app > logs/gunicorn.log 2>&1 &
sleep 3

# ========== 7. 启动自动更新守护进程 ==========
echo "=== 启动自动更新守护进程 ==="
nohup python3 auto_update_daemon.py > logs/auto_update.log 2>&1 &
sleep 1
echo "自动更新进程已启动（每5分钟检查更新）"

# ========== 8. 测试 ==========
echo "=== 测试 ==="
curl -s -o /dev/null -w "首页:     HTTP %{http_code}\n" http://localhost:5000
curl -s -o /dev/null -w "登录:     HTTP %{http_code}\n" http://localhost:5000/login.html
curl -s -o /dev/null -w "八字:     HTTP %{http_code}\n" http://localhost:5000/modules/bazi.html
curl -s -o /dev/null -w "CSS:      HTTP %{http_code}\n" http://localhost:5000/css/style.css
curl -s -o /dev/null -w "模块列表: HTTP %{http_code}\n" http://localhost:5000/module_list.json

echo ""
echo "=== 全部完成 ==="
echo "访问: http://你的IP:5000"

# ========== 9. 显示运行状态 ==========
echo ""
if [ -f "status.sh" ]; then
    bash status.sh
else
    echo "(status.sh 不存在，跳过状态检查)"
fi
