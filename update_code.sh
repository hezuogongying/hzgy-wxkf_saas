#!/bin/bash
# -*- coding: utf-8 -*-
# 生产环境自动更新脚本

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="wxkf_saas"
PROJECT_DIR="/root/site/python"
BACKUP_DIR="${PROJECT_DIR}/backups"
LOG_FILE="${PROJECT_DIR}/update.log"

# 日志函数
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO:${NC} $1" | tee -a "$LOG_FILE"
}

# 检查是否在正确的目录
check_directory() {
    if [ ! -d ".git" ]; then
        error "当前目录不是Git仓库"
        exit 1
    fi

    if [ ! -f "main.py" ]; then
        error "未找到main.py文件，可能不在项目根目录"
        exit 1
    fi

    log "当前目录: $(pwd)"
}

# 创建备份目录
create_backup() {
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        log "创建备份目录: $BACKUP_DIR"
    fi
}

# 备份当前代码
backup_code() {
    local backup_name="${PROJECT_NAME}_backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    local backup_path="${BACKUP_DIR}/${backup_name}"

    log "开始备份当前代码..."
    tar -czf "$backup_path" --exclude='.git' --exclude='__pycache__' --exclude='venv' --exclude='*.pyc' --exclude='.env' . 2>/dev/null

    if [ $? -eq 0 ]; then
        log "备份成功: $backup_path"
        echo "$backup_path" > "${PROJECT_DIR}/last_backup.txt"
    else
        error "备份失败"
        exit 1
    fi
}

# 获取当前版本
get_current_version() {
    local current_version=$(git rev-parse HEAD)
    echo "$current_version"
}

# 获取最新版本
get_latest_version() {
    # 获取远程最新版本
    git fetch origin 2>/dev/null || {
        error "无法获取远程更新"
        exit 1
    }

    local latest_version=$(git rev-parse origin/bwx_dev)
    echo "$latest_version"
}

# 检查是否有更新
check_updates() {
    log "检查代码更新..."

    local current_version=$(get_current_version)
    local latest_version=$(get_latest_version)

    info "当前版本: ${current_version:0:8}"
    info "最新版本: ${latest_version:0:8}"

    if [ "$current_version" = "$latest_version" ]; then
        log "代码已是最新版本"
        return 1
    else
        log "发现新版本"
        return 0
    fi
}

# 拉取更新
pull_updates() {
    log "开始拉取最新代码..."

    # 拉取最新代码
    git pull origin bwx_dev 2>&1 | tee -a "$LOG_FILE"

    if [ $? -eq 0 ]; then
        log "代码拉取成功"
        return 0
    else
        error "代码拉取失败"
        return 1
    fi
}

# 安装依赖
install_dependencies() {
    log "检查并安装依赖..."

    # 激活虚拟环境
    if [ -d "venv" ]; then
        source venv/bin/activate
        log "激活虚拟环境"
    else
        error "未找到虚拟环境目录: venv"
        exit 1
    fi

    # 安装或更新依赖
    log "安装Python依赖..."
    pip install -r requirements.txt 2>&1 | tee -a "$LOG_FILE"

    if [ $? -eq 0 ]; then
        log "依赖安装成功"
    else
        error "依赖安装失败"
        exit 1
    fi
}

# 数据库迁移
migrate_database() {
    log "执行数据库迁移..."

    # 检查是否有迁移脚本
    if [ -f "migrate.py" ]; then
        python migrate.py 2>&1 | tee -a "$LOG_FILE"
    else
        log "未找到迁移脚本，跳过数据库迁移"
    fi
}

# 重启服务
restart_service() {
    log "重启服务..."

    # 查找并停止Python进程
    local python_pids=$(pgrep -f "python.*main.py" 2>/dev/null || true)

    if [ -n "$python_pids" ]; then
        log "停止当前服务进程: $python_pids"
        echo "$python_pids" | xargs kill -TERM 2>/dev/null || true
        sleep 3

        # 如果进程仍在运行，强制停止
        python_pids=$(pgrep -f "python.*main.py" 2>/dev/null || true)
        if [ -n "$python_pids" ]; then
            log "强制停止服务进程"
            echo "$python_pids" | xargs kill -9 2>/dev/null || true
        fi
    fi

    # 启动服务
    log "启动服务..."
    nohup python main.py > app.log 2>&1 &
    local new_pid=$!

    # 等待服务启动
    sleep 5

    # 检查服务是否运行
    if kill -0 "$new_pid" 2>/dev/null; then
        log "服务启动成功，PID: $new_pid"
        echo "$new_pid" > "${PROJECT_DIR}/app.pid"
    else
        error "服务启动失败"
        tail -n 20 app.log | tee -a "$LOG_FILE"
        exit 1
    fi
}

