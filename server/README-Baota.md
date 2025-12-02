# 微信客服SaaS宝塔面板部署指南

## 🎯 部署概览

本方案专为腾讯云服务器 + 宝塔面板 + TECentOS9环境设计的企业级微信客服SaaS服务自动化部署解决方案。

### 🏗️ 系统架构

```mermaid
graph TB
    A[GitHub仓库] --> B[GitHub Actions]
    B --> C[构建部署包]
    C --> D[SSH推送到宝塔服务器]
    D --> E[自动部署脚本执行]
    E --> F[服务启动和健康检查]
    F --> G[生产环境运行]
```

### 🚀 快速部署步骤

#### 1. 服务器环境准备

**1.1 宝塔面板安装**
```bash
# 安装宝塔面板
yum install -y wget
wget -O install.sh https://download.bt.cn/install/install_6.0.sh
bash install.sh

# 访问宝塔面板
# http://your-server-ip:8888
```

**1.2 必要软件安装**
在宝塔面板中安装：
- ✅ **Python项目管理器** - 管理多个Python项目
- ✅ **MySQL 8.0** - 数据库服务
- ✅ **Redis 7.0** - 缓存服务
- ✅ **Nginx** - Web服务器
- ✅ **Supervisor** - 进程管理（可选）

**1.3 项目目录创建**
```bash
# SSH连接到服务器
cd /www/wwwroot

# 运行初始化脚本
bash setup-baota.sh
```

#### 2. GitHub Secrets配置

在GitHub仓库Settings > Secrets and variables > Actions中添加：

```bash
# 服务器连接信息
BAOTA_HOST=152.136.33.200
BAOTA_PORT=22
BAOTA_USERNAME=root
BAOTA_SSH_KEY="-----BEGIN OPENSSH PRIVATE KEY-----
your-ssh-private-key-content
-----END OPENSSH PRIVATE KEY-----"

# 数据库密码
MYSQL_ROOT_PASSWORD=your_mysql_root_password

# 通知配置
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

#### 3. 自动部署流程

**3.1 推送代码触发部署**
```bash
# 推送到main分支自动部署
git push origin main

# 手动触发部署
# 1. 访问GitHub Actions页面
# 2. 点击"Run workflow"
# 3. 选择环境: staging 或 production
```

**3.2 部署过程自动化**
- ✅ 代码质量检查和测试
- ✅ 构建部署包
- ✅ SSH推送到宝塔服务器
- ✅ 自动执行部署脚本
- ✅ 服务启动和健康检查
- ✅ 部署状态通知

## 📁 项目文件结构

部署完成后的目录结构：
```
/www/wwwroot/wxkf_saas/
├── venv/                    # Python虚拟环境
├── config/                   # 配置文件
│   ├── .env.production      # 生产环境配置
│   ├── .env.staging        # 测试环境配置
│   └── gunicorn.conf.py     # Gunicorn配置
├── scripts/                  # 管理脚本
│   ├── start.sh             # 启动脚本
│   ├── stop.sh              # 停止脚本
│   ├── restart.sh           # 重启脚本
│   ├── health_check.py      # 健康检查
│   ├── backup.sh            # 备份脚本
│   └── monitor.sh           # 监控脚本
├── logs/                     # 日志目录
│   ├── app.log              # 应用日志
│   ├── gunicorn_access.log  # 访问日志
│   ├── gunicorn_error.log   # 错误日志
│   └── backup.log           # 备份日志
├── run/                      # 运行时文件
│   └── gunicorn.pid        # 进程ID文件
└── api/ core/ models/ routes/  # 应用代码
```

## 🎛️ 管理脚本使用

### 快速管理命令

```bash
# 进入项目目录
cd /www/wwwroot/wxkf_saas

# 使用管理脚本
chmod +x manage-baota.sh

# 可用命令
./manage-baota.sh start      # 启动服务
./manage-baota.sh stop       # 停止服务
./manage-baota.sh restart    # 重启服务
./manage-baota.sh status     # 查看状态
./manage-baota.sh logs      # 查看日志
./manage-baota.sh backup    # 手动备份
./manage-baota.sh update     # 更新代码
./manage-baota.sh deploy     # 部署新版本
./manage-baota.sh health    # 健康检查
./manage-baota.sh monitor   # 监控模式
./manage-baota.sh config    # 查看配置
```

### 功能详解

**1. 服务管理**
```bash
# 启动服务（包含依赖检查、数据库连接验证、Redis连接验证）
./manage-baota.sh start

