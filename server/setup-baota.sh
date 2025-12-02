#!/bin/bash

# 宝塔面板环境初始化脚本
# 使用方法: bash setup-baota.sh

set -e

echo "🚀 开始配置宝塔面板微信客服SaaS环境..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ 请以root权限运行此脚本${NC}"
    exit 1
fi

# 获取用户输入
echo -e "${BLUE}请输入项目配置信息：${NC}"

read -p "项目目录名称 [wxkf_saas]: " PROJECT_NAME
PROJECT_NAME=${PROJECT_NAME:-wxkf_saas}

read -p "Python版本 [3.11]: " PYTHON_VERSION
PYTHON_VERSION=${PYTHON_VERSION:-3.11}

read -p "域名 [wxkf.shoudu888.com]: " DOMAIN_NAME
DOMAIN_NAME=${DOMAIN_NAME:-wxkf.shoudu888.com}

read -p "服务端口 [8083]: " SERVICE_PORT
SERVICE_PORT=${SERVICE_PORT:-8083}

read -p "数据库端口 [3306]: " DB_PORT
DB_PORT=${DB_PORT:-3306}

read -p "Redis端口 [6379]: " REDIS_PORT
REDIS_PORT=${REDIS_PORT:-6379}

# 设置路径变量
WWW_ROOT="/www/wwwroot"
PROJECT_ROOT="$WWW_ROOT/$PROJECT_NAME"
PROJECT_LOGS="/www/wwwlogs/$PROJECT_NAME"
PROJECT_BACKUP="/www/backup/$PROJECT_NAME"
PROJECT_CONFIG="/www/server/python/$PROJECT_NAME/config"
VENV_PATH="$PROJECT_ROOT/venv"
DEPLOY_PATH="/tmp/deploy_package"

echo -e "${GREEN}📁 项目配置${NC}"
echo "  项目名称: $PROJECT_NAME"
echo "  Python版本: $PYTHON_VERSION"
echo "  域名: $DOMAIN_NAME"
echo "  服务端口: $SERVICE_PORT"
echo "  数据库端口: $DB_PORT"
echo "  Redis端口: $REDIS_PORT"
echo "  项目根目录: $PROJECT_ROOT"

# 创建项目目录结构
echo -e "${BLUE}📂 创建项目目录结构...${NC}"
mkdir -p "$PROJECT_ROOT"
mkdir -p "$PROJECT_LOGS"
mkdir -p "$PROJECT_BACKUP"
mkdir -p "$PROJECT_CONFIG"
mkdir -p "$DEPLOY_PATH"

echo "✅ 目录结构创建完成"

# 安装Python环境
echo -e "${BLUE}🐍 安装Python环境...${NC}"
if ! command -v python$PYTHON_VERSION &> /dev/null; then
    # 安装pyenv用于管理Python版本
    if ! command -v pyenv &> /dev/null; then
        echo "📦 安装pyenv..."
        yum install -y gcc gcc-c++ make zlib-devel bzip2-devel readline-devel sqlite-devel openssl-devel xz xz-devel
        curl https://pyenv.run | bash
    fi

    # 加载pyenv
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"

    # 安装指定Python版本
    echo "📦 安装Python $PYTHON_VERSION..."
    pyenv install $PYTHON_VERSION
    pyenv global $PYTHON_VERSION
    pyenv rehash
else
    echo "✅ Python $PYTHON_VERSION 已安装"
fi

# 创建并激活虚拟环境
echo -e "${BLUE}🔧 创建虚拟环境...${NC}"
if [ ! -d "$VENV_PATH" ]; then
    cd "$PROJECT_ROOT"
    python$PYTHON_VERSION -m venv venv
    echo "✅ 虚拟环境创建完成"
else
    echo "✅ 虚拟环境已存在"
fi

# 激活虚拟环境
source "$VENV_PATH/bin/activate"
echo "✅ 虚拟环境已激活"

# 安装系统依赖
echo -e "${BLUE}📦 安装系统依赖...${NC}"
yum install -y mariadb-devel openssl-devel libffi-devel-devel

# 升级pip并安装基础包
echo -e "${BLUE}📦 安装Python包管理工具...${NC}"
pip install --upgrade pip setuptools wheel

