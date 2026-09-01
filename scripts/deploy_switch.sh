#!/usr/bin/env bash
# ============================================================================
# 部署切换脚本：旧版（api/app.py 单体）→ 新版（app/ 应用工厂架构）
#
# 用法（在阿里云 ECS 项目根目录）：
#   bash scripts/deploy_switch.sh
#
# 前置条件：
#   1. 新代码已拉取到项目目录（auto_update_daemon 或手动 git pull）
#   2. 已配置环境变量 SECRET_KEY（见 .env.example）
#
# 回滚：本脚本自动备份旧入口，回滚只需恢复备份并重启服务。
# ============================================================================
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo "=== 玄机算命网：新版架构切换 ==="

# 1. 校验密钥（生产必须显式配置，不再有硬编码回退）
if [ -z "${SECRET_KEY:-}" ] && [ ! -f .env ]; then
    echo "[错误] 未检测到 SECRET_KEY 环境变量或 .env 文件。"
    echo "       请先: cp .env.example .env 并填写 SECRET_KEY"
    exit 1
fi

# 2. 备份旧入口（回滚保险）
if [ -f wsgi.py ] && ! grep -q "create_app" wsgi.py 2>/dev/null; then
    cp wsgi.py wsgi.py.legacy.bak
    echo "[备份] 旧 wsgi.py → wsgi.py.legacy.bak"
fi

# 3. 安装依赖（国内镜像加速）
echo "[依赖] 安装 Python 依赖..."
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple -q

# 4. 数据目录自检（新版完全复用旧版 data/ 目录，无需迁移）
echo "[数据] 校验数据文件..."
for f in data/users.json data/tokens.json data/captcha_store.json; do
    if [ -f "$f" ]; then
        echo "  ✓ $f ($(wc -c < "$f") bytes)"
    else
        echo "  - $f 不存在（首次部署属正常，将自动创建）"
    fi
done

# 5. 启动自检（应用工厂能否正常创建）
echo "[自检] 创建应用实例..."
if ! python3 -c "
import sys; sys.path.insert(0, '.')
from app import create_app
app = create_app()
print('  ✓ 应用创建成功，路由数:', len(list(app.url_map.iter_rules())))
"; then
    echo "[错误] 应用自检失败，中止切换（旧服务未受影响）"
    exit 1
fi

# 6. 跑冒烟测试（服务器未装 pytest 时跳过，上方 import 自检已覆盖核心）
echo "[测试] 运行冒烟测试..."
if python3 -m pytest --version >/dev/null 2>&1; then
    python3 -m pytest tests/test_smoke.py -q || {
        echo "[错误] 冒烟测试未通过，中止切换"
        exit 1
    }
else
    echo "  - 服务器未安装 pytest，跳过（可 pip3 install pytest 后重跑）"
fi

# 7. 重启服务（兼容旧入口进程：新入口 HUP 平滑重载 / 旧入口先停再以新入口启动）
PID=$(pgrep -f "gunicorn.*wsgi:application" | head -1 || true)
if [ -n "$PID" ]; then
    echo "[重启] 向新入口 gunicorn 发送 HUP 信号（平滑重载 worker）..."
    kill -HUP "$PID"
    echo "  ✓ 已发送 HUP 到 PID $PID"
else
    OLD_PID=$(pgrep -f "gunicorn.*api.app" | head -1 || true)
    if [ -n "$OLD_PID" ]; then
        echo "[切换] 检测到旧入口进程 (api.app:app, PID $OLD_PID)，停止并以新入口启动..."
        pkill -f "gunicorn.*api.app" || true
        sleep 3
        mkdir -p logs
        nohup gunicorn -c gunicorn_config.py wsgi:application \
            >> logs/gunicorn.log 2>> logs/gunicorn_error.log &
        sleep 5
        NEW_PID=$(pgrep -f "gunicorn.*wsgi:application" | head -1 || true)
        if [ -n "$NEW_PID" ]; then
            echo "  ✓ 新入口 gunicorn 已启动 (PID $NEW_PID)"
            curl -s -o /dev/null -w "  ✓ 健康检查: HTTP %{http_code}\n" \
                --max-time 8 "http://127.0.0.1:${PORT:-5000}/api/health"
        else
            echo "  [错误] 新入口启动失败，请查看 logs/gunicorn_error.log"
            echo "  回滚方法：mv wsgi.py.legacy.bak wsgi.py && 重新启动旧入口"
            exit 1
        fi
    else
        echo "  - 未发现运行中的 gunicorn，直接以新入口启动..."
        mkdir -p logs
        nohup gunicorn -c gunicorn_config.py wsgi:application \
            >> logs/gunicorn.log 2>> logs/gunicorn_error.log &
        sleep 5
        echo "  ✓ 已启动 gunicorn (新入口 wsgi:application)"
    fi
fi

echo ""
echo "=== 切换完成 ==="
echo "回滚方法：mv wsgi.py.legacy.bak wsgi.py && 重启服务"
