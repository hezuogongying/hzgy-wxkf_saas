# -*- coding: utf-8 -*-
"""租户隔离功能 - 快速改造方案"""

from sqlalchemy import event
from sqlalchemy.orm import Session
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import time

class TenantIsolation:
    """租户隔离混入类"""

    @classmethod
    def apply_to_model(cls, model_class):
        """为模型类添加租户隔离功能"""

        # 添加租户过滤的查询方法
        def query_with_tenant(cls, session, tenant_id):
            """带租户过滤的查询"""
            return session.query(model_class).filter(model_class.corp_id == tenant_id)

        # 添加创建时自动设置租户ID
        original_init = model_class.__init__

        def __init__(self, *args, **kwargs):
            if 'corp_id' not in kwargs and hasattr(self, '_get_current_tenant_id'):
                tenant_id = self._get_current_tenant_id()
                if tenant_id:
                    kwargs['corp_id'] = tenant_id
            original_init(self, *args, **kwargs)

        model_class.query_with_tenant = classmethod(query_with_tenant)
        model_class.__init__ = __init__

        return model_class


class TenantMiddleware(BaseHTTPMiddleware):
    """租户识别中间件"""

    async def dispatch(self, request, call_next):
        # 从请求头获取租户ID
        tenant_id = request.headers.get('X-Tenant-ID')

        # 备选：从URL路径获取
        if not tenant_id and request.url.path.startswith('/api/'):
            path_parts = request.url.path.split('/')
            if len(path_parts) > 2 and path_parts[2].startswith('ww'):
                tenant_id = path_parts[2]

        # 设置到请求状态
        if tenant_id:
            request.state.tenant_id = tenant_id

        response = await call_next(request)
        return response


def get_current_tenant_id(request: Request) -> str:
    """获取当前租户ID的依赖注入"""
    if not hasattr(request.state, 'tenant_id'):
        raise HTTPException(
            status_code=400,
            detail="缺少租户信息，请在请求头中添加 X-Tenant-ID"
        )
    return request.state.tenant_id


# 自动租户过滤装饰器
def auto_tenant_filter(func):
    """自动为查询添加租户过滤的装饰器"""
    def wrapper(*args, **kwargs):
        # 提取 tenant_id 和 db
        tenant_id = None
        db = None

        for arg in args:
            if isinstance(arg, str) and arg.startswith('ww'):
                tenant_id = arg
            elif hasattr(arg, 'query'):
                db = arg

        for key, value in kwargs.items():
            if key == 'tenant_id' and value:
                tenant_id = value
            elif key == 'db' and hasattr(value, 'query'):
                db = value

        # 如果有租户ID和数据库连接，自动过滤
        if tenant_id and db and hasattr(func, '__self__'):
            # 为查询方法添加过滤
            original_query = db.query
            def filtered_query(model):
                return original_query(model).filter(model.corp_id == tenant_id)
            db.query = filtered_query

        return func(*args, **kwargs)
    return wrapper


# 使用示例：
# 1. 为模型添加租户隔离
# from models.message import Message
# Message = TenantIsolation.apply_to_model(Message)

# 2. 在API中使用
# @router.get("/messages")
# async def get_messages(
#     tenant_id: str = Depends(get_current_tenant_id),
#     db: Session = Depends(get_db)
# ):
#     # 自动过滤当前租户的消息
#     messages = db.query(Message).all()  # 只返回当前租户的消息
#     return messages

# 3. 创建数据时自动设置租户ID
# message = Message(content="Hello")
# # 如果有租户上下文，自动设置 message.corp_id = tenant_id