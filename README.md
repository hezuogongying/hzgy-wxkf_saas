# 微信客服SaaS服务 (wxkf_saas)

基于微信客服API的多租户SaaS服务平台，支持为多个企业提供微信生态的客服消息服务。

## 功能特性

### 核心功能
- ✅ 多租户管理 - 支持管理多个企业的微信客服
- ✅ Token自动管理 - 自动获取和刷新各类Token
- ✅ 客服账号管理 - 添加、修改、删除、查询客服账号
- ✅ 消息收发 - 发送文本、图片、语音、视频、文件消息
- ✅ 消息同步 - 实时同步客户消息和事件
- ✅ 素材管理 - 上传和下载临时素材
- ✅ 客户信息获取 - 获取客户基础信息

### 技术特性
- 🚀 基于FastAPI的高性能异步框架
- 💾 支持MySQL数据库存储租户配置
- ⚡ 支持Redis缓存加速Token访问
- 🔐 完整的异常处理和错误提示
- 📝 自动生成的API文档
- 🔄 RESTful API设计

## 架构设计

```
wxkf_saas/
├── core/                  # 核心模块
│   ├── config.py         # 配置管理
│   ├── database.py       # 数据库管理
│   ├── token_manager.py  # 多租户Token管理
│   ├── client.py         # API客户端
│   └── exceptions.py     # 异常定义
├── models/               # 数据模型
│   ├── base.py          # 基础模型
│   ├── tenant.py        # 租户模型
│   ├── kf_account.py    # 客服账号模型
│   ├── message.py       # 消息模型
│   └── media.py         # 素材模型
├── api/                 # API模块
│   ├── kf_account.py    # 客服账号API
│   ├── message.py       # 消息API
│   └── media.py         # 素材API
├── routes/              # 路由模块
│   └── tenant.py        # 租户管理路由
├── main.py              # 主应用入口
└── .env.example         # 配置文件示例
```

## 快速开始

### 1. 安装依赖

```bash
cd wxkf_saas
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

必需配置项：
- `SUITE_ID` - 服务商套件ID
- `SUITE_SECRET` - 服务商套件Secret
- `PROVIDER_SECRET` - 服务商密钥
- `PROVIDER_TOKEN` - 服务商回调Token
- `PROVIDER_ENCODING_AES_KEY` - 服务商回调加密密钥
- `DB_NAME` - 数据库名称
- `DB_USER` - 数据库用户
- `DB_PASSWORD` - 数据库密码

### 3. 初始化数据库

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE wxkf_saas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 应用会自动创建表结构
```

### 4. 启动服务

```bash
python main.py
```

服务将在 `http://localhost:8083` 启动。

### 5. 访问API文档

- Swagger UI: http://localhost:8083/docs
- ReDoc: http://localhost:8083/redoc

## API使用示例

### 租户管理

#### 创建租户
```bash
curl -X POST "http://localhost:8083/api/tenants/" \
  -H "Content-Type: application/json" \
  -d '{
    "corp_id": "wx1234567890",
    "corp_name": "测试企业",
    "contact_name": "张三",
    "contact_phone": "13800138000",
    "contact_email": "zhangsan@example.com"
  }'
```

#### 获取租户列表
```bash
curl "http://localhost:8083/api/tenants/?skip=0&limit=20"
```

#### 获取租户详情
```bash
curl "http://localhost:8083/api/tenants/wx1234567890"
```

### 客服账号管理

#### 添加客服账号
```python
from wxkf_saas.core.config import WxKfSaasConfig
from wxkf_saas.core.database import get_db_manager
from wxkf_saas.core.client import WxKfSaasClient
from wxkf_saas.api.kf_account import KfAccountApi

# 初始化配置
config = WxKfSaasConfig()

# 获取数据库会话
db = next(get_db_manager().get_session())

# 创建客户端
client = WxKfSaasClient(config, db)

# 创建客服账号API实例
kf_api = KfAccountApi(client)

# 添加客服账号
response = kf_api.add(
    corp_id="wx1234567890",
    name="客服小王",
    media_id="media_id_from_upload"
)

print(f"客服账号ID: {response.open_kfid}")
```

### 消息发送

#### 发送文本消息
```python
from wxkf_saas.api.message import MessageApi

# 创建消息API实例
msg_api = MessageApi(client)

# 发送文本消息
response = msg_api.send_text(
    corp_id="wx1234567890",
    touser="external_userid_xxx",
    open_kfid="wkAJ2GCAAAZSfhHCt7IFSvLKtMPxyJTw",
    content="您好，有什么可以帮您的吗？"
)

print(f"消息ID: {response.msgid}")
```

#### 同步消息
```python
# 同步客户消息
response = msg_api.sync_msg(
    corp_id="wx1234567890",
    limit=100
)

print(f"消息数量: {len(response.msg_list)}")
print(f"是否还有更多: {response.has_more}")
print(f"下次游标: {response.next_cursor}")

# 处理消息
for msg in response.msg_list:
    print(f"消息ID: {msg.msgid}")
    print(f"消息类型: {msg.msgtype}")
    if msg.msgtype == "text":
        print(f"文本内容: {msg.text.content}")
```

### 素材管理

#### 上传图片
```python
from wxkf_saas.api.media import MediaApi

# 创建素材API实例
media_api = MediaApi(client)

# 上传图片
response = media_api.upload(
    corp_id="wx1234567890",
    media_type="image",
    file_path="/path/to/image.jpg"
)

print(f"Media ID: {response.media_id}")
```

#### 下载素材
```python
# 下载并保存
response = media_api.download(
    corp_id="wx1234567890",
    media_id="media_id_xxx",
    save_path="/path/to/save/image.jpg"
)

print(f"文件类型: {response.content_type}")
print(f"文件名: {response.filename}")
```

## 数据库设计

### tenants 表 - 租户信息
- `id` - 主键
- `corp_id` - 企业ID(唯一)
- `corp_name` - 企业名称
- `permanent_code` - 永久授权码
- `is_active` - 是否激活
- `is_authorized` - 是否已授权
- `callback_url` - 回调URL
- `contact_name` - 联系人姓名
- `created_at` - 创建时间
- `updated_at` - 更新时间

### tenant_tokens 表 - Token信息
- `id` - 主键
- `corp_id` - 企业ID
- `token_type` - Token类型(access_token/suite_access_token等)
- `token_value` - Token值
- `expires_at` - 过期时间戳
- `created_at` - 创建时间
- `updated_at` - 更新时间

## 部署指南

### Docker部署

1. 创建 Dockerfile:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

2. 构建镜像:
```bash
docker build -t wxkf-saas:latest .
```

3. 运行容器:
```bash
docker run -d \
  --name wxkf-saas \
  -p 8083:8083 \
  --env-file .env \
  wxkf-saas:latest
```

### 生产环境部署

使用Gunicorn + Uvicorn:

```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8083 \
  --log-level info
```

## 开发计划

- [ ] 实现微信授权回调处理
- [ ] 添加会话分配API
- [ ] 添加智能助手API
- [ ] 添加知识库API
- [ ] 实现消息队列处理
- [ ] 添加监控和日志系统
- [ ] 完善单元测试
- [ ] 添加性能优化

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交Issue或联系开发团队。
