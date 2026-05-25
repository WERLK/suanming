#!/usr/bin/env python3
"""
自动更新守护进程
每5分钟检查GitHub仓库是否有新提交，有则自动拉取并重启服务
"""
import time
import subprocess
import os
import hashlib
import logging

# 配置
REPO_DIR = '/root/suanming/suanming'
GUNICORN_CONFIG = os.path.join(REPO_DIR, 'gunicorn_config.py')
CHECK_INTERVAL = 300  # 5分钟
LOG_FILE = '/tmp/auto_update.log'

# 配置日志
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_remote_commit():
    """获取远程仓库最新commit hash"""
    try:
        result = subprocess.run(
            ['git', 'ls-remote', 'origin', 'master'],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout.split()[0]
    except Exception as e:
        logging.error(f'获取远程commit失败: {e}')
    return None

def get_local_commit():
    """获取本地最新commit hash"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        logging.error(f'获取本地commit失败: {e}')
    return None

def update_and_restart():
    """拉取最新代码并重启服务"""
    try:
        # 拉取最新代码
        logging.info('检测到新提交，开始更新...')
        result = subprocess.run(
            ['git', 'fetch', 'origin'],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            logging.error(f'git fetch 失败: {result.stderr}')
            return False
        
        # 强制重置到远程master
        result = subprocess.run(
            ['git', 'reset', '--hard', 'origin/master'],
            cwd=REPO_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            logging.error(f'git reset 失败: {result.stderr}')
            return False
            
        logging.info(f'代码更新成功: {result.stdout.strip()}')
        
        # 重启gunicorn
        logging.info('重启gunicorn服务...')
        subprocess.run(['pkill', '-f', 'gunicorn'], timeout=10)
        time.sleep(3)
        
        # 启动gunicorn
        subprocess.Popen(
            ['python3', '-m', 'gunicorn', '-c', 'gunicorn_config.py', 'api.app:app'],
            cwd=REPO_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        logging.info('服务重启完成')
        return True
        
    except Exception as e:
        logging.error(f'更新失败: {e}')
        return False

def main():
    logging.info('自动更新守护进程启动')
    print(f'自动更新守护进程已启动，每 {CHECK_INTERVAL} 秒检查一次更新')
    print(f'日志文件: {LOG_FILE}')
    
    while True:
        try:
            remote = get_remote_commit()
            local = get_local_commit()
            
            if remote and local:
                if remote != local:
                    logging.info(f'发现新提交: {local[:7]} -> {remote[:7]}')
                    update_and_restart()
                else:
                    logging.debug('已是最新版本')
            else:
                logging.warning('无法获取commit信息')
                
        except Exception as e:
            logging.error(f'检查更新失败: {e}')
        
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()
