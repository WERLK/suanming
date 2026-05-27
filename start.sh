#!/bin/bash

# 玄机算命网 - 启动脚本
# 同时启动后端API服务器和前端HTTP服务器

echo "🔮 玄机算命网 - 启动中..."
echo ""

# 检查Python依赖
echo "📦 检查Python依赖..."
pip3 install -q flask flask-cors pyjwt 2>/dev/null

# 创建数据目录
mkdir -p data

# 启动后端API服务器（端口5000）
echo "🚀 启动后端API服务器（端口5000）..."
cd /workspace
nohup python3 api/app.py > logs/api.log 2>&1 &
API_PID=$!
echo "   后端API服务器已启动（PID: $API_PID）"
echo "   API地址: <http://localhost:5000>"

# 等待后端启动
sleep 2

# 启动前端HTTP服务器（端口8080）
echo "🌐 启动前端HTTP服务器（端口8080）..."
cd /workspace
nohup python3 -m http.server 8080 > logs/http.log 2>&1 &
HTTP_PID=$!
echo "   前端HTTP服务器已启动（PID: $HTTP_PID）"
echo "   网站地址: <http://localhost:8080>"

echo ""
echo "✅ 所有服务已启动！"
echo ""
echo "📋 访问地址："
echo "   首页: <http://localhost:8080>"
echo "   登录: <http://localhost:8080/login.html>"
echo "   注册: <http://localhost:8080/register.html>"
echo "   个人中心: <http://localhost:8080/profile.html>"
echo "   忘记密码: <http://localhost:8080/forgot-password.html>"
echo "   重置密码: <http://localhost:8080/reset-password.html?token=xxx>"
echo ""
echo "📊 服务状态："
echo "   后端API: <http://localhost:5000/api/profile>"
echo "   前端页面: <http://localhost:8080/login.html>"
echo ""
echo "📝 日志文件："
echo "   后端API日志: logs/api.log"
echo "   前端HTTP日志: logs/http.log"
echo ""
echo "🛑 停止服务："
echo "   kill $API_PID $HTTP_PID"
echo ""
echo "🎉  enjoy!"