# 停止服务（优雅停止、进程清理）
./manage-baota.sh stop

# 重启服务（停止→更新→启动）
./manage-baota.sh restart
```

**2. 监控和检查**
```bash
# 实时健康检查（HTTP状态、数据库、Redis、SSL证书）
./manage-baota.sh health

# 持续监控模式（30分钟自动检查，系统资源监控）
./manage-baota.sh monitor
```

**3. 部署管理**
```bash
# 手动备份（数据库+配置文件+应用文件）
./manage-baota.sh backup

# 自动更新（拉取最新代码→重启服务）
./manage-baota.sh update

# 部署指定版本（支持Git标签和分支）
./manage-baota.sh deploy v1.0.0
./manage-baota.sh deploy main
```

## 🔧 配置管理

### 环境配置文件

**生产环境配置** (.env.production)
```bash
# 服务器配置
SERVER_URL=https://wxkf.shoudu888.com
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8083

# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=wxkf_saas
DB_USER=wxkf_saas
DB_PASSWORD=your_production_mysql_password

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_production_redis_password
REDIS_KEY_PREFIX=wxkf_saas:

# 微信配置
SUITE_ID=your_suite_id
SUITE_SECRET=your_suite_secret
PROVIDER_SECRET=your_provider_secret
PROVIDER_TOKEN=your_provider_token
PROVIDER_ENCODING_AES_KEY=your_provider_encoding_aes_key
```

**测试环境配置** (.env.staging)
```bash
SERVER_URL=https://staging.wxkf.shoudu888.com
DB_NAME=wxkf_saas_staging
DB_USER=wxkf_saas_staging
DB_PASSWORD=your_staging_mysql_password
REDIS_DB=1
REDIS_KEY_PREFIX=wxkf_saas_staging:
```

### Gunicorn配置

高性能生产服务器配置：
```python
# gunicorn.conf.py
bind = "0.0.0.0:8083"
workers = 4  # CPU核心数 * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 10000
max_requests_jitter = 1000
preload_app = True
timeout = 120
keepalive = 2
backlog = 2048

# 日志配置
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" "%(s)s" "%(b)s" "%(f)s"'
accesslog = "/www/wwwlogs/wxkf_saas/gunicorn_access.log"
errorlog = "/www/wwwlogs/wxkf_saas/gunicorn_error.log"
loglevel = "info"
```

## 🔒 安全配置

### SSL证书配置

**自动Let's Encrypt证书**
```bash
# 宝塔面板中SSL配置
1. 网站 → SSL → Let's Encrypt
2. 域名: wxkf.shoudu888.com
3. 邮箱: admin@wxkf.shoudu888.com
4. 自动续签: 启用

