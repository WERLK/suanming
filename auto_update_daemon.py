#!/usr/bin/env python3
"""
自动更新守护进程
每5分钟检查GitHub仓库是否有新提交，有则自动拉取并重启服务
用法: python3 auto_update_daemon.py &
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
CHECK_INTERVAL = 300  # 5分钟（秒）
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'auto_update.log')
GITHUB_API = 'https://api.github.com/repos/WERLK/suanming/commits?per_page=1'
LAST_COMMIT_FILE = os.path.join(BASE_DIR, '.last_commit')

# 确保日志目录存在
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# 配置日志
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def log(msg):
    ts = time.strftime('%H:%M:%S')
    print(f'[{ts}] {msg}')
    logging.info(msg)


def get_remote_commit():
    """通过 GitHub API 获取远程最新 commit hash"""
    try:
        result = subprocess.run(
            ['curl', '-s', GITHUB_API],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if isinstance(data, list) and len(data) > 0:
                return data[0]['sha']
    except Exception as e:
        logging.error(f'获取远程commit失败: {e}')
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
        logging.error(f'获取本地commit失败: {e}')
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
        logging.error(f'保存commit记录失败: {e}')


def restart_gunicorn():
    """重启 gunicorn 服务"""
    log('重启 gunicorn 服务...')
    # 先温和停止
    subprocess.run(['pkill', '-f', 'gunicorn_config'], timeout=10, capture_output=True)
    time.sleep(2)
    # 强制清理残留
    subprocess.run(['pkill', '-9', '-f', 'gunicorn'], timeout=5, capture_output=True)
    time.sleep(1)

    # 启动 gunicorn
    log_file = os.path.join(BASE_DIR, 'logs', 'gunicorn.log')
    err_file = os.path.join(BASE_DIR, 'logs', 'gunicorn_error.log')
    os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

    with open(log_file, 'a') as stdout, open(err_file, 'a') as stderr:
        subprocess.Popen(
            [sys.executable, '-m', 'gunicorn', '-c', 'gunicorn_config.py', 'api.app:app'],
            cwd=BASE_DIR,
            start_new_session=True,
            stdout=stdout,
            stderr=stderr
        )

    time.sleep(5)
    log('gunicorn 重启完成')


def update_and_restart():
    """拉取最新代码并重启服务"""
    try:
        log('检测到新提交，开始更新...')

        # git fetch + reset
        result = subprocess.run(
            ['git', 'fetch', 'origin'],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            logging.error(f'git fetch 失败: {result.stderr}')
            return False

        result = subprocess.run(
            ['git', 'reset', '--hard', 'origin/main'],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            logging.error(f'git reset 失败: {result.stderr}')
            return False

        log('代码更新成功')

        # 确保 api/__init__.py 存在
        init_file = os.path.join(BASE_DIR, 'api', '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# api package init\n')
            log('创建 api/__init__.py')

        # 重启服务
        restart_gunicorn()
        return True

    except Exception as e:
        logging.error(f'更新失败: {e}')
        return False


def main():
    log('自动更新守护进程启动')
    log(f'项目目录: {BASE_DIR}')
    log(f'检查间隔: {CHECK_INTERVAL} 秒')
    log(f'日志文件: {LOG_FILE}')
    print(f'自动更新守护进程已启动，每 {CHECK_INTERVAL // 60} 分钟检查一次更新')
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
                    save_last_commit(remote)
                else:
                    log('已是最新版本')
            elif remote:
                # 还没有记录，保存当前 remote
                save_last_commit(remote)
                log(f'首次记录 commit: {remote[:7]}')
            else:
                logging.warning('无法获取 commit 信息')

        except Exception as e:
            logging.error(f'检查更新失败: {e}')

        time.sleep(CHECK_INTERVAL)


if __name__ == '__main__':
    main()