# 创建requirements目录
mkdir -p "$PROJECT_ROOT/requirements"

# 创建应用依赖文件
cat > "$PROJECT_ROOT/requirements/base.txt" << EOF
# FastAPI和依赖
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# 数据库
sqlalchemy==2.0.25
pymysql==1.1.0
aiomysql==0.2.0

# 配置管理
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0

# HTTP客户端
httpx==0.26.0

# Redis
redis==5.0.1

# 工具库
python-dateutil==2.8.2
pycryptodome==3.20.0  # 微信消息加密解密
EOF

# 创建开发环境依赖
cat > "$PROJECT_ROOT/requirements/dev.txt" << EOF
# 开发工具
pytest==8.0.2
pytest-asyncio==0.23.3
pytest-cov==4.1.0
pytest-mock==3.15.1
black==24.4.2
flake8==7.1.0
mypy==1.10.1
EOF

# 创建生产环境依赖
cat > "$PROJECT_ROOT/requirements/prod.txt" << EOF
# 生产服务器
gunicorn==22.0.0
EOF

# 合并依赖文件
cat > "$PROJECT_ROOT/requirements.txt" << EOF
-r base.txt
-r prod.txt
EOF

# 安装应用依赖
echo -e "${BLUE}📦 安装应用依赖...${NC}"
pip install -r "$PROJECT_ROOT/requirements.txt"

# 创建应用配置目录
echo -e "${BLUE}⚙️ 创建应用配置...${NC}"
mkdir -p "$PROJECT_ROOT/config"
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/run"

# 创建生产环境配置文件
cat > "$PROJECT_ROOT/config/.env.production" << EOF
# ==========================================
# 微信客服SaaS服务配置文件 - 生产环境
# ==========================================

# ===== 服务器配置 =====
SERVER_URL=https://$DOMAIN_NAME
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=$SERVICE_PORT

# ===== 数据库配置 =====
DB_HOST=localhost
DB_PORT=$DB_PORT
DB_NAME=$PROJECT_NAME
DB_USER=$PROJECT_NAME
DB_PASSWORD=请设置数据库密码

# ===== Redis配置 =====
REDIS_HOST=localhost
REDIS_PORT=$REDIS_PORT
REDIS_DB=0
REDIS_PASSWORD=请设置Redis密码
REDIS_KEY_PREFIX=wxkf_saas:

# ===== 微信服务商配置 (生产) =====
# 请填入真实的生产环境配置
SUITE_ID=your_suite_id
SUITE_SECRET=your_suite_secret
PROVIDER_SECRET=your_provider_secret
PROVIDER_TOKEN=your_provider_token
PROVIDER_ENCODING_AES_KEY=your_provider_encoding_aes_key

# ===== SaaS服务配置 =====
ENABLE_TENANT_ISOLATION=true
MAX_TENANTS=1000
TOKEN_CACHE_TTL=7000

# ===== 日志配置 =====
LOG_LEVEL=INFO
LOG_FILE=$PROJECT_ROOT/logs/app.log
WXKF_TEST_LOG_TO_FILE=false

# ===== OpenAI配置 (可选) =====
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL_NAME=gpt-3.5-turbo
OPENAI_SYSTEM_PROMPT=
EOF

# 创建测试环境配置文件
cat > "$PROJECT_ROOT/config/.env.staging" << EOF
# ==========================================
# 微信客服SaaS服务配置文件 - 测试环境
# ==========================================

# ===== 服务器配置 =====
SERVER_URL=https://staging.$DOMAIN_NAME
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=$SERVICE_PORT

# ===== 数据库配置 =====
DB_HOST=localhost
DB_PORT=$DB_PORT
DB_NAME=${PROJECT_NAME}_staging
DB_USER=${PROJECT_NAME}_staging
DB_PASSWORD=staging_db_password

# ===== Redis配置 =====
REDIS_HOST=localhost
REDIS_PORT=$REDIS_PORT
REDIS_DB=1
REDIS_PASSWORD=staging_redis_password
REDIS_KEY_PREFIX=wxkf_saas_staging:

