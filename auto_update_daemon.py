#!/usr/bin/env python3
"""
自动更新守护进程 v2 — 适配应用工厂架构（app/ 分层架构）

每 5 分钟检查 GitHub 仓库是否有新提交，有则自动拉取、冒烟自检、平滑重启。

v2 关键变更（相对旧版）：
1. 入口自动检测：新架构 wsgi:application / 旧架构 api.app:app（兼容回滚场景）
2. 修复旧版 bug：不再补建 api/__init__.py（新架构无 api/ 目录，旧逻辑会在
   open('api/__init__.py') 时抛 FileNotFoundError，导致 gunicorn 重启环节被跳过）
3. 零宕机保护：更新前记录 commit，冒烟测试失败自动回滚代码、绝不重启旧进程
4. 自动加载项目根 .env（SECRET_KEY 等环境变量，不覆盖已有环境）
5. 重启后健康检查 /api/health，异常写入 CRITICAL 日志

用法: python3 auto_update_daemon.py &  （或 systemd: auto_update.service）
日志: logs/auto_update.log
"""

import time
import subprocess
import os
import sys
import logging
import json

# 自动检测项目根目录（本脚本所在目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 配置
CHECK_INTERVAL = 300  # 5 分钟（秒）
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'auto_update.log')
GITHUB_API = 'https://api.github.com/repos/WERLK/suanming/commits?per_page=1'
# GitHub Token（可选，设置后可提高 API 限流上限）
# 使用方法：在服务器上执行 echo 'ghp_xxxx' > /root/suanming/.github_token
GITHUB_TOKEN_FILE = os.path.join(BASE_DIR, '.github_token')
LAST_COMMIT_FILE = os.path.join(BASE_DIR, '.last_commit')
ENV_FILE = os.path.join(BASE_DIR, '.env')
GUNICORN_PORT = os.environ.get('PORT', '5000')

# 确保日志目录存在
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def log(msg, level=logging.INFO):
    ts = time.strftime('%H:%M:%S')
    print(f'[{ts}] {msg}')
    logging.log(level, msg)


