#!/bin/bash

# 部署脚本 - 支持热更新
# 使用方法: ./deploy.sh [start|stop|restart|reload|status]

APP_NAME="Flask登录注册系统"
APP_DIR="/workspace"
PID_FILE="/workspace/logs/gunicorn.pid"
CONFIG_FILE="/workspace/gunicorn_config.py"
LOG_DIR="/workspace/logs"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印信息
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查 Python 依赖..."
    cd $APP_DIR
    pip3 install -r requirements.txt -q
    if [ $? -eq 0 ]; then
        log_info "依赖安装成功"
    else
        log_error "依赖安装失败"
        exit 1
    fi
}

# 启动服务
start_server() {
    log_info "启动 $APP_NAME..."
    
    # 检查是否已经在运行
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null 2>&1; then
            log_warn "服务已经在运行 (PID: $PID)"
            return 1
        else
            log_warn "PID 文件存在但进程不存在，清理..."
            rm -f $PID_FILE
        fi
    fi
    
    # 检查日志目录
    if [ ! -d $LOG_DIR ]; then
        mkdir -p $LOG_DIR
    fi
    
    # 启动 Gunicorn
    cd $APP_DIR
    gunicorn -c $CONFIG_FILE api.app:app --daemon --pid $PID_FILE
    
    sleep 2
    
    # 检查是否启动成功
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null 2>&1; then
            log_info "服务启动成功! (PID: $PID)"
            log_info "访问地址: <ADDRESS_REDACTED>
            return 0
        fi
    fi
    
    log_error "服务启动失败，请检查日志: $LOG_DIR/error.log"
    return 1
}

# 停止服务
stop_server() {
    log_info "停止 $APP_NAME..."
    
    if [ ! -f $PID_FILE ]; then
        log_warn "PID 文件不存在，服务可能未运行"
        return 1
    fi
    
    PID=$(cat $PID_FILE)
    
    if ps -p $PID > /dev/null 2>&1; then
        # 优雅停止
        kill -TERM $PID
        log_info "发送停止信号到进程 $PID"
        
        # 等待进程停止
        for i in {1..10}; do
            if ! ps -p $PID > /dev/null 2>&1; then
                log_info "服务已停止"
                rm -f $PID_FILE
                return 0
            fi
            sleep 1
        done
        
        # 强制停止
        log_warn "进程未响应，强制停止..."
        kill -9 $PID
        rm -f $PID_FILE
        log_info "服务已强制停止"
        return 0
    else
        log_warn "进程不存在，清理 PID 文件"
        rm -f $PID_FILE
        return 1
    fi
}

# 热更新（不中断服务）
reload_server() {
    log_info "热更新 $APP_NAME..."
    
    if [ ! -f $PID_FILE ]; then
        log_error "服务未运行，请先启动服务"
        return 1
    fi
    
    PID=$(cat $PID_FILE)
    
    if ! ps -p $PID > /dev/null 2>&1; then
        log_error "PID 文件存在但进程不存在，请重启服务"
        rm -f $PID_FILE
        return 1
    fi
    
    # 发送 SIGHUP 信号触发优雅重载
    kill -HUP $PID
    
    if [ $? -eq 0 ]; then
        log_info "热更新信号已发送 (PID: $PID)"
        log_info "Gunicorn 将启动新的工作进程并优雅关闭旧进程"
        log_info "服务不会中断，用户可以继续访问"
        return 0
    else
        log_error "热更新失败"
        return 1
    fi
}

# 重启服务（会短暂中断）
restart_server() {
    log_info "重启 $APP_NAME..."
    stop_server
    sleep 2
    start_server
}

# 查看状态
status_server() {
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null 2>&1; then
            log_info "服务状态: ${GREEN}运行中${NC} (PID: $PID)"
            
            # 显示进程信息
            echo ""
            log_info "进程信息:"
            ps -fp $PID
            
            # 显示端口监听
            echo ""
            log_info "端口监听:"
            netstat -tlnp 2>/dev/null | grep :5000 || ss -tlnp 2>/dev/null | grep :5000
            
            # 显示工作进程
            echo ""
            log_info "工作进程:"
            pstree -p $PID 2>/dev/null || ps --ppid $PID -o pid,cmd
            
            return 0
        else
            log_warn "PID 文件存在但进程不存在"
            rm -f $PID_FILE
        fi
    fi
    
    log_info "服务状态: ${RED}未运行${NC}"
    return 1
}

# 查看日志
view_logs() {
    echo ""
    log_info "最近的错误日志 (最后 20 行):"
    echo "----------------------------------------"
    tail -n 20 $LOG_DIR/error.log 2>/dev/null || log_warn "错误日志文件不存在"
    
    echo ""
    log_info "最近的访问日志 (最后 20 行):"
    echo "----------------------------------------"
    tail -n 20 $LOG_DIR/access.log 2>/dev/null || log_warn "访问日志文件不存在"
}

# 主函数
main() {
    case "$1" in
        start)
            check_dependencies
            start_server
            ;;
        stop)
            stop_server
            ;;
        restart)
            check_dependencies
            restart_server
            ;;
        reload)
            check_dependencies
            reload_server
            ;;
        status)
            status_server
            ;;
        logs)
            view_logs
            ;;
        *)
            echo "使用方法: $0 {start|stop|restart|reload|status|logs}"
            echo ""
            echo "命令说明:"
            echo "  start   - 启动服务"
            echo "  stop    - 停止服务"
            echo "  restart - 重启服务（会短暂中断）"
            echo "  reload  - 热更新（不中断服务）"
            echo "  status  - 查看服务状态"
            echo "  logs    - 查看日志"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
