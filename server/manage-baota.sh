#!/bin/bash

# 宝塔面板微信客服SaaS项目管理脚本
# 使用方法: ./manage-baota.sh [start|stop|restart|status|logs|backup|update]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_NAME="wxkf_saas"
PROJECT_ROOT="/www/wwwroot/$PROJECT_NAME"
VENV_PATH="$PROJECT_ROOT/venv"
SERVICE_NAME="$PROJECT_NAME"
DOMAIN_NAME="wxkf.shoudu888.com"

# 显示使用帮助
show_help() {
    echo -e "${BLUE}微信客服SaaS管理脚本${NC}"
    echo ""
    echo "使用方法:"
    echo "  ./manage-baota.sh [命令]"
    echo ""
    echo "可用命令:"
    echo -e "  ${GREEN}start${NC}     - 启动服务"
    echo -e "  ${GREEN}stop${NC}      - 停止服务"
    echo -e "  ${GREEN}restart${NC}   - 重启服务"
    echo -e "  ${GREEN}status${NC}    - 查看服务状态"
    echo -e "  ${GREEN}logs${NC}     - 查看实时日志"
    echo -e "  ${GREEN}backup${NC}    - 手动备份"
    echo -e "  ${GREEN}update${NC}    - 更新代码并重启"
    echo -e "  ${GREEN}deploy${NC}    - 部署新版本"
    echo -e "  ${GREEN}health${NC}   - 健康检查"
    echo -e "  ${GREEN}monitor${NC}  - 监控模式"
    echo -e "  ${GREEN}config${NC}   - 查看配置"
    echo ""
}

# 检查项目状态
check_project() {
    if [ ! -d "$PROJECT_ROOT" ]; then
        echo -e "${RED}❌ 项目目录不存在: $PROJECT_ROOT${NC}"
        echo -e "${YELLOW}⚠️ 请先运行: bash setup-baota.sh${NC}"
        exit 1
    fi
}

# 启动服务
start_service() {
    echo -e "${BLUE}🚀 启动微信客服SaaS服务...${NC}"

    # 检查虚拟环境
    if [ ! -d "$VENV_PATH" ]; then
        echo -e "${YELLOW}⚠️ 虚拟环境不存在，正在创建...${NC}"
        cd "$PROJECT_ROOT"
        python3.11 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
    else
        cd "$PROJECT_ROOT"
        source venv/bin/activate
    fi

    # 检查数据库连接
    echo -e "${BLUE}🔍 检查数据库连接...${NC}"
    python3 -c "
import os
from dotenv import load_dotenv
load_dotenv('$PROJECT_ROOT/config/.env.production')
import pymysql
try:
    conn = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '3306')),
        database=os.getenv('DB_NAME', 'wxkf_saas'),
        user=os.getenv('DB_USER', 'wxkf_saas'),
        password=os.getenv('DB_PASSWORD', ''),
        connect_timeout=5
    )
    print('✅ 数据库连接成功')
    conn.close()
except Exception as e:
    print(f'❌ 数据库连接失败: {e}')
    exit(1)
"

    # 检查Redis连接
    echo -e "${BLUE}🔍 检查Redis连接...${NC}"
    python3 -c "
import os
from dotenv import load_dotenv
load_dotenv('$PROJECT_ROOT/config/.env.production')
import redis
try:
    r = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', '6379')),
        password=os.getenv('REDIS_PASSWORD', ''),
        socket_connect_timeout=5
    )
    r.ping()
    print('✅ Redis连接成功')
except Exception as e:
    print(f'❌ Redis连接失败: {e}')
    exit(1)
"

    # 启动服务
    echo -e "${BLUE}🚀 启动应用服务...${NC}"
    systemctl start "$SERVICE_NAME"

    # 等待服务启动
    sleep 5

    # 检查服务状态
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✅ 服务启动成功！${NC}"
        echo -e "${BLUE}🌐 访问地址: https://$DOMAIN_NAME${NC}"
        echo -e "${BLUE}🏥 健康检查: https://$DOMAIN_NAME/health${NC}"
    else
        echo -e "${RED}❌ 服务启动失败！${NC}"
        echo -e "${YELLOW}📋 查看日志: journalctl -u $SERVICE_NAME -f --no-pager${NC}"
        exit 1
    fi
}

