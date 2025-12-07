# -*- coding: utf-8 -*-
"""权限管理模块"""

from functools import wraps
from typing import List, Union, Callable, Optional
from fastapi import HTTPException, status, Depends

from core.auth import User
from middleware.auth import get_current_active_user


class Permission:
    """权限类"""

    # 预定义权限
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"

    # 功能权限
    TENANT_MANAGE = "tenant:manage"
    USER_MANAGE = "user:manage"
    MESSAGE_READ = "message:read"
    MESSAGE_SEND = "message:send"
    MEDIA_UPLOAD = "media:upload"
    CALLBACK_HANDLE = "callback:handle"


class Role:
    """角色类"""

    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"

    # 角色权限映射
    ROLE_PERMISSIONS = {
        SUPERADMIN: [Permission.SUPERADMIN, Permission.ADMIN, Permission.READ, Permission.WRITE, Permission.DELETE,
                    Permission.TENANT_MANAGE, Permission.USER_MANAGE,
                    Permission.MESSAGE_READ, Permission.MESSAGE_SEND, Permission.MEDIA_UPLOAD, Permission.CALLBACK_HANDLE],
        ADMIN: [Permission.ADMIN, Permission.READ, Permission.WRITE, Permission.DELETE,
                Permission.TENANT_MANAGE, Permission.USER_MANAGE,
                Permission.MESSAGE_READ, Permission.MESSAGE_SEND, Permission.MEDIA_UPLOAD, Permission.CALLBACK_HANDLE],
        MANAGER: [Permission.READ, Permission.WRITE, Permission.TENANT_MANAGE,
                   Permission.MESSAGE_READ, Permission.MESSAGE_SEND, Permission.MEDIA_UPLOAD],
        USER: [Permission.READ, Permission.MESSAGE_SEND],
        GUEST: [Permission.READ, Permission.MESSAGE_READ]
    }

    @classmethod
    def get_permissions(cls, role: str) -> List[str]:
        """获取角色的所有权限"""
        return cls.ROLE_PERMISSIONS.get(role, [])


def has_permission(user: User, permission: str) -> bool:
    """检查用户是否具有特定权限"""
    if not user.is_active:
        return False

    # 超级管理员拥有所有权限
    if Permission.SUPERADMIN in user.permissions:
        return True

    # 检查用户权限
    return permission in user.permissions


def has_any_permission(user: User, permissions: List[str]) -> bool:
    """检查用户是否具有任一权限"""
    if not user.is_active:
        return False

    # 超级管理员拥有所有权限
    if Permission.SUPERADMIN in user.permissions:
        return True

    # 检查是否有任一权限
    return any(perm in user.permissions for perm in permissions)


def has_all_permissions(user: User, permissions: List[str]) -> bool:
    """检查用户是否具有所有权限"""
    if not user.is_active:
        return False

    # 超级管理员拥有所有权限
    if Permission.SUPERADMIN in user.permissions:
        return True

    # 检查是否有所有权限
    return all(perm in user.permissions for perm in permissions)


def check_permission(permission: Union[str, List[str]], require_all: bool = False):
    """
    权限检查装饰器

    Args:
        permission: 单个权限或权限列表
        require_all: 是否需要拥有所有权限（False表示只需要其中一个）
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取当前用户
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break

            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未认证用户"
                )

            # 权限检查
            if isinstance(permission, str):
                # 单个权限检查
                if not has_permission(current_user, permission):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"需要权限: {permission}"
                    )
            else:
                # 多个权限检查
                permissions = list(permission)
                if require_all:
                    if not has_all_permissions(current_user, permissions):
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"需要所有权限: {', '.join(permissions)}"
                        )
                else:
                    if not has_any_permission(current_user, permissions):
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"需要以下任一权限: {', '.join(permissions)}"
                        )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


# 权限依赖注入
def require_permission(permission: Union[str, List[str]], require_all: bool = False):
    """权限检查依赖注入"""
    def permission_checker(current_user: User = Depends(get_current_active_user)):
        if isinstance(permission, str):
            if not has_permission(current_user, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"需要权限: {permission}"
                )
        else:
            permissions = list(permission)
            if require_all:
                if not has_all_permissions(current_user, permissions):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"需要所有权限: {', '.join(permissions)}"
                    )
            else:
                if not has_any_permission(current_user, permissions):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"需要以下任一权限: {', '.join(permissions)}"
                    )
        return current_user

    return permission_checker


# 常用权限检查依赖
RequireAdmin = require_permission(Permission.ADMIN)
RequireTenantManage = require_permission(Permission.TENANT_MANAGE)
RequireMessageSend = require_permission(Permission.MESSAGE_SEND)
RequireMediaUpload = require_permission(Permission.MEDIA_UPLOAD)
RequireCallbackHandle = require_permission(Permission.CALLBACK_HANDLE)
RequireRead = require_permission(Permission.READ)
RequireWrite = require_permission(Permission.WRITE)

# 多权限检查依赖
RequireManageUser = require_permission([Permission.USER_MANAGE, Permission.ADMIN], require_all=True)
RequireFullAccess = require_permission([Permission.READ, Permission.WRITE, Permission.DELETE], require_all=True)