# 验证证书
curl -I https://wxkf.shoudu888.com
```

**Nginx安全配置**
```nginx
# 宝塔面板 → 网站 → 配置文件
server {
    listen 443 ssl http2;
    server_name wxkf.shoudu888.com;

    # SSL配置
    ssl_certificate /etc/letsencrypt/live/wxkf.shoudu888.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/wxkf.shoudu888.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 安全头部
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # 请求限制
    client_max_body_size 50M;
    limit_req_zone $binary_remote_addr zone=limit:10m rate=10r/s;
    limit_req zone=limit burst=100 nodelay;

    # 代理配置
    location / {
        proxy_pass http://127.0.0.1:8083;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时配置
        proxy_connect_timeout 75s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

## 📊 监控和告警

### 系统监控指标

**1. 服务状态监控**
- ✅ 应用进程状态
- ✅ HTTP健康检查
- ✅ 数据库连接状态
- ✅ Redis连接状态
- ✅ SSL证书有效期

**2. 系统资源监控**
- ✅ CPU使用率
- ✅ 内存使用率
- ✅ 磁盘空间使用
- ✅ 网络连接数
- ✅ 系统负载

**3. 应用性能监控**
- ✅ HTTP响应时间
- ✅ 请求数量统计
- ✅ 错误率监控
- ✅ 并发连接数

### 告警机制

**自动告警触发条件**：
- ❌ 服务连续3次健康检查失败
- ❌ 错误率连续30分钟超过5%
- ❌ CPU使用率持续超过80%
- ❌ 内存使用率持续超过85%
- ❌ 磁盘使用率超过90%
- ❌ SSL证书7天内过期

## 🚨 故障排查

### 常见问题解决

**1. 服务启动失败**
```bash
# 查看服务状态
systemctl status wxkf_saas

# 查看详细错误
journalctl -u wxkf_saas -n 50

# 检查配置文件
cat /www/wwwroot/wxkf_saas/config/.env.production

# 手动启动调试
cd /www/wwwroot/wxkf_saas
source venv/bin/activate
python main.py
```

**2. 数据库连接问题**
```bash
# 检查数据库状态
systemctl status mysql

# 测试数据库连接
mysql -u root -p -e "SHOW DATABASES;"

# 查看数据库日志
tail -f /www/server/mysql/mysql-error.log
```

**3. Nginx配置问题**
```bash
# 测试Nginx配置
nginx -t

# 重新加载配置
nginx -s reload

# 查看Nginx日志
tail -f /www/wwwlogs/wxkf_saas/access.log
tail -f /www/wwwlogs/wxkf_saas/error.log
```

## 🔄 备份和恢复

### 自动备份策略

**1. 数据库备份**
```bash
# 每日自动备份
0 2 * * * root /www/wwwroot/wxkf_saas/scripts/backup.sh

# 手动备份
./manage-baota.sh backup
```

**2. 配置文件备份**
```bash
# 每次部署前自动备份
# 备份位置: /www/backup/wxkf_saas/

# 保留30天历史备份
find /www/backup/wxkf_saas -type d -mtime +30 -exec rm -rf {} \;
```

**3. 恢复流程**
```bash
# 从备份恢复
cd /www/backup/wxkf_saas/
tar -xzf application_20241201_120000.tar.gz -C /www/wwwroot/

# 恢复数据库
gunzip < database_20241201_120000.sql.gz | mysql -u root -p wxkf_saas

# 重启服务
systemctl restart wxkf_saas
```

## 📱 访问和测试

### 服务地址

**生产环境**
- 🌐 主服务: https://wxkf.shoudu888.com
- 🔍 健康检查: https://wxkf.shoudu888.com/health
- 📊 API文档: https://wxkf.shoudu888.com/docs
- 📈 监控面板: https://wxkf.shoudu888.com/dashboard

**测试环境**（如配置）
- 🌐 测试服务: https://staging.wxkf.shoudu888.com
- 🔍 健康检查: https://staging.wxkf.shoudu888.com/health

### 功能测试

**1. 基础健康检查**
```bash
curl -X GET https://wxkf.shoudu888.com/health

# 预期响应
{
  "status": "healthy",
  "timestamp": "2024-12-01T12:00:00Z",
  "version": "v1.0.0"
}
```

**2. 微信客服API测试**
```bash
# 测试客服账号API
curl -X POST https://wxkf.shoudu888.com/api/v1/kf/account \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-access-token"
```

## 🎯 最佳实践建议

### 1. 部署安全
- ✅ 使用SSH密钥认证，禁用密码登录
- ✅ 定期更新系统和依赖包
- ✅ 配置防火墙规则
- ✅ 启用Fail2Ban防暴力破解
- ✅ 定期备份数据

### 2. 性能优化
- ✅ 配置Gunicorn多worker进程
- ✅ 启用Redis缓存
- ✅ 配置数据库连接池
- ✅ 启用Nginx gzip压缩
- ✅ 配置CDN加速静态资源

### 3. 监控完善
- ✅ 配置日志轮转防磁盘满
- ✅ 设置系统资源告警阈值
- ✅ 配置服务自动重启机制
- ✅ 定期检查SSL证书有效期

### 4. 运维自动化
- ✅ 定期清理日志和临时文件
- ✅ 自动化依赖更新流程
- ✅ 配置自动灾难恢复方案
- ✅ 建立应急响应流程

## 📞 技术支持

### 联系方式
- 📧 技术支持邮箱: support@wxkf.shoudu888.com
- 📱 紧急联系: +86-138-xxxx-xxxx
- 💬 在线客服: https://wxkf.shoudu888.com/support

### 常用管理命令速查

```bash
# 服务管理
systemctl start wxkf_saas      # 启动
systemctl stop wxkf_saas       # 停止
systemctl restart wxkf_saas    # 重启
systemctl status wxkf_saas     # 状态

# 日志查看
tail -f /www/wwwlogs/wxkf_saas/app.log
journalctl -u wxkf_saas -f

# 脚本管理
./manage-baota.sh start      # 启动
./manage-baota.sh logs       # 日志
./manage-baota.sh health     # 健康
./manage-baota.sh monitor    # 监控
```

---

**文档版本**: v1.0.0
**最后更新**: 2024-12-02
**维护团队**: DevOps团队

🚀 **祝您部署成功！如有问题，请及时联系技术支持。**