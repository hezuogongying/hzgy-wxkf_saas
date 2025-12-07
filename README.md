# 微信客服SaaS服务 (wxkf_saas)

基于微信客服API开发的多租户SaaS服务平台，支持为多个企业提供微信生态的客服消息服务。

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.25-orange.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 核心特性

### 多租户架构
- ✅ **多租户管理** - 支持管理无限个企业的微信客服
- ✅ **独立Token管理** - 每个租户独立的访问Token和缓存
- ✅ **租户隔离** - 数据库级别的租户数据隔离
- ✅ **自动Token刷新** - Token过期前60秒自动刷新机制

### 微信客服功能
- ✅ **客服账号管理** - 添加、修改、删除、查询客服账号
- ✅ **消息收发** - 支持文本、图片、语音、视频、文件消息
- ✅ **素材管理** - 上传和下载临时素材
- ✅ **客户信息获取** - 获取客户基础信息
- ✅ **消息同步** - 实时同步客户消息和事件

### 技术特性
- ⚡ **异步数据库** - 支持MySQL、PostgreSQL、SQLite，高性能异步操作
- 🗄️ **多数据库支持** - 灵活配置，支持直接URL或环境变量
- 🔄 **自动迁移** - 自动创建和更新表结构
- 📝 **自动文档** - 基于FastAPI自动生成Swagger文档
- 🔐 **JWT认证** - 完整的JWT认证和权限管理系统
- 🔒 **完整安全** - 数据加密、权限控制、HTTPS支持

## 🏗️ 项目架构

```
wxkf_saas/
├── core/                      # 核心模块
│   ├── config.py             # 配置管理（支持多数据库）
│   ├── database.py            # 异步数据库管理器
│   ├── token_manager.py       # 多租户Token管理器
│   ├── client.py             # 微信API客户端
│   ├── exceptions.py         # 异常定义
│   ├── security.py           # JWT认证和权限管理
│   └── dependencies.py       # 依赖注入和中间件
├── models/                    # 数据模型
│   ├── base.py               # 基础模型
│   ├── tenant.py             # 租户模型
│   ├── kf_account.py          # 客服账号模型
│   ├── message.py            # 消息模型
│   ├── media.py              # 素材模型
│   └── user.py               # 用户模型
├── api/                       # API模块
│   ├── kf_account.py          # 客服账号API
│   ├── message.py             # 消息API
│   └── media.py              # 素材API
├── routes/                    # FastAPI路由
│   ├── tenant.py             # 租户管理路由
│   ├── auth.py               # 认证相关路由
│   └── health.py             # 健康检查路由
├── test_scripts/              # 测试脚本目录
├── dev_tmp/                   # 远程调试临时文件目录
├── docs/                      # 开发说明文档目录
├── dev_docs/                  # 知识库文件目录
├── main.py                    # 主应用入口
├── requirements.txt           # 项目依赖
├── .env.example              # 配置文件示例
└── README.md                 # 项目文档
```

## 🗄️ 数据库支持

### 支持的数据库类型

| 数据库类型 | 同步驱动 | 异步驱动 | 适用场景 |
|----------|----------|----------|----------|
| MySQL | pymysql | aiomysql | 通用业务、云数据库 |
| PostgreSQL | psycopg2 | asyncpg | 复杂查询、事务要求高 |
| SQLite | sqlite | aiosqlite | 开发测试、小型应用 |

### 配置方式

