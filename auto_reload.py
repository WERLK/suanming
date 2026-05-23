#!/usr/bin/env python3
"""
自动热更新脚本 - 监听文件变化并自动触发 Gunicorn 热更新
支持: .py, .html, .css, .js 文件
"""

import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import signal

# 配置
WORKSPACE_DIR = '/workspace'
PID_FILE = '/workspace/logs/gunicorn.pid'
WATCH_EXTENSIONS = ['.py', '.html', '.css', '.js', '.json']
IGNORE_DIRS = ['__pycache__', '.git', 'node_modules', 'logs', 'backups', '.pytest_cache']

class AutoReloadHandler(FileSystemEventHandler):
    """文件变化处理器"""
    
    def __init__(self):
        super().__init__()
        self.last_reload_time = 0
        self.reload_cooldown = 2  # 2秒冷却时间，防止频繁重载
        
    def should_watch(self, path):
        """判断是否需要监听该文件/目录"""
        # 检查文件扩展名
        _, ext = os.path.splitext(path)
        if ext and ext not in WATCH_EXTENSIONS:
            return False
        
        # 检查是否在忽略的目录中
        for ignore_dir in IGNORE_DIRS:
            if f'/{ignore_dir}/' in path or path.endswith(f'/{ignore_dir}'):
                return False
        
        return True
    
    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        if not self.should_watch(file_path):
            return
        
        # 冷却时间检查
        current_time = time.time()
        if current_time - self.last_reload_time < self.reload_cooldown:
            return
        
        print(f"\n📝 检测到文件变化: {file_path}")
        self.reload_server()
        self.last_reload_time = current_time
    
    def on_created(self, event):
        """文件创建事件"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        
        if not self.should_watch(file_path):
            return
        
        print(f"\n➕ 检测到新文件: {file_path}")
        self.reload_server()
        self.last_reload_time = time.time()
    
    def reload_server(self):
        """触发服务器热更新"""
        if not os.path.exists(PID_FILE):
            print("⚠️  Gunicorn 未运行，跳过热更新")
            return
        
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            # 检查进程是否存在
            try:
                os.kill(pid, 0)  # 发送信号 0 检查进程是否存在
            except OSError:
                print(f"❌ 进程不存在 (PID: {pid})")
                return
            
            # 发送 SIGHUP 信号触发热更新
            os.kill(pid, signal.SIGHUP)
            print(f"✅ 热更新信号已发送 (PID: {pid})")
            print(f"⏱️  新代码将在几秒内生效...")
            
        except FileNotFoundError:
            print("⚠️  PID 文件不存在")
        except PermissionError:
            print(f"❌ 没有权限向进程 {pid} 发送信号")
        except Exception as e:
            print(f"❌ 热更新失败: {e}")


def check_gunicorn_running():
    """检查 Gunicorn 是否运行"""
    if not os.path.exists(PID_FILE):
        return False
    
    try:
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)
        return True
    except (FileNotFoundError, OSError):
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 Flask 自动热更新服务")
    print("=" * 60)
    print()
    
    # 检查依赖
    try:
        import watchdog
    except ImportError:
        print("❌ 缺少 watchdog 依赖，正在安装...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'watchdog', '-q'], check=True)
        print("✅ watchdog 安装成功")
    
    # 检查 Gunicorn 是否运行
    if not check_gunicorn_running():
        print("⚠️  Gunicorn 未运行")
        print("💡 请先运行: ./deploy.sh start")
        response = input("\n是否现在启动服务? (y/n): ")
        if response.lower() == 'y':
            subprocess.run(['/workspace/deploy.sh', 'start'])
        else:
            print("❌ 请先启动 Gunicorn 服务")
            sys.exit(1)
    
    # 启动文件监听
    print()
    print(f"👀 开始监听文件变化: {WORKSPACE_DIR}")
    print(f"📁 监听文件类型: {', '.join(WATCH_EXTENSIONS)}")
    print(f"🚫 忽略目录: {', '.join(IGNORE_DIRS)}")
    print()
    print("💡 提示:")
    print("   - 修改文件后会自动触发热更新")
    print("   - 热更新不会中断服务")
    print("   - 按 Ctrl+C 停止监听")
    print("=" * 60)
    print()
    
    # 创建事件处理器和观察者
    event_handler = AutoReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, WORKSPACE_DIR, recursive=True)
    
    # 启动监听
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  停止监听...")
        observer.stop()
    
    observer.join()
    print("✅ 自动热更新服务已停止")


if __name__ == '__main__':
    main()