# 健康检查
health_check() {
    log "执行健康检查..."

    # 等待服务完全启动
    sleep 10

    # 检查健康接口
    if command -v curl >/dev/null 2>&1; then
        local health_response=$(curl -s "http://localhost:58083/health" 2>/dev/null || echo "")

        if [[ "$health_response" == *"ok"* ]]; then
            log "健康检查通过"
            return 0
        else
            error "健康检查失败"
            return 1
        fi
    else
        warning "curl命令不可用，跳过健康检查"
        return 0
    fi
}

# 清理旧备份
cleanup_old_backups() {
    log "清理30天前的备份文件..."

    find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete 2>/dev/null || true
    log "旧备份清理完成"
}

# 发送通知（可选）
send_notification() {
    local status=$1
    local latest_version=$(get_latest_version)
    local current_version=$(git rev-parse HEAD)

    # 这里可以添加发送邮件、微信、钉钉等通知的逻辑
    if command -v sendmail >/dev/null 2>&1; then
        echo "$status" | sendmail -s "项目更新通知" admin@example.com 2>/dev/null || true
    fi

    # 记录到系统日志
    logger "$PROJECT_NAME update: $status, version: ${current_version:0:8}"
}

# 主函数
main() {
    log "===================="
    log "开始执行项目更新"
    log "===================="

    # 检查环境
    check_directory

    # 创建备份
    create_backup
    backup_code

    # 检查更新
    if ! check_updates; then
        log "无需更新，退出"
        exit 0
    fi

    # 获取版本信息
    local old_version=$(get_current_version)

    # 执行更新
    log "===================="
    log "执行更新操作"
    log "===================="

    if ! pull_updates; then
        # 恢复备份
        error "更新失败，准备恢复备份"
        restore_backup
        exit 1
    fi

    # 安装依赖
    install_dependencies

    # 数据库迁移
    migrate_database

    # 重启服务
    restart_service

    # 健康检查
    if health_check; then
        local new_version=$(get_latest_version)
        log "===================="
        log "更新完成！"
        log "旧版本: ${old_version:0:8}"
        log "新版本: ${new_version:0:8}"
        log "===================="

        # 清理旧备份
        cleanup_old_backups

        # 发送通知
        send_notification "SUCCESS"
    else
        error "健康检查失败，可能需要手动干预"
        send_notification "FAILED"
        exit 1
    fi
}

# 恢复备份
restore_backup() {
    local last_backup_file="${PROJECT_DIR}/last_backup.txt"

    if [ -f "$last_backup_file" ]; then
        local backup_path=$(cat "$last_backup_file")
        if [ -f "$backup_path" ]; then
            log "恢复备份: $backup_path"

            # 删除当前文件（保留.git）
            find . -mindepth 1 ! -path './.git*' ! -path './venv*' -delete 2>/dev/null || true

            # 解压备份
            tar -xzf "$backup_path" 2>/dev/null || {
                error "备份恢复失败"
                exit 1
            }

            log "备份恢复成功"
        fi
    fi
}

# 回滚到指定版本
rollback() {
    local target_version=$1

    log "开始回滚到版本: $target_version"

    # 创建当前版本的备份
    backup_code

    # 回滚到指定版本
    git reset --hard "$target_version" 2>&1 | tee -a "$LOG_FILE"

    if [ $? -eq 0 ]; then
        # 重启服务
        restart_service
        health_check

        if [ $? -eq 0 ]; then
            log "回滚成功到版本: ${target_version:0:8}"
        else
            error "回滚后服务启动失败"
        fi
    else
        error "回滚失败"
        exit 1
    fi
}

# 查看版本历史
show_versions() {
    log "最近10次提交历史："
    git log --oneline -10 --decorate --graph
}

# 使用说明
show_usage() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help     显示帮助信息"
    echo "  -v, --version  显示版本信息"
    echo "  --rollback [commit_hash]  回滚到指定版本"
    echo "  --history     查看版本历史"
    echo ""
    echo "示例:"
    echo "  $0                    # 正常更新"
    echo "  $0 --rollback abc123   # 回滚到abc123版本"
    echo "  $0 --history          # 查看历史版本"
}

# 显示版本信息
show_version() {
    echo "$PROJECT_NAME 更新脚本 v1.0.0"
    echo "最后更新时间: $(date '+%Y-%m-%d')"
}

# 解析命令行参数
case "$1" in
    -h|--help)
        show_usage
        exit 0
        ;;
    -v|--version)
        show_version
        exit 0
        ;;
    --rollback)
        if [ -z "$2" ]; then
            error "请指定要回滚的版本号"
            show_usage
            exit 1
        fi
        rollback "$2"
        exit 0
        ;;
    --history)
        show_versions
        exit 0
        ;;
    *)
        main
        ;;
esac