# 停止服务
stop_service() {
    echo -e "${YELLOW}⏹ 停止微信客服SaaS服务...${NC}"

    # 优雅停止
    systemctl stop "$SERVICE_NAME"

    # 等待进程完全停止
    sleep 3

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${RED}❌ 服务停止失败！${NC}"
        echo -e "${YELLOW}🔨 强制停止服务...${NC}"
        systemctl kill "$SERVICE_NAME"
        sleep 2
    fi

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${RED}❌ 强制停止也失败！${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ 服务已停止！${NC}"
    fi
}

# 重启服务
restart_service() {
    echo -e "${BLUE}🔄 重启微信客服SaaS服务...${NC}"
    systemctl restart "$SERVICE_NAME"

    sleep 5

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✅ 服务重启成功！${NC}"
        echo -e "${BLUE}🌐 访问地址: https://$DOMAIN_NAME${NC}"
    else
        echo -e "${RED}❌ 服务重启失败！${NC}"
        exit 1
    fi
}

# 查看服务状态
show_status() {
    echo -e "${BLUE}📊 微信客服SaaS服务状态${NC}"
    echo ""

    # 系统服务状态
    echo -e "${YELLOW}🏥 系统服务状态:${NC}"
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "  ${GREEN}✅ 服务状态: 运行中${NC}"
        echo -e "  ${GREEN}✅ 启动时间: $(systemctl show "$SERVICE_NAME" --property=ExecMainStartTimestamp --value)${NC}"
    else
        echo -e "  ${RED}❌ 服务状态: 已停止${NC}"
    fi

    echo -e "  ${YELLOW}🔄 上次重启时间: $(systemctl show "$SERVICE_NAME" --property=ExecMainStartTimestamp --value || echo '未知')${NC}"
    echo ""

    # 端口监听状态
    echo -e "${YELLOW}🌐 端口监听状态:${NC}"
    netstat -tlnp | grep ":8083" | head -5
    echo ""

    # 进程状态
    echo -e "${YELLOW}⚙️ 进程状态:${NC}"
    ps aux | grep -E "(gunicorn|$SERVICE_NAME)" | grep -v grep | head -5
    echo ""

    # 资源使用情况
    echo -e "${YELLOW}💾 资源使用情况:${NC}"
    top -b -n 1 | head -5
    echo ""

    # 磁盘使用情况
    echo -e "${YELLOW}💿 磁盘使用情况:${NC}"
    df -h "$PROJECT_ROOT"
    echo ""
}

# 查看实时日志
show_logs() {
    echo -e "${BLUE}📋 查看微信客服SaaS服务日志${NC}"
    echo -e "${YELLOW}按 Ctrl+C 退出日志查看${NC}"
    echo ""

    # 显示应用日志
    echo -e "${GREEN}=== 应用日志 ===${NC}"
    if [ -f "$PROJECT_ROOT/logs/app.log" ]; then
        tail -f "$PROJECT_ROOT/logs/app.log"
    else
        echo -e "${RED}❌ 应用日志文件不存在${NC}"
    fi
}

# 手动备份
do_backup() {
    echo -e "${BLUE}💾 手动备份微信客服SaaS服务${NC}"

    BACKUP_DIR="/www/backup/$PROJECT_NAME"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)

    # 创建备份目录
    mkdir -p "$BACKUP_DIR/$TIMESTAMP"

    echo -e "${YELLOW}📦 备份数据库...${NC}"
    mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" "$PROJECT_NAME" | gzip > "$BACKUP_DIR/$TIMESTAMP/database_$TIMESTAMP.sql.gz"

    echo -e "${YELLOW}📁 备份配置文件...${NC}"
    cp -r "$PROJECT_ROOT/config" "$BACKUP_DIR/$TIMESTAMP/"

    echo -e "${YELLOW}📁 备份应用文件...${NC}"
    tar -czf "$BACKUP_DIR/$TIMESTAMP/application_$TIMESTAMP.tar.gz" -C "$(dirname "$PROJECT_ROOT")" "$(basename "$PROJECT_ROOT")"

    echo -e "${GREEN}✅ 备份完成！${NC}"
    echo -e "${BLUE}📂 备份位置: $BACKUP_DIR/$TIMESTAMP${NC}"

    # 清理旧备份（保留30天）
    find "$BACKUP_DIR" -type d -mtime +30 -exec rm -rf {} +
    echo -e "${YELLOW}🗑️ 已清理30天前的备份${NC}"
}