#### 方式1: 环境变量（推荐用于开发/生产）
```env
# 数据库配置
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=wxkf_saas
DB_USER=user
DB_PASSWORD=password
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

#### 方式2: 直接URL配置（推荐用于生产）
```env
# 直接配置完整URL（会覆盖上述参数）
DATABASE_URL=mysql+pymysql://user:password@prod-db.internal:3306/wxkf_saas?charset=utf8mb4
ASYNC_DATABASE_URL=mysql+aiomysql://user:password@prod-db.internal:3306/wxkf_saas?charset=utf8mb4
```

#### 方式3: SQLite配置
```env
# SQLite配置
DB_TYPE=sqlite
DB_PATH=./data/app.db
DB_POOL_SIZE=1
DB_MAX_OVERFLOW=5
```

### URL生成规则

- **同步URL**: `{db_type}+{sync_driver}://{user}:{password}@{host}:{port}/{database}{params}`
- **异步URL**: `{db_type}+{async_driver}://{user}:{password}@{host}:{port}/{database}{params}`
- **SQLite**: `sqlite+{driver}:///path/to/database`

## 🚀 快速开始

### 1. 环境准备

```bash
# 1. 克隆项目
git clone https://github.com/your-org/wxkf_saas.git
cd wxkf_saas

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件填写实际配置
```

### 2. 数据库初始化

```bash
# MySQL (推荐生产环境)
mysql -u root -p -e "CREATE DATABASE wxkf_saas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# PostgreSQL (推荐复杂业务)
psql -U postgres -c "CREATE DATABASE wxkf_saas ENCODING 'UTF8';"

# SQLite (开发测试)
# 数据库目录会自动创建
```

### 3. 启动服务

```bash
# 开发模式
python main.py

# 生产模式
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8083 \
  --log-level info
```

## 📋 配置说明

### 必需配置项

```env
# ===== 服务商配置 (必需) =====
SUITE_ID=your_suite_id                    # 服务商套件ID
SUITE_SECRET=your_suite_secret              # 服务商套件Secret
PROVIDER_SECRET=your_provider_secret            # 服务商密钥
PROVIDER_TOKEN=your_provider_token              # 服务商回调Token
PROVIDER_ENCODING_AES_KEY=your_key          # 服务商回调加密密钥

# ===== 数据库配置 (必需) =====
# 方式1: 环境变量
DB_TYPE=mysql                                 # 数据库类型 (mysql/postgresql/sqlite)
DB_HOST=localhost                               # 数据库主机
DB_PORT=3306                                   # 数据库端口
DB_NAME=wxkf_saas                             # 数据库名称
DB_USER=wxkf_saas                             # 数据库用户
DB_PASSWORD=wxkf_saas                         # 数据库密码
DB_POOL_SIZE=10                                # 连接池大小
DB_MAX_OVERFLOW=20                               # 最大额外连接数

# 方式2: 直接URL配置（生产推荐）
DATABASE_URL=mysql+pymysql://user:pass@host:port/db
ASYNC_DATABASE_URL=mysql+aiomysql://user:pass@host:port/db
```

### 可选配置项

```env
# ===== 服务器配置 =====
SERVER_URL=https://your-domain.com              # 服务器地址（生产必需）
FASTAPI_HOST=127.0.0.1                     # 监听地址
FASTAPI_PORT=8083                            # 监听端口

# ===== Redis配置 (推荐) =====
REDIS_HOST=localhost                           # Redis主机
REDIS_PORT=6379                              # Redis端口
REDIS_DB=0                                   # Redis数据库
REDIS_PASSWORD=                               # Redis密码
REDIS_KEY_PREFIX=wxkf_saas:                   # 键前缀

# ===== JWT认证配置 =====
SECRET_KEY=your-super-secret-jwt-key-here    # JWT签名密钥（生产环境必须更改）
ALGORITHM=HS256                               # JWT算法
ACCESS_TOKEN_EXPIRE_MINUTES=30               # 访问令牌过期时间（分钟）
REFRESH_TOKEN_EXPIRE_DAYS=7                  # 刷新令牌过期时间（天）

# ===== SSL/TLS配置 =====
SSL_CERT_PATH=/path/to/cert.pem             # SSL证书路径
SSL_KEY_PATH=/path/to/key.pem               # SSL私钥路径

# ===== 文件上传配置 =====
UPLOAD_DIR=uploads                            # 上传目录
MAX_FILE_SIZE=10485760                      # 最大文件大小(10MB)

# ===== 日志配置 =====
LOG_LEVEL=INFO                               # 日志级别
LOG_FILE=/var/log/wxkf_saas/app.log         # 日志文件路径
```

