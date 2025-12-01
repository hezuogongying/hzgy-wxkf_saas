# wxkf_api 项目总览

## 项目概述

**wxkf_api** 是一个基于微信客服API开发的**多租户SaaS服务平台**，旨在为多个企业提供微信生态的客服消息服务。

本项目完全独立于 `wx_kf`，采用全新的架构设计，专注于**SaaS模式**和**多租户管理**。

## 核心特性

### 1. 多租户架构
- ✅ 支持管理无限个企业客户
- ✅ 每个租户独立的Token管理
- ✅ 数据库级别的租户隔离
- ✅ Redis缓存加速Token访问

### 2. 完整的微信客服API支持
- ✅ **客服账号管理**: 添加、删除、修改、查询客服账号
- ✅ **消息收发**: 支持文本、图片、语音、视频、文件等多种消息类型
- ✅ **消息同步**: 实时同步客户消息和事件
- ✅ **素材管理**: 上传和下载临时素材
- ✅ **客户信息**: 获取客户基础信息

### 3. 企业级功能
- ✅ 自动Token管理和刷新
- ✅ 完整的异常处理机制
- ✅ RESTful API设计
- ✅ 自动生成API文档
- ✅ 支持异步请求

## 技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| **Python** | 3.10+ | 编程语言 |
| **FastAPI** | 0.109+ | Web框架 |
| **SQLAlchemy** | 2.0+ | ORM框架 |
| **Pydantic** | 2.5+ | 数据验证 |
| **MySQL** | 5.7+ | 关系数据库 |
| **Redis** | 6.0+ | 缓存数据库 |
| **Uvicorn** | 0.27+ | ASGI服务器 |

## 项目结构

```
wxkf_api/
│
├── core/                      # 核心模块
│   ├── config.py             # 配置管理 (支持多租户配置)
│   ├── database.py           # 数据库管理 (SQLAlchemy)
│   ├── token_manager.py      # 多租户Token管理器
│   ├── client.py             # 微信API客户端
│   └── exceptions.py         # 异常定义
│
├── models/                    # 数据模型
│   ├── base.py               # 基础模型
│   ├── tenant.py             # 租户模型 (ORM + Pydantic)
│   ├── kf_account.py         # 客服账号模型
│   ├── message.py            # 消息模型
│   └── media.py              # 素材模型
│
├── api/                       # API调用层
│   ├── kf_account.py         # 客服账号API
│   ├── message.py            # 消息API
│   └── media.py              # 素材API
│
├── routes/                    # FastAPI路由
│   └── tenant.py             # 租户管理路由
│
├── main.py                    # 主应用入口
├── .env.example              # 配置文件示例
├── requirements.txt          # 依赖列表
└── README.md                 # 使用文档
```

## 核心模块说明

### 1. 配置管理 (core/config.py)
- 使用Pydantic Settings进行配置管理
- 支持从环境变量或.env文件加载
- 自动验证配置完整性
- 支持多环境配置

### 2. 数据库管理 (core/database.py)
- 使用SQLAlchemy ORM
- 支持连接池管理
- 自动创建表结构
- 提供依赖注入支持

### 3. Token管理器 (core/token_manager.py)
- 支持三种Token类型:
  - `access_token` - 企业访问Token
  - `suite_access_token` - 服务商套件Token
  - `provider_access_token` - 服务商Token
- 自动刷新过期Token
- 支持Redis缓存
- 数据库持久化存储

### 4. API客户端 (core/client.py)
- 统一的HTTP请求封装
- 自动Token注入
- 完整的错误处理
- 支持同步和异步请求

## 数据模型

### 租户表 (tenants)
```sql
CREATE TABLE tenants (
    id INT PRIMARY KEY AUTO_INCREMENT,
    corp_id VARCHAR(64) UNIQUE NOT NULL,
    corp_name VARCHAR(128),
    permanent_code VARCHAR(512),
    is_active BOOLEAN DEFAULT TRUE,
    is_authorized BOOLEAN DEFAULT FALSE,
    callback_url VARCHAR(512),
    contact_name VARCHAR(64),
    contact_phone VARCHAR(32),
    contact_email VARCHAR(128),
    created_at DATETIME,
    updated_at DATETIME
);
```

### Token表 (tenant_tokens)
```sql
CREATE TABLE tenant_tokens (
    id INT PRIMARY KEY AUTO_INCREMENT,
    corp_id VARCHAR(64) NOT NULL,
    token_type VARCHAR(32) NOT NULL,
    token_value VARCHAR(512) NOT NULL,
    expires_at INT NOT NULL,
    created_at DATETIME,
    updated_at DATETIME
);
```

