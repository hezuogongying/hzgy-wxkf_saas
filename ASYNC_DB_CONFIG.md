# 异步数据库配置文档

## 概述

本项目已升级为使用异步数据库操作，支持高并发的微信客服SaaS服务。配置使用 `mysql+aiomysql` 驱动，同时保留同步操作作为备用。

## 配置结构

### 1. 双引擎配置

```python
class DatabaseManager:
    def __init__(self, config: WxKfSaasConfig):
        # 异步引擎（主要使用）
        self.async_engine = create_async_engine(
            config.db_async_url,  # mysql+aiomysql://
            poolclass=QueuePool,
            pool_size=config.db_pool_size,
            max_overflow=config.db_max_overflow,
            pool_pre_ping=True,
            echo=config.log_level == "DEBUG",
        )

        # 同步引擎（备用）
        self.sync_engine = create_engine(
            config.db_url,  # mysql+pymysql://
            poolclass=QueuePool,
            pool_size=config.db_pool_size,
            max_overflow=config.db_max_overflow,
            pool_pre_ping=True,
            echo=config.log_level == "DEBUG",
        )
```

### 2. URL 配置

```env
# .env 文件配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=wxkf_saas
DB_USER=wxkf_saas
DB_PASSWORD=wxkf_saas
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

### 3. 自动生成的URL

- **同步URL**: `mysql+pymysql://user:pass@host:port/db?charset=utf8mb4`
- **异步URL**: `mysql+aiomysql://user:pass@host:port/db?charset=utf8mb4`

## 使用方法

### 1. 获取异步会话

```python
from core.database import get_async_db

async def some_function():
    async for session in get_async_db():
        # 执行异步操作
        result = await session.execute(query)
        await session.commit()  # 自动处理
```

### 2. 依赖注入使用

```python
from fastapi import Depends
from core.database import get_async_db

@router.get("/tenants")
async def get_tenants(db: AsyncSession = Depends(get_async_db)):
    # 异步查询
    result = await db.execute(select(Tenant))
    return result.scalars().all()
```

### 3. 复杂异步操作

```python
async def complex_operation():
    async for session in get_async_db():
        try:
            # 开始事务
            async with session.begin():
                # 创建租户
                tenant = Tenant(corp_id="new", name="新企业")
                session.add(tenant)

                # 创建Token
                token = TenantToken(
                    corp_id="new",
                    token_type="access",
                    token_value="token123"
                )
                session.add(token)

            # 自动提交
            print("操作成功")
        except Exception as e:
            # 自动回滚
            print(f"操作失败: {e}")
```

## 性能优化

### 1. 连接池配置

```env
# 根据服务器配置调整
DB_POOL_SIZE=20        # 核心连接数
DB_MAX_OVERFLOW=40      # 最大额外连接
```

**建议配置**:
- 小型服务器: 5-10 核心连接
- 中型服务器: 10-20 核心连接
- 大型服务器: 20-40 核心连接

### 2. 批量操作优化

```python
async def batch_create_tenants(tenant_data_list):
    async for session in get_async_db():
        async with session.begin():
            # 批量添加
            session.add_all([
                Tenant(**data) for data in tenant_data_list
            ])
        # 一次提交
```

### 3. 查询优化

```python
# 使用索引
stmt = select(Tenant).where(Tenant.corp_id == corp_id)

# 分页查询
stmt = select(Tenant).offset(page * size).limit(size)

# 只查询需要的字段
stmt = select(Tenant.id, Tenant.name)
```

## 故障排查

### 1. 常见错误

#### ModuleNotFoundError: No module named 'aiomysql'
```bash
# 安装依赖
pip install aiomysql==0.2.0
```

#### 数据库连接错误
```bash
# 检查数据库服务
mysql -h localhost -u root -p

# 检查端口
netstat -tlnp | grep :3306
```

#### URL格式错误
```python
# 正确格式
mysql+aiomysql://user:password@host:port/database

# 错误格式
mysql://user:password@host:port/database  # 缺少驱动
```

### 2. 调试配置

```env
# 开启SQL日志
LOG_LEVEL=DEBUG

# 检查连接
DB_POOL_SIZE=1
DB_MAX_OVERFLOW=0
```

### 3. 监控指标

- 连接池使用率
- 查询响应时间
- 事务成功率
- 错误日志统计

## 部署建议

### 1. 生产环境配置

```env
# 数据库配置（内网地址）
DB_HOST=10.0.0.100
DB_PORT=3306
DB_NAME=wxkf_saas_prod
DB_USER=wxkf_saas_prod
DB_PASSWORD=strong_password
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=100

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=/var/log/wxkf_saas/db.log
```

### 2. 性能监控

```python
# 添加连接池事件监听
from sqlalchemy import event

@event.listens_for(engine, "connect")
def receive_connect(dbapi_connection, connection_record):
    print("新连接建立")

@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    print("连接从池中取出")
```

### 3. 健康检查

```python
async def health_check():
    async for session in get_async_db():
        try:
            result = await session.execute("SELECT 1")
            return {"status": "healthy", "db": "connected"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
```

## 最佳实践

1. **始终使用异步操作**: 提高并发性能
2. **合理配置连接池**: 避免连接泄漏
3. **使用事务**: 保证数据一致性
4. **处理异常**: 正确回滚失败操作
5. **监控性能**: 及时发现瓶颈
6. **定期维护**: 优化查询和索引