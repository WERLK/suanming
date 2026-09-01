#!/bin/bash
# 远程更新脚本 - 正确版本
# 服务器 IP: 8.153.90.109

echo "===== 玄机算命网 远程更新 ====="
echo ""

# 1. 拉取最新代码
echo "[1/4] 拉取 GitHub 最新代码..."
cd /root/suanming && git pull origin main

if [ $? -eq 0 ]; then
    echo "✅ 代码更新成功"
else
    echo "❌ 代码更新失败"
    exit 1
fi

# 2. 停止旧进程
echo ""
echo "[2/4] 停止旧后端进程..."
pkill -f gunicorn
sleep 5

# 3. 启动新进程
echo ""
echo "[3/4] 启动后端服务..."
cd /root/suanming/api
nohup gunicorn -w 4 -t 300 -b 0.0.0.0:5000 app:app > /root/suanming/logs/gunicorn.log 2>&1 &

sleep 5

# 4. 检查状态
echo ""
echo "[4/4] 检查服务状态..."
cd /root/suanming
python3 backend_check.py

echo ""
echo "===== 更新完成 ====="