## API接口

### 租户管理
- `POST /api/tenants/` - 创建租户
- `GET /api/tenants/` - 获取租户列表
- `GET /api/tenants/{corp_id}` - 获取租户详情
- `PUT /api/tenants/{corp_id}` - 更新租户
- `DELETE /api/tenants/{corp_id}` - 删除租户

### 系统接口
- `GET /` - 健康检查
- `GET /health` - 详细健康检查
- `GET /docs` - Swagger API文档
- `GET /redoc` - ReDoc API文档

## 使用流程

### 1. 环境准备
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件填写配置
```

### 2. 数据库初始化
```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE wxkf_saas CHARACTER SET utf8mb4;"
```

### 3. 启动服务
```bash
python main.py
```

### 4. 创建租户
```bash
curl -X POST "http://localhost:8083/api/tenants/" \
  -H "Content-Type: application/json" \
  -d '{"corp_id": "wx123", "corp_name": "测试企业"}'
```

### 5. 使用API
```python
from wxkf_api.core.client import WxKfSaasClient
from wxkf_api.api.message import MessageApi

# 创建客户端
client = WxKfSaasClient(config, db)
msg_api = MessageApi(client)

# 发送消息
msg_api.send_text(
    corp_id="wx123",
    touser="customer_id",
    open_kfid="kf_id",
    content="Hello!"
)
```

## 与 wx_kf 的区别

| 特性 | wx_kf | wxkf_api |
|------|-------|----------|
| **定位** | 单租户SDK | 多租户SaaS服务 |
| **架构** | 库/模块 | 完整服务 |
| **租户支持** | 单个企业 | 无限个企业 |
| **Token管理** | 文件缓存 | 数据库+Redis |
| **部署方式** | 集成到应用 | 独立服务 |
| **API接口** | Python接口 | RESTful API |
| **适用场景** | 单企业使用 | SaaS平台 |

## 安全性

### 1. Token安全
- Token存储在数据库中加密
- Redis缓存设置过期时间
- 自动刷新机制避免Token泄露

### 2. 数据隔离
- 每个租户独立的企业ID
- 数据库级别的租户隔离
- API调用强制传入corp_id

### 3. API安全
- 输入验证使用Pydantic
- 完整的异常处理
- HTTPS支持 (生产环境)

## 性能优化

### 1. Token缓存
- Redis缓存避免频繁数据库查询
- Token提前60秒刷新
- 自动失效检测

### 2. 数据库优化
- 使用连接池
- 添加索引 (corp_id, token_type)
- 定期清理过期Token

### 3. 异步支持
- 支持异步HTTP请求
- FastAPI原生异步支持
- 可配置并发数

## 监控与日志

### 日志级别
- `DEBUG` - 详细调试信息
- `INFO` - 正常运行信息
- `WARNING` - 警告信息
- `ERROR` - 错误信息

### 监控指标
- API请求次数
- Token刷新次数
- 数据库连接数
- Redis缓存命中率

## 扩展性

### 水平扩展
- 无状态设计
- 支持负载均衡
- Redis共享缓存
- 数据库读写分离

### 功能扩展
- 插件化设计
- 易于添加新API
- 支持自定义中间件
- 事件系统 (计划中)

## 部署建议

### 开发环境
```bash
python main.py
```

### 生产环境
```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8083
```

### Docker部署
```bash
docker build -t wxkf-saas .
docker run -p 8083:8083 --env-file .env wxkf-saas
```

### Kubernetes部署
- 支持HPA自动扩缩容
- 配置ConfigMap和Secret
- 使用StatefulSet部署数据库

## 未来规划

### 短期 (1-3个月)
- [ ] 实现微信授权回调处理
- [ ] 添加会话分配API
- [ ] 添加智能助手API
- [ ] 完善单元测试
- [ ] 添加监控面板

### 中期 (3-6个月)
- [ ] 实现知识库管理
- [ ] 添加消息队列处理
- [ ] 实现Webhook推送
- [ ] 添加数据统计分析
- [ ] 性能优化

### 长期 (6-12个月)
- [ ] AI客服集成
- [ ] 多渠道客服支持
- [ ] 企业级权限管理
- [ ] 完整的SaaS控制台
- [ ] 商业化功能

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License

---

**开发团队**: wxkf_api Team
**版本**: 1.0.0
**最后更新**: 2025-12-01
