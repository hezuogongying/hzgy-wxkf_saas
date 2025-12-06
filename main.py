# -*- coding: utf-8 -*-
"""微信客服SaaS服务主应用"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 先导入核心模块
from core.config import WxKfSaasConfig
from core.database import init_database
from core.exceptions import (
    WxKfApiError,
    TenantNotFoundError,
    TenantNotAuthorizedError,
    TokenExpiredError,
    ConfigurationError
)

# 添加路径后确保能够导入模块
if str(project_root) in sys.path:
    # 导入路由
    from routes.tenant import router as tenant_router
    from routes.kf_account import router as kf_account_router
    from routes.message import router as message_router
    from routes.media import router as media_router
    from routes.callback import router as callback_router
    from routes.contact import router as contact_router
else:
    raise ImportError("无法添加项目路径到 sys.path")


# 初始化配置
try:
    config = WxKfSaasConfig()
    config.validate_config()
    print("✅ 配置加载成功")
    print(f"   数据库: {config.db_host}:{config.db_port}/{config.db_name}")
    print(f"   Redis: {config.redis_host}:{config.redis_port}/{config.redis_db}")
    print(f"   服务端口: {config.fastapi_port}")
except Exception as e:
    print(f"❌ 配置加载失败: {e}")
    print("请检查 .env 文件中的配置项是否完整")
    sys.exit(1)


# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动和关闭时的处理"""
    # 启动时初始化数据库
    print("🚀 正在初始化数据库...")
    try:
        db_manager = await init_database(config)
        print("✅ 数据库初始化成功（使用异步连接）")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        print("💡 提示：如果异步初始化失败，可能是 aiomysql 驱动问题")
        print("   请检查 requirements.txt 中是否包含 aiomysql==0.2.0")
        raise

    yield

    # 关闭时清理资源
    print("👋 正在关闭应用...")
    try:
        db_manager.close()
        print("✅ 数据库连接已关闭")
    except Exception as e:
        print(f"⚠️ 关闭数据库时出错: {e}")


# 创建FastAPI应用
app = FastAPI(
    title="微信客服SaaS服务",
    description="基于微信客服API的多租户SaaS服务平台",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600
)


# 全局异常处理器
@app.exception_handler(WxKfApiError)
async def wxkf_api_error_handler(request: Request, exc: WxKfApiError):
    """微信客服API错误处理"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "wxkf_api_error",
            "errcode": exc.errcode,
            "errmsg": exc.errmsg
        }
    )


@app.exception_handler(TenantNotFoundError)
async def tenant_not_found_handler(request: Request, exc: TenantNotFoundError):
    """租户不存在错误处理"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "tenant_not_found",
            "message": f"Tenant not found: {exc.tenant_id}"
        }
    )


@app.exception_handler(TenantNotAuthorizedError)
async def tenant_not_authorized_handler(request: Request, exc: TenantNotAuthorizedError):
    """租户未授权错误处理"""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": "tenant_not_authorized",
            "message": f"Tenant not authorized: {exc.tenant_id}"
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证错误处理"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "detail": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    import traceback
    traceback.print_exc()

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_server_error",
            "message": str(exc)
        }
    )


# 挂载路由
app.include_router(tenant_router)
app.include_router(kf_account_router)
app.include_router(message_router)
app.include_router(media_router)
app.include_router(callback_router)
app.include_router(contact_router)


# 健康检查
@app.get("/", summary="健康检查", tags=["系统"])
def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "service": "微信客服SaaS服务",
        "version": "1.0.0"
    }


@app.get("/health", summary="详细健康检查", tags=["系统"])
def detailed_health_check():
    """详细健康检查"""
    return {
        "status": "ok",
        "service": "wxkf_saas_api",
        "version": "1.0.0",
        "config": {
            "database": f"{config.db_host}:{config.db_port}/{config.db_name}",
            "redis": f"{config.redis_host}:{config.redis_port}/{config.redis_db}",
        }
    }


# 主入口
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=config.fastapi_host,
        port=config.fastapi_port,
        log_level=config.log_level.lower()
    )
