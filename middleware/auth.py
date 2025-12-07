# -*- coding: utf-8 -*-
"""认证中间件"""

from fastapi import Request, HTTPException, status, Depends
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Optional
import logging

from core.auth import AuthService, User, TokenData

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """JWT认证中间件"""

    # 不需要认证的路径
    SKIP_AUTH_PATHS = {
        "/health",
        "/login",
        "/register",
        "/refresh-token",
        "/docs",
        "/redoc",
        "/openapi.json",
    }

    def __init__(self, app, skip_paths: Optional[list] = None):
        super().__init__(app)
        if skip_paths:
            self.SKIP_AUTH_PATHS.update(skip_paths)

    async def dispatch(self, request: Request, call_next) -> Response:
        # 检查是否跳过认证
        if self._should_skip_auth(request):
            return await call_next(request)

        # 提取并验证Token
        token = self._extract_token_from_request(request)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="未提供认证令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 验证Token
        token_data = AuthService.verify_token(token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 获取用户信息
        user = await self._get_user_from_token(token_data)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已禁用"
            )

        # 将用户信息添加到请求状态
        request.state.user = user
        request.state.tenant_id = user.corp_id

        return await call_next(request)

    def _should_skip_auth(self, request: Request) -> bool:
        """判断是否应该跳过认证"""
        path = request.url.path

        # 检查路径是否在跳过列表中
        for skip_path in self.SKIP_AUTH_PATHS:
            if path.startswith(skip_path):
                return True

        # 检查选项请求
        if request.method == "OPTIONS":
            return True

        return False

    def _extract_token_from_request(self, request: Request) -> Optional[str]:
        """从请求中提取Token"""
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None

        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer":
            return None

        return token

    async def _get_user_from_token(self, token_data: TokenData) -> Optional[User]:
        """从Token数据获取用户信息"""
        try:
            # 这里应该从数据库获取用户信息
            # 暂时使用模拟数据
            # TODO: 实现真实的用户查询逻辑
            mock_users = {
                "admin": {
                    "id": "admin",
                    "username": "admin",
                    "corp_id": token_data.corp_id,
                    "role": "admin",
                    "permissions": ["admin", "read", "write"],
                    "is_active": True
                }
            }

            user_data = mock_users.get(token_data.user_id)
            if user_data:
                return User(**user_data)

            return None

        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return None


async def get_current_user(request: Request) -> User:
    """获取当前用户依赖注入"""
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未认证"
        )
    return request.state.user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前活跃用户依赖注入"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未激活"
        )
    return current_user


async def get_current_tenant_id(request: Request) -> str:
    """获取当前租户ID依赖注入"""
    if hasattr(request.state, "tenant_id"):
        return request.state.tenant_id

    # 备选方案：从请求头获取
    tenant_id = request.headers.get("X-Tenant-ID")
    if tenant_id:
        return tenant_id

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="缺少租户信息"
    )