# ===== 日志配置 =====
LOG_LEVEL=DEBUG
LOG_FILE=$PROJECT_ROOT/logs/staging.log
WXKF_TEST_LOG_TO_FILE=true
EOF

# 设置权限
echo -e "${BLUE}🔐 设置文件权限...${NC}"
chown -R www:www "$PROJECT_ROOT"
chmod -R 755 "$PROJECT_ROOT"
chmod 600 "$PROJECT_ROOT/config/.env."*

# 创建systemd服务文件
echo -e "${BLUE}⚙️ 创建系统服务...${NC}"
cat > "/etc/systemd/system/$PROJECT_NAME.service" << EOF
[Unit]
Description=微信客服SaaS服务 - $PROJECT_NAME
After=network.target mysql.service redis.service

[Service]
Type=exec
User=www
Group=www
WorkingDirectory=$PROJECT_ROOT
Environment=PATH=$VENV_PATH/bin
ExecStart=$VENV_PATH/bin/gunicorn main:app \
  --bind 0.0.0.0:$SERVICE_PORT \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --preload \
  --timeout 120 \
  --keep-alive 2 \
  --log-level info \
  --access-logfile - \
  --error-logfile - \
  --log-config $PROJECT_ROOT/config/gunicorn.conf.py

# 重启策略
Restart=always
RestartSec=10
StartLimitBurst=3
StartLimitInterval=60

[Install]
WantedBy=multi-user.target
EOF

# 创建gunicorn配置
echo -e "${BLUE}⚙️ 创建Gunicorn配置...${NC}"
cat > "$PROJECT_ROOT/config/gunicorn.conf.py" << EOF
# Gunicorn配置文件
import multiprocessing
import os

# 服务器设置
bind = f"0.0.0.0:{os.getenv('FASTAPI_PORT', '8083')}"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# 超时设置
timeout = 120
keepalive = 2
backlog = 2048

# 日志设置
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" "%(s)s" "%(b)s" "%(f)s"'
accesslog = "-"
errorlog = "-"
loglevel = "info"

# 进程管理
max_requests = 1000
preload_app = True

# 安全设置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
EOF