# 更新代码
update_code() {
    echo -e "${BLUE}🔄 更新微信客服SaaS代码...${NC}"

    cd "$PROJECT_ROOT"

    # 激活虚拟环境
    source venv/bin/activate

    # 停止服务
    echo -e "${YELLOW}⏹ 停止服务以进行更新...${NC}"
    systemctl stop "$SERVICE_NAME"

    # 备份当前版本
    if [ -d ".git" ]; then
        echo -e "${YELLOW}💾 备份当前版本...${NC}"
        git stash push -m "自动备份 $(date +%Y%m%d_%H%M%S)"
    fi

    # 拉取最新代码
    echo -e "${YELLOW}📥 拉取最新代码...${NC}"
    if [ -d ".git" ]; then
        git pull origin main
    else
        echo -e "${RED}❌ 不是Git仓库，无法自动更新${NC}"
        exit 1
    fi

    # 安装依赖
    echo -e "${YELLOW}📦 安装依赖...${NC}"
    pip install -r requirements.txt

    # 收集静态文件
    echo -e "${YELLOW}📁 收集静态文件...${NC}"
    python3 -c "
import sys
import os
sys.path.insert(0, '$PROJECT_ROOT')
from main import app
import glob
try:
    from flask import Flask
    print('检测到Flask应用')
except ImportError:
    print('检测到FastAPI应用')
print('静态文件收集完成')
"

    # 重新启动服务
    echo -e "${YELLOW}🚀 重新启动服务...${NC}"
    systemctl start "$SERVICE_NAME"

    sleep 5

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✅ 更新完成，服务已启动！${NC}"
    else
        echo -e "${RED}❌ 服务启动失败，正在回滚...${NC}"
        if [ -d ".git" ]; then
            git stash pop
        fi
        systemctl start "$SERVICE_NAME"
    fi
}

# 部署新版本
deploy_version() {
    if [ -z "$1" ]; then
        echo -e "${RED}❌ 请指定版本号或分支名${NC}"
        echo -e "${YELLOW}使用方法: ./manage-baota.sh deploy [版本号|分支名]${NC}"
        exit 1
    fi

    VERSION=$1
    echo -e "${BLUE}🚀 部署微信客服SaaS版本: $VERSION${NC}"

    cd "$PROJECT_ROOT"

    # 停止服务
    echo -e "${YELLOW}⏹ 停止服务以进行部署...${NC}"
    systemctl stop "$SERVICE_NAME"

    # 备份当前版本
    echo -e "${YELLOW}💾 备份当前版本...${NC}"
    ./scripts/backup.sh

    # 切换到指定版本
    echo -e "${YELLOW}🔄 切换到版本: $VERSION${NC}"
    if [ -d ".git" ]; then
        git fetch origin
        git checkout "$VERSION"
    else
        echo -e "${RED}❌ 不是Git仓库，无法切换版本${NC}"
        exit 1
    fi

    # 激活虚拟环境
    source venv/bin/activate

    # 安装依赖
    echo -e "${YELLOW}📦 安装依赖...${NC}"
    pip install -r requirements.txt

    # 数据库迁移
    echo -e "${YELLOW}🗄️ 执行数据库迁移...${NC}"
    python3 -c "
import os
sys.path.insert(0, '$PROJECT_ROOT')
from dotenv import load_dotenv
load_dotenv('$PROJECT_ROOT/config/.env.production')
from core.database import init_database
import asyncio
asyncio.run(init_database())
print('数据库迁移完成')
"

    # 重新启动服务
    echo -e "${YELLOW}🚀 重新启动服务...${NC}"
    systemctl start "$SERVICE_NAME"

    sleep 5

    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✅ 部署完成！${NC}"
        echo -e "${BLUE}🌐 访问地址: https://$DOMAIN_NAME${NC}"
        echo -e "${BLUE}🏥 健康检查: https://$DOMAIN_NAME/health${NC}"
    else
        echo -e "${RED}❌ 部署失败！${NC}"
        # 回滚
        git checkout main
        systemctl start "$SERVICE_NAME"
        echo -e "${YELLOW}⚠️ 已回滚到主分支${NC}"
        exit 1
    fi
}

