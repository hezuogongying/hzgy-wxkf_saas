# 🚀 微信客服SaaS宝塔面板快速部署

## 📋 部署清单

### 前置条件
- [ ] 腾讯云服务器已购买
- [ ] TECentOS9系统已安装
- [ ] 宝塔面板已安装
- [ ] 域名已解析到服务器IP
- [ ] GitHub仓库已创建
- [ ] SSH密钥已配置

## ⚡ 一键部署脚本

### 步骤1: 服务器环境准备
```bash
# SSH连接到服务器
ssh root@152.136.33.200

# 下载并运行初始化脚本
curl -fsSL https://raw.githubusercontent.com/hezuogongying/hzgy-wxkf_saas/main/server/setup-baota.sh -o setup-baota.sh
chmod +x setup-baota.sh
./setup-baota.sh

# 脚本会自动完成：
# ✅ 创建项目目录结构
# ✅ 安装Python环境和依赖
# ✅ 配置数据库和Redis
# ✅ 设置SSL证书
# ✅ 创建系统服务
# ✅ 配置Nginx
# ✅ 安装监控脚本
```

### 步骤2: 配置生产环境
```bash
# 编辑配置文件
vim /www/wwwroot/wxkf_saas/config/.env.production

# 必填配置项：
DB_PASSWORD=your_actual_mysql_password
REDIS_PASSWORD=your_actual_redis_password
SUITE_ID=your_actual_suite_id
SUITE_SECRET=your_actual_suite_secret
PROVIDER_SECRET=your_actual_provider_secret
PROVIDER_TOKEN=your_actual_provider_token
PROVIDER_ENCODING_AES_KEY=your_actual_provider_aes_key
```

### 步骤3: 初始化数据库
```bash
# 运行数据库初始化
cd /www/wwwroot/wxkf_saas
source venv/bin/activate
python scripts/init_database.py
```

### 步骤4: 启动服务
```bash
# 使用管理脚本启动
chmod +x manage-baota.sh
./manage-baota.sh start

# 检查服务状态
./manage-baota.sh status

# 查看实时日志
./manage-baota.sh logs
```

## 🔄 GitHub自动部署

### 步骤1: 配置GitHub Secrets
在GitHub仓库设置中添加以下Secrets：

```bash
BAOTA_HOST=152.136.33.200
BAOTA_PORT=22
BAOTA_USERNAME=root
BAOTA_SSH_KEY="你的SSH私钥"
MYSQL_ROOT_PASSWORD="你的MySQL root密码"
SLACK_WEBHOOK_URL="你的Slack Webhook URL（可选）"
```

### 步骤2: 触发自动部署
```bash
# 推送代码到main分支
git add .
git commit -m "feat: 微信客服SaaS服务部署"
git push origin main

# GitHub Actions会自动执行：
# ✅ 代码质量检查
# ✅ 构建部署包
# ✅ SSH推送到服务器
# ✅ 自动执行部署
# ✅ 健康检查验证
# ✅ 发送部署通知
```

## 🔍 部署验证

### 功能检查
```bash
# 1. 健康检查
curl -f https://wxkf.shoudu888.com/health

# 2. API文档访问
curl -f https://wxkf.shoudu888.com/docs

# 3. 服务状态检查
systemctl status wxkf_saas

# 4. 进程检查
ps aux | grep gunicorn

# 5. 端口监听检查
netstat -tlnp | grep :8083
```

### 配置验证
```bash
# 1. 数据库连接测试
mysql -u root -p -e "SHOW DATABASES;"

# 2. Redis连接测试
redis-cli ping

# 3. SSL证书检查
curl -I https://wxkf.shoudu888.com

# 4. Nginx配置检查
nginx -t
```

## 🎯 服务地址

### 生产环境
- **应用地址**: https://wxkf.shoudu888.com
- **API文档**: https://wxkf.shoudu888.com/docs
- **健康检查**: https://wxkf.shoudu888.com/health

### 宝塔面板
- **面板地址**: http://152.136.33.200:8888
- **项目管理**: 软件商店 → Python项目管理

### 系统服务
```bash
# 服务管理命令
systemctl start wxkf_saas    # 启动
systemctl stop wxkf_saas     # 停止
systemctl restart wxkf_saas  # 重启
systemctl status wxkf_saas   # 状态

# 快速管理脚本
./manage-baota.sh start|stop|restart|status|logs|backup|update|deploy|health|monitor
```

## 📞 常见问题

### Q1: 服务启动失败
```bash
# 检查日志
journalctl -u wxkf_saas -n 20

# 检查端口占用
netstat -tlnp | grep :8083

# 手动启动调试
cd /www/wwwroot/wxkf_saas
source venv/bin/activate
python main.py
```

### Q2: 数据库连接失败
```bash
# 检查MySQL状态
systemctl status mysql

# 检查配置文件
cat /www/wwwroot/wxkf_saas/config/.env.production | grep DB_

# 测试连接
mysql -u wxkf_saas -p -h localhost wxkf_saas
```

### Q3: Nginx 502错误
```bash
# 检查Gunicorn进程
ps aux | grep gunicorn

# 检查端口监听
netstat -tlnp | grep :8083

# 测试后端直接访问
curl http://127.0.0.1:8083/health

# 重新加载Nginx
nginx -s reload
```

### Q4: SSL证书问题
```bash
# 检查证书状态
certbot certificates

# 手动申请证书
certbot --nginx -d wxkf.shoudu888.com

# 强制续签
certbot renew --force-renewal
```

## 🎉 部署成功！

完成以上步骤后，你的微信客服SaaS服务将运行在：
- **🌐 生产环境**: https://wxkf.shoudu888.com
- **📊 监控面板**: 宝塔面板实时监控
- **🔄 自动更新**: GitHub推送自动部署
- **🛡️ 安全防护**: SSL证书 + 防火墙
- **📈 性能优化**: Gunicorn + Redis + Nginx

## 📞 技术支持

如果遇到问题，请：
1. 查看详细文档: `server/README-Baota.md`
2. 运行诊断脚本: `./manage-baota.sh health`
3. 查看系统日志: `./manage-baota.sh logs`
4. 联系技术支持: support@wxkf.shoudu888.com

---
**🎯 恭喜！微信客服SaaS服务部署成功！**