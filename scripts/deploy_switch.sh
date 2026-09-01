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

# 6. 跑冒烟测试
echo "[测试] 运行冒烟测试..."
python3 -m pytest tests/test_smoke.py -q || {
    echo "[错误] 冒烟测试未通过，中止切换"
    exit 1
}

# 7. 平滑重启（gunicorn HUP 信号，与新架构的 auto_update 流程一致）
echo "[重启] 向 gunicorn 发送 HUP 信号（平滑重载 worker）..."
PID=$(pgrep -f "gunicorn.*wsgi:application" | head -1 || true)
if [ -n "$PID" ]; then
    kill -HUP "$PID"
    echo "  ✓ 已发送 HUP 到 PID $PID"
else
    echo "  - 未发现运行中的 gunicorn（可能由 systemd 管理，请手动重启服务）"
    echo "    systemctl restart suanming  # 视你的服务名而定"
fi

echo ""
echo "=== 切换完成 ==="
echo "回滚方法：mv wsgi.py.legacy.bak wsgi.py && 重启服务"