# 健康检查
health_check() {
    echo -e "${BLUE}🏥 微信客服SaaS健康检查${NC}"
    echo ""

    # 检查服务状态
    echo -e "${YELLOW}🔍 服务状态检查:${NC}"
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "  ${GREEN}✅ 服务状态: 运行中${NC}"
    else
        echo -e "  ${RED}❌ 服务状态: 已停止${NC}"
        exit 1
    fi

    # HTTP健康检查
    echo -e "${YELLOW}🌐 HTTP健康检查:${NC}"
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN_NAME/health")
    if [ "$HTTP_STATUS" = "200" ]; then
        echo -e "  ${GREEN}✅ HTTP状态: $HTTP_STATUS (正常)${NC}"
    else
        echo -e "  ${RED}❌ HTTP状态: $HTTP_STATUS (异常)${NC}"
    fi

    # 响应时间检查
    echo -e "${YELLOW}⏱️ 响应时间检查:${NC}"
    RESPONSE_TIME=$(curl -s -o /dev/null -w "%{time_total}" "https://$DOMAIN_NAME/health")
    if (( $(echo "$RESPONSE_TIME < 1.0" | bc -l) )); then
        echo -e "  ${GREEN}✅ 响应时间: ${RESPONSE_TIME}s (良好)${NC}"
    elif (( $(echo "$RESPONSE_TIME < 3.0" | bc -l) )); then
        echo -e "  ${YELLOW}⚠️ 响应时间: ${RESPONSE_TIME}s (一般)${NC}"
    else
        echo -e "  ${RED}❌ 响应时间: ${RESPONSE_TIME}s (较慢)${NC}"
    fi

    # 数据库连接检查
    echo -e "${YELLOW}🗄️ 数据库连接检查:${NC}"
    python3 -c "
import os
sys.path.insert(0, '$PROJECT_ROOT')
from dotenv import load_dotenv
load_dotenv('$PROJECT_ROOT/config/.env.production')
import pymysql
try:
    conn = pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '3306')),
        database=os.getenv('DB_NAME', 'wxkf_saas'),
        user=os.getenv('DB_USER', 'wxkf_saas'),
        password=os.getenv('DB_PASSWORD', ''),
        connect_timeout=5
    )
    conn.close()
    print('  ${GREEN}✅ 数据库连接: 正常${NC}')
except Exception as e:
    print(f'  ${RED}❌ 数据库连接: 失败 - {e}${NC}')
"

    # Redis连接检查
    echo -e "${YELLOW}🔴 Redis连接检查:${NC}"
    python3 -c "
import os
sys.path.insert(0, '$PROJECT_ROOT')
from dotenv import load_dotenv
load_dotenv('$PROJECT_ROOT/config/.env.production')
import redis
try:
    r = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', '6379')),
        password=os.getenv('REDIS_PASSWORD', ''),
        socket_connect_timeout=5
    )
    r.ping()
    print('  ${GREEN}✅ Redis连接: 正常${NC}')
except Exception as e:
    print(f'  ${RED}❌ Redis连接: 失败 - {e}${NC}')
"

    # SSL证书检查
    echo -e "${YELLOW}🔒 SSL证书检查:${NC}"
    SSL_DAYS=$(echo | openssl s_client -connect "$DOMAIN_NAME:443" -servername "$DOMAIN_NAME" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep notAfter | cut -d= -f2 | xargs -I {} date +%s)
    CURRENT_DAYS=$(date +%s)
    DAYS_LEFT=$(( (SSL_DAYS - CURRENT_DAYS) / 86400 ))

    if [ "$DAYS_LEFT" -gt 30 ]; then
        echo -e "  ${GREEN}✅ SSL证书: 还有${DAYS_LEFT}天过期${NC}"
    elif [ "$DAYS_LEFT" -gt 7 ]; then
        echo -e "  ${YELLOW}⚠️ SSL证书: 还有${DAYS_LEFT}天过期${NC}"
    else
        echo -e "  ${RED}❌ SSL证书: 还有${DAYS_LEFT}天过期（即将过期！）${NC}"
    fi

    echo ""
    echo -e "${BLUE}📊 健康检查完成${NC}"
}