## 📚 API使用

### JWT认证

#### 用户登录获取Token
```python
import requests

# 用户登录
response = requests.post("http://localhost:8083/api/auth/login", json={
    "username": "admin",
    "password": "password"
})

data = response.json()
access_token = data["access_token"]
refresh_token = data["refresh_token"]

# 保存Token用于后续请求
headers = {
    "Authorization": f"Bearer {access_token}"
}
```

#### 刷新Token
```python
# 当access_token过期时，使用refresh_token获取新的token
response = requests.post("http://localhost:8083/api/auth/refresh", json={
    "refresh_token": refresh_token
})

data = response.json()
new_access_token = data["access_token"]
```

#### 用户注册
```python
response = requests.post("http://localhost:8083/api/auth/register", json={
    "username": "newuser",
    "password": "secure_password",
    "email": "user@example.com",
    "corp_id": "your_corp_id"  # 所属企业ID
})

user_id = response.json()["id"]
```

#### 获取当前用户信息
```python
response = requests.get(
    "http://localhost:8083/api/auth/me",
    headers=headers
)

user_info = response.json()
```

### 租户管理

#### 创建租户
```python
import requests

response = requests.post("http://localhost:8083/api/tenants/",
    json={
        "corp_id": "your_corp_id",
        "corp_name": "示例企业",
        "contact_name": "张三",
        "contact_phone": "13800138000",
        "contact_email": "zhangsan@example.com"
    },
    headers=headers  # 需要认证
)

tenant_id = response.json()["id"]
```

#### 获取租户列表
```python
response = requests.get(
    "http://localhost:8083/api/tenants/",
    headers=headers  # 需要认证
)
tenants = response.json()
```

### 客服账号管理

```python
from wxkf_saas.core.client import WxKfSaasClient
from wxkf_saas.core.config import WxKfSaasConfig
from wxkf_saas.core.database import get_async_db
from wxkf_saas.api.kf_account import KfAccountApi

# 初始化客户端
config = WxKfSaasConfig()
client = WxKfSaasClient(config)
kf_api = KfAccountApi(client)

# 添加客服账号
async for db in get_async_db():
    response = await kf_api.add(
        corp_id="your_corp_id",
        name="客服小王",
        media_id="media_id_from_upload"
    )

    kf_id = response.open_kfid
    print(f"客服账号ID: {kf_id}")
```

**注意**: 调用微信API时，用户必须已登录并有相应权限

### 消息发送

```python
from wxkf_saas.api.message import MessageApi

# 创建消息API
msg_api = MessageApi(client)

# 发送文本消息
async for db in get_async_db():
    response = await msg_api.send_text(
        corp_id="your_corp_id",
        touser="external_userid",
        content="您好，有什么可以帮助您的吗？"
    )

    msg_id = response.msgid
    print(f"消息ID: {msg_id}")
```

### 消息同步

```python
# 同步客户消息
async for db in get_async_db():
    response = await msg_api.sync_msg(
        corp_id="your_corp_id",
        limit=100
    )

    messages = response.msg_list
    for msg in messages:
        print(f"客户消息: {msg.content}")

    print(f"是否还有更多: {response.has_more}")
    print(f"下次游标: {response.next_cursor}")
```

## 🐳 部署

### Docker部署

#### Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8083
CMD ["python", "main.py"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  wxkf_saas:
    build: .
    ports:
      - "8083:8083"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - ASYNC_DATABASE_URL=${ASYNC_DATABASE_URL}
      - SUITE_ID=${SUITE_ID}
      - SUITE_SECRET=${SUITE_SECRET}
    volumes:
      - ./uploads:/app/uploads
      - ./data:/app/data
    depends_on:
      - mysql
      - redis

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=wxkf_saas
      - MYSQL_USER=wxkf_saas
      - MYSQL_PASSWORD=wxkf_saas
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
```

### Kubernetes部署

#### ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: wxkf-saas-config
data:
  DB_TYPE: "mysql"
  DB_HOST: "mysql-service"
  DB_PORT: "3306"
  DB_NAME: "wxkf_saas"
  DB_USER: "wxkf_saas"
  DB_PASSWORD: "wxkf_saas"
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
```

#### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wxkf-saas
spec:
  replicas: 3
  selector:
    matchLabels:
      app: wxkf-saas
  template:
    metadata:
      labels:
        app: wxkf-saas
    spec:
      containers:
      - name: wxkf-saas
        image: wxkf-saas:latest
        ports:
        - containerPort: 8083
        envFrom:
        - configMapRef:
            name: wxkf-saas-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
```

## 🔒 安全性

### JWT认证安全
- 🔐 **双Token机制** - Access Token + Refresh Token组合
- 🔄 **自动刷新** - Access Token过期自动使用Refresh Token更新
- ⏰ **可配置过期时间** - 灵活设置Token有效期
- 🛡️ **Token黑名单** - 主动作废Token机制
- 🔒 **密码加密存储** - 使用bcrypt哈希加密用户密码

### Token安全
- 🔐 **数据库加密存储** - Token在数据库中加密存储
- 🔄 **自动刷新机制** - Token过期前自动刷新，避免服务中断
- ⏰ **过期时间管理** - 合理设置Token过期时间和缓存TTL
- 🚫 **权限最小化** - 每个租户仅拥有必要的权限

### API安全
- 🔐 **输入验证** - 使用Pydantic进行完整的请求验证
- 🔒 **HTTPS支持** - 生产环境强制使用HTTPS
- 🛡️ **CORS控制** - 可配置的跨域资源共享控制
- 🚨 **异常处理** - 完整的异常处理和错误提示
- 🎯 **权限控制** - 基于角色的访问控制(RBAC)

### 数据安全
- 🔐 **密码加密** - 敏感配置使用环境变量或密钥管理
- 🔒 **连接加密** - 支持SSL/TLS数据库连接
- 🛡️ **SQL注入防护** - SQLAlchemy ORM提供SQL注入防护
- 🔒 **数据隔离** - 租户数据严格隔离，防止数据泄露

## 📊 性能优化

### 数据库优化
- ⚡ **异步操作** - 支持异步数据库操作，提高并发性能
- 🔄 **连接池管理** - 可配置连接池大小和溢出数量
- 📝 **索引优化** - 在关键字段上建立索引
- 🧹 **定期清理** - 自动清理过期Token和临时数据

### 缓存优化
- ⚡ **Redis缓存** - Token缓存，减少数据库查询频率
- 📊 **缓存策略** - 合理的缓存过期时间和刷新策略
- 🔄 **预热机制** - 启动时预加载常用Token

### 并发优化
- 🚀 **异步请求** - 支持HTTPX异步请求客户端
- 🔧 **连接复用** - HTTP连接复用和Keep-Alive
- ⚡ **批量操作** - 支持批量消息发送和Token操作

## 📖 API文档

服务启动后，可通过以下地址访问API文档：

- **Swagger UI**: http://localhost:8083/docs
- **ReDoc**: http://localhost:8083/redoc
- **OpenAPI JSON**: http://localhost:8083/openapi.json

### 主要端点

#### 认证相关
| 方法 | 路径 | 描述 | 参数 |
|------|------|------|------|
| POST | `/api/auth/register` | 用户注册 | 用户信息 |
| POST | `/api/auth/login` | 用户登录 | 用户名/密码 |
| POST | `/api/auth/refresh` | 刷新Token | refresh_token |
| GET | `/api/auth/me` | 获取当前用户信息 | 需要认证 |

#### 租户管理
| 方法 | 路径 | 描述 | 参数 |
|------|------|------|------|
| POST | `/api/tenants/` | 创建租户 | 租户信息（需认证） |
| GET | `/api/tenants/` | 获取租户列表 | 分页参数（需认证） |
| GET | `/api/tenants/{corp_id}` | 获取租户详情 | 租户ID（需认证） |
| PUT | `/api/tenants/{corp_id}` | 更新租户 | 租户ID + 更新信息（需认证） |
| DELETE | `/api/tenants/{corp_id}` | 删除租户 | 租户ID（需认证） |

#### 健康检查
| 方法 | 路径 | 描述 | 参数 |
|------|------|------|------|
| GET | `/` | 健康检查 | 无 |
| GET | `/health` | 详细健康检查 | 无 |

## 🧪 测试

### 运行测试
```bash
# 安装测试依赖
pip install pytest pytest-asyncio httpx

# 运行所有测试
pytest test_scripts/

# 运行特定测试
pytest test_scripts/test_config.py
```

### 测试覆盖率
```bash
# 安装覆盖率工具
pip install pytest-cov

# 运行测试并生成覆盖率报告
pytest --cov=wxkf_saas --cov-report=html test_scripts/

# 查看报告
open htmlcov/index.html
```

## 📈 监控

### 健康检查
```python
# 基础健康检查
GET /

# 详细健康检查（包含数据库状态）
GET /health

# 返回示例
{
    "status": "ok",
    "service": "wxkf_saas_api",
    "version": "1.0.0",
    "database": "connected",
    "cache": "connected"
}
```

### 日志管理
```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/var/log/wxkf_saas/app.log')
    ]
)
```

### 监控指标
- 📊 **API请求数** - 请求总数、成功率、错误率
- 🗄️ **数据库连接数** - 活跃连接数、连接池使用率
- ⚡ **响应时间** - API响应时间分布和平均值
- 🔄 **Token刷新次数** - 自动刷新次数和成功率
- 💾 **缓存命中率** - Redis缓存命中率统计

## 🤝 贡献指南

### 开发环境搭建
1. Fork本项目
2. 创建功能分支：`git checkout -b feature/amazing-feature`
3. 进行开发和测试
4. 提交代码：`git commit -m "Add amazing feature"`
5. 推送分支：`git push origin feature/amazing-feature`
6. 创建Pull Request

### 代码规范
- 🐍 使用 **PEP 8** 编码规范
- 📝 添加适当的 **注释和文档字符串**
- 🧪 编写相应的 **单元测试**
- 🎯 遵循 **RESTful API** 设计原则

### 提交规范
- 🎯 **feat**: 新功能
- 🔧 **fix**: 修复bug
- 📝 **docs**: 文档更新
- 🎨 **style**: 代码格式调整
- ♻️ **refactor**: 重构代码
- ⚡ **perf**: 性能优化
- 🧪 **test**: 测试相关

## 📄 许可证

本项目采用 **MIT License**，详情请查看 [LICENSE](LICENSE) 文件。

## 📞 支持

如有问题或建议，请通过以下方式联系：

- 🐛 **问题反馈**: 提交 [Issue](https://github.com/your-org/wxkf_saas/issues)
- 💡 **功能建议**: 提交 [Issue](https://github.com/your-org/wxkf_saas/issues) 并标记为enhancement
- 📧 **技术交流**: 发送邮件至 dev@example.com
- 📖 **文档问题**: 查看项目Wiki或提交文档Issue

## 🏆 致谢

感谢所有为项目做出贡献的开发者和用户！

- [所有贡献者列表](https://github.com/your-org/wxkf_saas/graphs/contributors)

---

**⭐ 如果本项目对您有帮助，请给我们一个Star！**