def load_env_file():
    """加载项目根 .env 文件（不覆盖已有环境变量）"""
    if not os.path.exists(ENV_FILE):
        return
    try:
        with open(ENV_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, _, val = line.partition('=')
                key, val = key.strip(), val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
        log(f'已加载环境变量文件: {ENV_FILE}')
    except Exception as e:
        log(f'加载 .env 失败: {e}', logging.WARNING)


def detect_gunicorn_entry():
    """检测当前代码架构对应的 gunicorn 入口（新架构 / 旧架构兼容）"""
    wsgi = os.path.join(BASE_DIR, 'wsgi.py')
    if os.path.exists(wsgi):
        try:
            with open(wsgi, 'r', encoding='utf-8') as f:
                if 'create_app' in f.read():
                    return 'wsgi:application'
        except Exception:
            pass
    if os.path.exists(os.path.join(BASE_DIR, 'api', 'app.py')):
        return 'api.app:app'
    return None


def get_remote_commit():
    """通过 GitHub API 获取远程最新 commit hash"""
    try:
        curl_cmd = [
            'curl', '-s', '--connect-timeout', '10', '--max-time', '30',
            GITHUB_API
        ]
        if os.path.exists(GITHUB_TOKEN_FILE):
            with open(GITHUB_TOKEN_FILE, 'r') as f:
                token = f.read().strip()
            if token:
                curl_cmd += ['-H', f'Authorization: Bearer {token}']
        curl_cmd += ['-H', 'Accept: application/vnd.github.v3+json']

        result = subprocess.run(
            curl_cmd,
            capture_output=True,
            text=True,
            timeout=35
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            if isinstance(data, list) and len(data) > 0:
                return data[0]['sha']
            elif isinstance(data, dict) and data.get('sha'):
                # 兼容单对象响应
                return data['sha']
            else:
                logging.warning('GitHub API 返回数据格式异常: %s', str(data)[:200])
        else:
            logging.error('curl 请求失败: returncode=%s, stderr=%s',
                          result.returncode, result.stderr[:200])
    except subprocess.TimeoutExpired:
        logging.error('获取远程 commit 超时（curl 执行超时）')
    except json.JSONDecodeError as e:
        logging.error('解析 GitHub API 响应失败: %s', e)
    except Exception as e:
        logging.error('获取远程commit失败: %s', e)
    return None


def get_local_commit():
    """获取本地最新 commit hash"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        logging.error('获取本地commit失败: %s', e)
    return None


def read_last_commit():
    """读取上次记录的 commit"""
    try:
        if os.path.exists(LAST_COMMIT_FILE):
            with open(LAST_COMMIT_FILE, 'r') as f:
                return f.read().strip()
    except Exception:
        pass
    return None


def save_last_commit(commit_sha):
    """保存当前 commit"""
    try:
        with open(LAST_COMMIT_FILE, 'w') as f:
            f.write(commit_sha)
    except Exception as e:
        logging.error('保存commit记录失败: %s', e)


def smoke_test(entry):
    """更新后冒烟测试：能否成功导入应用（失败则不重启，保住旧进程）"""
    if entry == 'wsgi:application':
        code = 'import wsgi'
    else:
        code = 'from api.app import app'
    try:
        result = subprocess.run(
            [sys.executable, '-c', code],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=90,
            env=os.environ.copy()
        )
        if result.returncode == 0:
            return True
        log(f'冒烟测试失败:\n{result.stderr[-800:]}', logging.ERROR)
    except subprocess.TimeoutExpired:
        log('冒烟测试超时', logging.ERROR)
    except Exception as e:
        log(f'冒烟测试异常: {e}', logging.ERROR)
    return False


def rollback_code(prev_commit):
    """回滚代码到更新前的 commit"""
    if not prev_commit:
        log('无更新前 commit 可回滚', logging.CRITICAL)
        return
    try:
        subprocess.run(
            ['git', 'reset', '--hard', prev_commit],
            cwd=BASE_DIR, capture_output=True, text=True, timeout=60
        )
        log(f'已回滚代码到 {prev_commit[:7]}（旧进程未受影响）', logging.CRITICAL)
    except Exception as e:
        log(f'回滚失败: {e}', logging.CRITICAL)


def restart_gunicorn(entry):
    """重启 gunicorn 服务（entry 为自动检测的入口）"""
    log(f'重启 gunicorn（入口: {entry}）...')
    # 先温和停止
    subprocess.run(['pkill', '-f', 'gunicorn_config'], timeout=10, capture_output=True)
    time.sleep(2)
    # 强制清理残留
    subprocess.run(['pkill', '-9', '-f', 'gunicorn'], timeout=5, capture_output=True)
    time.sleep(1)

    log_file = os.path.join(BASE_DIR, 'logs', 'gunicorn.log')
    err_file = os.path.join(BASE_DIR, 'logs', 'gunicorn_error.log')
    os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

    with open(log_file, 'a') as stdout, open(err_file, 'a') as stderr:
        subprocess.Popen(
            [sys.executable, '-m', 'gunicorn', '-c', 'gunicorn_config.py', entry],
            cwd=BASE_DIR,
            start_new_session=True,
            stdout=stdout,
            stderr=stderr
        )

    time.sleep(5)
    log('gunicorn 重启完成')


def health_check():
    """重启后 60 秒内探测 /api/health，确认服务真正起来"""
    url = f'http://127.0.0.1:{GUNICORN_PORT}/api/health'
    for _ in range(12):
        time.sleep(5)
        try:
            r = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
                 '--max-time', '5', url],
                capture_output=True, text=True, timeout=10
            )
            if r.stdout.strip() == '200':
                log('健康检查通过，服务运行正常 ✓')
                return True
        except Exception:
            pass
    log('健康检查失败！请立即查看 logs/gunicorn_error.log 排查', logging.CRITICAL)
    return False


def update_and_restart():
    """拉取最新代码、冒烟自检、重启服务（任一环节失败即回滚并保住旧进程）"""
    prev_commit = get_local_commit()
    try:
        log('检测到新提交，开始更新...')

        # git fetch + reset
        result = subprocess.run(
            ['git', 'fetch', 'origin'],
            cwd=BASE_DIR, capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            logging.error('git fetch 失败: %s', result.stderr[:300])
            return False

        # 清理 untracked 文件（data/ 等 ignored 目录不受影响）
        subprocess.run(
            ['git', 'clean', '-fd'],
            cwd=BASE_DIR, capture_output=True, text=True, timeout=30
        )

        result = subprocess.run(
            ['git', 'reset', '--hard', 'origin/main'],
            cwd=BASE_DIR, capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            logging.error('git reset 失败: %s', result.stderr[:300])
            return False

        log('代码更新成功')

        # 安装/更新依赖
        req_file = os.path.join(BASE_DIR, 'requirements.txt')
        if os.path.exists(req_file):
            log('检测到 requirements.txt，更新依赖...')
            pip_result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-q', '-r', req_file],
                cwd=BASE_DIR, capture_output=True, text=True, timeout=180
            )
            if pip_result.returncode != 0:
                logging.error('pip install 失败: %s', pip_result.stderr[-300:])
            else:
                log('依赖更新完成')

        # v2：检测入口（新架构 wsgi:application / 旧架构 api.app:app）
        entry = detect_gunicorn_entry()
        if not entry:
            log('无法识别应用入口（wsgi.py 与 api/app.py 均不存在），回滚',
                logging.CRITICAL)
            rollback_code(prev_commit)
            return False

        # v2：冒烟测试（导入应用），失败则回滚、绝不重启旧进程
        log(f'冒烟自检（入口: {entry}）...')
        if not smoke_test(entry):
            log('冒烟测试未通过，自动回滚，旧进程继续服务（零宕机保护）',
                logging.CRITICAL)
            rollback_code(prev_commit)
            return False
        log('冒烟自检通过 ✓')

        # 重新加载 .env（代码更新后可能有新增配置）
        load_env_file()

        # 重启服务
        restart_gunicorn(entry)
        health_check()
        return True

    except Exception as e:
        logging.exception('更新失败: %s', e)
        rollback_code(prev_commit)
        return False


def main():
    load_env_file()
    log('自动更新守护进程 v2 启动（适配应用工厂架构）')
    log(f'项目目录: {BASE_DIR}')
    log(f'检查间隔: {CHECK_INTERVAL} 秒')
    log(f'日志文件: {LOG_FILE}')
    entry = detect_gunicorn_entry()
    log(f'当前检测入口: {entry or "未识别"}')
    print(f'自动更新守护进程 v2 已启动，每 {CHECK_INTERVAL // 60} 分钟检查一次更新')
    print(f'查看日志: tail -f {LOG_FILE}')

    # 初始化本地 commit 记录
    local = get_local_commit()
    if local:
        save_last_commit(local)
        log(f'初始 commit: {local[:7]}')

    while True:
        try:
            remote = get_remote_commit()
            last = read_last_commit()

            if remote and last:
                if remote != last:
                    log(f'发现新提交: {last[:7] if last else "???"} -> {remote[:7]}')
                    update_and_restart()
                    # 只有本地确实到位才记录，避免半途失败后不再重试
                    current = get_local_commit()
                    if current == remote:
                        save_last_commit(remote)
                    elif current:
                        save_last_commit(current)
                        log(f'更新未完全到位，记录当前 {current[:7]}，下轮重试',
                            logging.WARNING)
                else:
                    log('已是最新版本')
            elif remote:
                save_last_commit(remote)
                log(f'首次记录 commit: {remote[:7]}')
            else:
                logging.warning('无法获取 commit 信息')

        except Exception as e:
            logging.exception('检查更新失败: %s', e)

        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    main()
