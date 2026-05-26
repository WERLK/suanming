#!/bin/bash
# 玄机算命网 - 一键修复脚本
# 用法: bash fix.sh

set -e
cd /root/suanming/suanming

echo "=== 1. 停止旧进程 ==="
pkill -f auto_update 2>/dev/null || true
pkill -f gunicorn 2>/dev/null || true
sleep 2
echo "OK"

echo "=== 2. 下载最新代码 ==="
rm -rf api/__pycache__
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/api/app.py -O api/app.py
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/api/__init__.py -O api/__init__.py
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/gunicorn_config.py -O gunicorn_config.py
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/icon-192.png -O icon-192.png
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/manifest.json -O manifest.json
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/auto_update_daemon.py -O auto_update_daemon.py
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/fix.sh -O fix.sh
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/index.html -O index.html
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/js/main.js -O js/main.js
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/css/style.css -O css/style.css
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/modules/tarot.html -O modules/tarot.html
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/modules/fengshui.html -O modules/fengshui.html
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/modules/shengxiao.html -O modules/shengxiao.html
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/modules/ziwei.html -O modules/ziwei.html
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/more.html -O more.html
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/profile.html -O profile.html
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/login.html -O login.html
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/register.html -O register.html
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/modules/bazi.html -O modules/bazi.html
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/modules/xingzuo.html -O modules/xingzuo.html
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/login_backup_v2.html -O login_backup_v2.html
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/login_with_sms.html -O login_with_sms.html
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/register_backup.html -O register_backup.html
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/register_with_captcha.html -O register_with_captcha.html
wget -q https://raw.githubusercontent.com/WERLK/suanming/master/sms_login_patch.html -O sms_login_patch.html
echo "OK"

echo "=== 3. 验证代码 ==="
python3 -c "from api.app import app; print('导入成功')"
echo "OK"

echo "=== 4. 启动服务 ==="
mkdir -p logs
nohup python3 -m gunicorn -c gunicorn_config.py api.app:app > logs/gunicorn.log 2>&1 &
sleep 3

echo "=== 5. 测试 ==="
curl -s -o /dev/null -w "首页: HTTP %{http_code}\n" http://localhost:5000
curl -s -o /dev/null -w "登录: HTTP %{http_code}\n" http://localhost:5000/login.html
curl -s -o /dev/null -w "八字: HTTP %{http_code}\n" http://localhost:5000/modules/bazi.html
curl -s -o /dev/null -w "CSS:  HTTP %{http_code}\n" http://localhost:5000/css/style.css

echo ""
echo "=== 全部完成 ==="
echo "访问: http://你的IP:5000"