# 创建健康检查脚本
echo -e "${BLUE}🏥 创建健康检查脚本...${NC}"
cat > "$PROJECT_ROOT/scripts/health_check.py" << EOF
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""健康检查脚本"""

import asyncio
import sys
import aiohttp
import os

async def check_service_health():
    """检查服务健康状态"""
    try:
        service_port = os.getenv('FASTAPI_PORT', '8083')
        health_url = f"http://localhost:{service_port}/health"

        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(health_url) as response:
                if response.status == 200:
                    print("✅ 服务健康检查通过")
                    return True
                else:
                    print(f"❌ 服务健康检查失败: HTTP {response.status}")
                    return False

    except Exception as e:
        print(f"❌ 服务健康检查异常: {e}")
        return False

async def check_database_connection():
    """检查数据库连接"""
    try:
        import pymysql

        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = int(os.getenv('DB_PORT', '3306'))
        db_name = os.getenv('DB_NAME', 'wxkf_saas')
        db_user = os.getenv('DB_USER', 'wxkf_saas')
        db_password = os.getenv('DB_PASSWORD', '')

        connection = pymysql.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
            connect_timeout=5,
            read_timeout=5
        )

        connection.close()
        print("✅ 数据库连接正常")
        return True

    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

async def check_redis_connection():
    """检查Redis连接"""
    try:
        import redis

        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', '6379'))
        redis_password = os.getenv('REDIS_PASSWORD', '')

        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            socket_connect_timeout=5,
            socket_timeout=5
        )

        r.ping()
        print("✅ Redis连接正常")
        return True

    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        return False

async def main():
    """主检查函数"""
    print("🔍 开始系统健康检查...")

    # 检查各项服务
    results = []

    # 服务健康检查
    service_ok = await check_service_health()
    results.append(("服务", service_ok))

    # 数据库连接检查
    db_ok = await check_database_connection()
    results.append(("数据库", db_ok))

    # Redis连接检查
    redis_ok = await check_redis_connection()
    results.append(("Redis", redis_ok))

    # 汇总结果
    print("\n📊 健康检查结果:")
    all_ok = True
    for name, status in results:
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {name}: {'正常' if status else '异常'}")
        if not status:
            all_ok = False

    if all_ok:
        print("\n🎉 所有服务运行正常！")
        sys.exit(0)
    else:
        print("\n⚠️ 部分服务异常，请检查日志")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
EOF

chmod +x "$PROJECT_ROOT/scripts/health_check.py"

# 创建日志轮转配置
echo -e "${BLUE}📝 创建日志轮转配置...${NC}"
cat > "/etc/logrotate.d/$PROJECT_NAME" << EOF
$PROJECT_ROOT/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www www
    postrotate
        systemctl reload $PROJECT_NAME || true
}
EOF

# 创建监控脚本
echo -e "${BLUE}📊 创建监控脚本...${NC}"
cat > "$PROJECT_ROOT/scripts/monitor.sh" << EOF
#!/bin/bash
# 微信客服SaaS监控脚本

PROJECT_NAME="$PROJECT_NAME"
LOG_FILE="$PROJECT_ROOT/logs/app.log"
ALERT_THRESHOLD=5  # 连续失败阈值

check_count=0
alert_sent=false

while true; do
    # 检查服务状态
    if systemctl is-active --quiet $PROJECT_NAME; then
        echo "\$(date '+%Y-%m-%d %H:%M:%S') - ✅ 服务运行正常"

        # 执行健康检查
        if python3 "$PROJECT_ROOT/scripts/health_check.py" >/dev/null 2>&1; then
            check_count=0
            alert_sent=false
            echo "\$(date '+%Y-%m-%d %H:%M:%S') - ✅ 健康检查通过"
        else
            check_count=$((check_count + 1))
            echo "\$(date '+%Y-%m-%d %H:%M:%S') - ❌ 健康检查失败 (\$check_count/\$ALERT_THRESHOLD)"

            if [ \$check_count -ge \$ALERT_THRESHOLD ] && [ "\$alert_sent" = false ]; then
                # 发送告警通知
                echo "\$(date '+%Y-%m-%d %H:%M:%S') - 🚨 服务告警：连续失败\$check_count次"
                alert_sent=true
            fi
        fi
    else
        echo "\$(date '+%Y-%m-%d %H:%M:%S') - ❌ 服务未运行"
        check_count=$((check_count + 1))
    fi

    # 检查日志中的错误
    error_count=\$(tail -n 100 "\$LOG_FILE" | grep -c "ERROR" || echo 0)
    if [ "\$error_count" -gt 10 ]; then
        echo "\$(date '+%Y-%m-%d %H:%M:%S') - ⚠️ 日志错误过多 (最近100行: \$error_count个)"
    fi

    sleep 60  # 每分钟检查一次
done
EOF

chmod +x "$PROJECT_ROOT/scripts/monitor.sh"

# 创建数据库初始化脚本
echo -e "${BLUE}🗄️ 创建数据库初始化脚本...${NC}"
cat > "$PROJECT_ROOT/scripts/init_database.py" << EOF
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数据库初始化脚本"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import init_database

async def main():
    print("🗄️ 开始初始化数据库...")

    try:
        # 加载环境变量
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config/.env.production'))

        await init_database()
        print("✅ 数据库初始化成功")

    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
EOF

chmod +x "$PROJECT_ROOT/scripts/init_database.py"

# 创建备份脚本
echo -e "${BLUE}💾 创建备份脚本...${NC}"
cat > "$PROJECT_ROOT/scripts/backup.sh" << EOF
#!/bin/bash
# 微信客服SaaS备份脚本

PROJECT_NAME="$PROJECT_NAME"
DB_NAME="$PROJECT_NAME"
BACKUP_DIR="$PROJECT_BACKUP"
LOG_FILE="$PROJECT_LOGS/backup.log"

echo "\$(date '+%Y-%m-%d %H:%M:%S') - 💾 开始备份..."

# 创建备份目录
mkdir -p "\$BACKUP_DIR/\$(date +%Y%m%d)"

# 备份数据库
echo "\$(date '+%Y-%m-%d %H:%M:%S') - 📦 备份数据库..."
mysqldump -u root -p "\$MYSQL_ROOT_PASSWORD" "\$DB_NAME" | gzip > "\$BACKUP_DIR/\$(date +%Y%m%d)/database_\$(date +%H%M%S).sql.gz"

# 备份配置文件
echo "\$(date '+%Y-%m-%d %H:%M:%S') - 📄 备份配置文件..."
cp -r "$PROJECT_ROOT/config" "\$BACKUP_DIR/\$(date +%Y%m%d)/"

# 清理旧备份（保留30天）
echo "\$(date '+%Y-%m-%d %H:%M:%S') - 🗑️ 清理旧备份..."
find "\$BACKUP_DIR" -type d -mtime +30 -exec rm -rf {} +

echo "\$(date '+%Y-%m-%d %H:%M:%S') - ✅ 备份完成"
EOF

chmod +x "$PROJECT_ROOT/scripts/backup.sh"

# 配置宝塔面板
echo -e "${BLUE}🛠️ 配置宝塔面板...${NC}"

# 添加到宝塔面板的项目列表（如果宝塔API可用）
if command -v bt &> /dev/null; then
    echo "🛠️ 检测到宝塔面板，尝试自动配置..."

    # 创建宝塔面板网站配置
    cat > "/www/server/panel/vhost/nginx/$PROJECT_NAME.conf" << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN_NAME;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:$SERVICE_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        proxy_send_timeout 300s;
    }

    location /ws {
        proxy_pass http://127.0.0.1:$SERVICE_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }

    access_log /www/wwwlogs/$PROJECT_NAME/access.log;
    error_log /www/wwwlogs/$PROJECT_NAME/error.log;
}
EOF

    # 重载Nginx
    nginx -t && systemctl reload nginx || echo "⚠️ Nginx配置需要手动检查"
fi

# 配置数据库
echo -e "${BLUE}🗄️ 配置数据库...${NC}"

# 创建数据库和用户（如果MySQL已安装）
if command -v mysql &> /dev/null; then
    echo "📦 创建数据库和用户..."

    # 创建数据库
    mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $PROJECT_NAME;" 2>/dev/null || true
    mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS ${PROJECT_NAME}_staging;" 2>/dev/null || true

    # 创建用户
    mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "CREATE USER IF NOT EXISTS '$PROJECT_NAME'@'localhost' IDENTIFIED BY 'your_temp_password';" 2>/dev/null || true
    mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "CREATE USER IF NOT EXISTS '${PROJECT_NAME}_staging'@'localhost' IDENTIFIED BY 'staging_temp_password';" 2>/dev/null || true

    # 授权
    mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "GRANT ALL PRIVILEGES ON $PROJECT_NAME.* TO '$PROJECT_NAME'@'localhost';" 2>/dev/null || true
    mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "GRANT ALL PRIVILEGES ON ${PROJECT_NAME}_staging.* TO '${PROJECT_NAME}_staging'@'localhost';" 2>/dev/null || true

    mysql -u root -p"$MYSQL_ROOT_PASSWORD" -e "FLUSH PRIVILEGES;" 2>/dev/null || true

    echo "✅ 数据库配置完成"
else
    echo "⚠️ MySQL未安装，请通过宝塔面板安装MySQL"
fi

# 配置Redis
echo -e "${BLUE}🔴 配置Redis...${NC}"

if command -v redis-server &> /dev/null; then
    echo "📦 配置Redis..."

    # 创建Redis配置文件
    cat > "/etc/redis/redis-$PROJECT_NAME.conf" << EOF
# Redis配置 - $PROJECT_NAME
bind 127.0.0.1
port $REDIS_PORT
timeout 300
save 900 1
save 300 10
save 60 10000
dbfilename $PROJECT_ROOT/data/dump.rdb
dir $PROJECT_ROOT/data/
logfile $PROJECT_LOGS/redis.log
databases 16
maxclients 10000
maxmemory 256mb
maxmemory-policy allkeys-lru
EOF

    # 创建Redis数据目录
    mkdir -p "$PROJECT_ROOT/data"
    chown -R redis:redis "$PROJECT_ROOT/data"

    # 启动Redis
    redis-server "/etc/redis/redis-$PROJECT_NAME.conf" --daemonize yes
    echo "✅ Redis配置完成"
else
    echo "⚠️ Redis未安装，请通过宝塔面板安装Redis"
fi

# 配置SSL证书（Let's Encrypt）
echo -e "${BLUE}🔒 配置SSL证书...${NC}"

if command -v certbot &> /dev/null; then
    echo "📦 申请SSL证书..."

    # 安装certbot
    yum install -y certbot python3-certbot-nginx

    # 申请证书
    certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --email admin@$DOMAIN_NAME

    echo "✅ SSL证书配置完成"
else
    echo "⚠️ Certbot未安装，请通过宝塔面板配置SSL证书"
fi

# 重新加载systemd服务
echo -e "${BLUE}🔄 重新加载系统服务...${NC}"
systemctl daemon-reload

# 启用并启动服务
echo -e "${BLUE}🚀 启用项目服务...${NC}"
systemctl enable $PROJECT_NAME
echo "✅ 服务已启用，请使用以下命令启动："
echo "  systemctl start $PROJECT_NAME"

# 创建启动/停止脚本
echo -e "${BLUE}📝 创建管理脚本...${NC}"

# 启动脚本
cat > "$PROJECT_ROOT/scripts/start.sh" << EOF
#!/bin/bash
echo "🚀 启动微信客服SaaS服务..."
systemctl start $PROJECT_NAME
systemctl status $PROJECT_NAME
EOF

# 停止脚本
cat > "$PROJECT_ROOT/scripts/stop.sh" << EOF
#!/bin/bash
echo "⏹ 停止微信客服SaaS服务..."
systemctl stop $PROJECT_NAME
systemctl status $PROJECT_NAME
EOF

# 重启脚本
cat > "$PROJECT_ROOT/scripts/restart.sh" << EOF
#!/bin/bash
echo "🔄 重启微信客服SaaS服务..."
systemctl restart $PROJECT_NAME
systemctl status $PROJECT_NAME
EOF

# 日志查看脚本
cat > "$PROJECT_ROOT/scripts/logs.sh" << EOF
#!/bin/bash
echo "📋 查看微信客服SaaS日志..."
tail -f $PROJECT_ROOT/logs/app.log
EOF

# 设置脚本权限
chmod +x "$PROJECT_ROOT/scripts/"*.sh

echo -e "${GREEN}🎉 宝塔面板环境配置完成！${NC}"
echo ""
echo -e "${BLUE}📋 项目信息：${NC}"
echo "  项目名称: $PROJECT_NAME"
echo "  项目路径: $PROJECT_ROOT"
echo "  配置文件: $PROJECT_ROOT/config/.env.production"
echo "  日志目录: $PROJECT_ROOT/logs"
echo "  备份目录: $PROJECT_BACKUP"
echo ""
echo -e "${YELLOW}⚠️ 下一步操作：${NC}"
echo "1. 编辑配置文件: $PROJECT_ROOT/config/.env.production"
echo "2. 设置数据库密码: 请修改配置文件中的密码"
echo "3. 设置微信配置: 填入真实的微信服务商配置"
echo "4. 初始化数据库: $PROJECT_ROOT/scripts/init_database.py"
echo "5. 启动服务: systemctl start $PROJECT_NAME"
echo "6. 查看服务状态: systemctl status $PROJECT_NAME"
echo "7. 查看日志: tail -f $PROJECT_ROOT/logs/app.log"
echo ""
echo -e "${GREEN}🚀 管理命令：${NC}"
echo "  启动: $PROJECT_ROOT/scripts/start.sh"
echo "  停止: $PROJECT_ROOT/scripts/stop.sh"
echo "  重启: $PROJECT_ROOT/scripts/restart.sh"
echo "  日志: $PROJECT_ROOT/scripts/logs.sh"
echo "  健康检查: $PROJECT_ROOT/scripts/health_check.py"
echo "  监控: $PROJECT_ROOT/scripts/monitor.sh"
echo "  备份: $PROJECT_ROOT/scripts/backup.sh"
EOF

chmod +x "D:\project\python\wxkf_saas\server\setup-baota.sh"