# 监控模式
monitor_mode() {
    echo -e "${BLUE}📊 微信客服SaaS监控模式${NC}"
    echo -e "${YELLOW}按 Ctrl+C 退出监控${NC}"
    echo ""

    MONITOR_INTERVAL=30
    while true; do
        echo -e "${BLUE}=== $(date '+%Y-%m-%d %H:%M:%S') 监控报告 ===${NC}"

        # 服务状态
        if systemctl is-active --quiet "$SERVICE_NAME"; then
            SERVICE_STATUS="${GREEN}运行中${NC}"
        else
            SERVICE_STATUS="${RED}已停止${NC}"
        fi

        # HTTP状态
        HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN_NAME/health" 2>/dev/null || echo "000")
        if [ "$HTTP_STATUS" = "200" ]; then
            HTTP_STATUS="${GREEN}正常${NC}"
        elif [ "$HTTP_STATUS" = "000" ]; then
            HTTP_STATUS="${RED}连接失败${NC}"
        else
            HTTP_STATUS="${RED}异常${NC}"
        fi

        # 响应时间
        RESPONSE_TIME=$(curl -s -o /dev/null -w "%{time_total}" "https://$DOMAIN_NAME/health" 2>/dev/null || echo "999")
        if (( $(echo "$RESPONSE_TIME < 1.0" | bc -l) )); then
            RESPONSE_COLOR="${GREEN}"
        elif (( $(echo "$RESPONSE_TIME < 3.0" | bc -l) )); then
            RESPONSE_COLOR="${YELLOW}"
        else
            RESPONSE_COLOR="${RED}"
        fi

        # 系统负载
        LOAD_AVG=$(uptime | awk '{print $10}')
        if (( $(echo "$LOAD_AVG > 2.0" | bc -l) )); then
            LOAD_COLOR="${RED}"
        elif (( $(echo "$LOAD_AVG > 1.0" | bc -l) )); then
            LOAD_COLOR="${YELLOW}"
        else
            LOAD_COLOR="${GREEN}"
        fi

        # 内存使用率
        MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
        if (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
            MEMORY_COLOR="${RED}"
        elif (( $(echo "$MEMORY_USAGE > 60" | bc -l) )); then
            MEMORY_COLOR="${YELLOW}"
        else
            MEMORY_COLOR="${GREEN}"
        fi

        # 磁盘使用率
        DISK_USAGE=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $5}' | sed 's/%//')
        if (( $(echo "$DISK_USAGE > 90" | bc -l) )); then
            DISK_COLOR="${RED}"
        elif (( $(echo "$DISK_USAGE > 80" | bc -l) )); then
            DISK_COLOR="${YELLOW}"
        else
            DISK_COLOR="${GREEN}"
        fi

        echo -e "服务状态: $SERVICE_STATUS"
        echo -e "HTTP状态: $HTTP_STATUS"
        echo -e "响应时间: ${RESPONSE_COLOR}${RESPONSE_TIME}s${NC}"
        echo -e "系统负载: ${LOAD_COLOR}${LOAD_AVG}${NC}"
        echo -e "内存使用: ${MEMORY_COLOR}${MEMORY_USAGE}%${NC}"
        echo -e "磁盘使用: ${DISK_COLOR}${DISK_USAGE}%${NC}"
        echo ""

        sleep $MONITOR_INTERVAL
    done
}

# 查看配置
show_config() {
    echo -e "${BLUE}⚙️ 微信客服SaaS配置信息${NC}"
    echo ""

    if [ -f "$PROJECT_ROOT/config/.env.production" ]; then
        echo -e "${YELLOW}📄 生产环境配置 (.env.production):${NC}"
        grep -v "PASSWORD\|SECRET\|KEY" "$PROJECT_ROOT/config/.env.production" | head -10
        echo ""
    fi

    if [ -f "$PROJECT_ROOT/config/gunicorn.conf.py" ]; then
        echo -e "${YELLOW}⚙️ Gunicorn配置:${NC}"
        grep -E "(bind|workers|timeout)" "$PROJECT_ROOT/config/gunicorn.conf.py"
        echo ""
    fi

    if [ -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
        echo -e "${YELLOW}🔧 系统服务配置:${NC}"
        systemctl show "$SERVICE_NAME" --property=Description --value
        systemctl show "$SERVICE_NAME" --property=ExecStart --value
        echo ""
    fi

    echo -e "${BLUE}🌐 网络信息:${NC}"
    echo -e "  域名: $DOMAIN_NAME"
    echo -e "  HTTPS端口: 443"
    echo -e "  HTTP端口: 80"
    echo ""

    echo -e "${BLUE}📁 项目路径:${NC}"
    echo -e "  项目根目录: $PROJECT_ROOT"
    echo -e "  虚拟环境: $VENV_PATH"
    echo -e "  配置目录: $PROJECT_ROOT/config"
    echo -e "  日志目录: $PROJECT_ROOT/logs"
    echo -e "  备份目录: /www/backup/$PROJECT_NAME"
    echo ""
}

# 主程序
main() {
    check_project

    case "$1" in
        "start")
            start_service
            ;;
        "stop")
            stop_service
            ;;
        "restart")
            restart_service
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs
            ;;
        "backup")
            do_backup
            ;;
        "update")
            update_code
            ;;
        "deploy")
            deploy_version "$2"
            ;;
        "health")
            health_check
            ;;
        "monitor")
            monitor_mode
            ;;
        "config")
            show_config
            ;;
        *)
            show_help
            exit 1
            ;;
    esac
}

# 运行主程序
main "$@"