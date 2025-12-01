# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个基于微信客服 API 的多租户 SaaS 服务平台,为多个企业提供微信客服消息服务。使用 FastAPI 框架,支持 MySQL 数据库和 Redis 缓存。

## 常用命令

### 项目准则

1. 测试脚本都在test_scripts下，远程调试临时文件保护都保存在dev_tmp下。知识库文件在dev_docs下，开发说明、进度等markdwon文件在docs下。
2. 保持项目根目录干净。
3. 及时提交中文 git commit，以便回溯和持续开发。
4. 始终保持中文交流
5. 代码要模块化原则，详细中文注释

### 环境配置

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 然后编辑 .env 填写配置
```

### 运行服务

```bash
# 开发模式运行
python main.py

# 生产模式运行
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8083 \
  --log-level info
```

### 数据库操作

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE wxkf_saas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 应用会在启动时自动创建表结构
```

### 测试和调试

```bash
# 测试脚本保存在
d:\project\python\wxkf_saas\test_scripts\

# 远程调试临时文件保存在
d:\project\python\wxkf_saas\dev_tmp\
```

## 核心架构

### 多租户 Token 管理机制

这是项目的核心架构特点,需要理解以下 Token 层级关系:

1. **provider_access_token** (服务商级别)

   - 使用 `suite_id` + `provider_secret` 获取
   - 不区分租户,全局共享
   - 在 `token_manager.py` 中以 `corp_id="_provider_"` 标识
2. **suite_access_token** (服务商级别)

   - 需要 `suite_ticket` (通过回调获得,当前未实现)
   - 用于获取企业 `access_token`
   - 在 `token_manager.py` 中以 `corp_id="_suite_"` 标识
3. **access_token** (企业级别)

   - 每个租户(企业)独立的 Token
   - 使用 `permanent_code` + `suite_access_token` 获取
   - 区分不同租户

### Token 存储策略

Token 采用 **两级缓存** 机制:

1. **Redis 缓存** - 优先级最高,快速访问
2. **MySQL 数据库** - 持久化存储,Redis 未命中时回退
3. **自动刷新** - Token 过期前 60 秒自动刷新

实现位置: `core/token_manager.py:MultiTenantTokenManager`

### API 请求流程

所有 API 请求遵循统一流程:

1. 通过 `WxKfSaasClient._request()` 发起请求
2. 根据参数决定使用哪种 Token:
   - `use_provider_token=True` → provider_access_token
   - `use_suite_token=True` → suite_access_token
   - 默认 → 企业的 access_token (需要 `corp_id`)
3. Token 自动通过 `MultiTenantTokenManager` 获取和刷新
4. 响应自动解析为 Pydantic 模型

### 数据库模型

#### tenants 表

- 存储租户(企业)基础信息
- `permanent_code` - 永久授权码,用于获取企业 access_token
- `is_authorized` - 是否已完成授权流程

#### tenant_tokens 表

- 存储所有类型的 Token
- `corp_id` - 租户标识 (特殊值: `_provider_`, `_suite_`)
- `token_type` - Token 类型枚举
- `expires_at` - 过期时间戳

### 异常处理体系

自定义异常层级 (`core/exceptions.py`):

- `WxKfApiError` - 微信 API 返回错误(errcode != 0)
- `TenantNotFoundError` - 租户不存在
- `TenantNotAuthorizedError` - 租户未授权
- `TokenExpiredError` - Token 过期

全局异常处理器在 `main.py` 中注册,自动转换为 HTTP 响应。

## API 模块结构

### API 类设计模式

所有 API 类遵循相同模式:

```python
class XxxApi:
    def __init__(self, client: WxKfSaasClient):
        self._client = client

    def method_name(self, corp_id: str, ...) -> ResponseModel:
        return self._client._request(
            "POST/GET",
            "/endpoint",
            response_model=ResponseModel,
            corp_id=corp_id,
            json_data=...
        )
```

- `KfAccountApi` - 客服账号管理 (添加、修改、删除、查询)
- `MessageApi` - 消息收发 (文本、图片、语音、视频、文件)
- `MediaApi` - 素材管理 (上传、下载临时素材)

### 文件上传处理

文件上传 (`MediaApi.upload`) 支持两种方式:

1. 文件路径 (`file_path`)
2. 文件对象 (`file_obj` + `filename`)

Content-Type 自动根据文件后缀判断。

## 配置管理

### 必需配置项

在 `.env` 文件中必须配置:

- `SUITE_ID`, `SUITE_SECRET` - 服务商套件凭证
- `PROVIDER_SECRET`, `PROVIDER_TOKEN`, `PROVIDER_ENCODING_AES_KEY` - 服务商密钥
- `DB_NAME`, `DB_USER`, `DB_PASSWORD` - 数据库凭证

### 配置验证

应用启动时会调用 `config.validate_config()` 验证必需配置项,缺少任何必需配置都会导致启动失败。

## 开发注意事项

1. **始终传递 corp_id**: 除非使用 `use_provider_token` 或 `use_suite_token`,所有 API 调用都需要 `corp_id` 参数
2. **Pydantic 模型**: 所有请求和响应都使用 Pydantic 模型,利用 `model_dump(exclude_none=True)` 排除 None 值
3. **文件流处理**: 下载文件时使用 `stream=True` 参数,返回原始响应对象而非解析 JSON
4. **租户隔离**: SaaS 模式下确保数据隔离,所有操作都基于 `corp_id` 进行
5. **Token 刷新**: Token 管理器会自动处理过期,无需手动刷新
6. **异步支持**: `WxKfSaasClient` 提供 `_request_async()` 方法,但当前 API 类主要使用同步方法

## 服务端点

- **服务地址**: `http://localhost:8083`
- **API 文档**: `http://localhost:8083/docs`
- **健康检查**: `GET /health`

## 未实现功能

- 微信授权回调处理 (suite_ticket 接收)
- suite_access_token 完整实现
- 会话分配 API
- 智能助手 API
- 知识库 API
