# -*- coding: utf-8 -*-
"""JWT认证和权限管理"""

import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi import HTTPException, status

from core.config import WxKfSaasConfig


# JWT配置
JWT_SECRET_KEY = secrets.token_urlsafe(32)  # 生产环境应该从环境变量读取
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天
REFRESH_TOKEN_EXPIRE_DAYS = 30

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenPayload(BaseModel):
    """JWT载荷"""
    sub: str  # 用户ID
    corp_id: str  # 租户ID
    role: str  # 角色
    permissions: list = []  # 权限列表
    exp: int  # 过期时间
    iat: int  # 签发时间


class TokenData(BaseModel):
    """Token数据"""
    user_id: str
    corp_id: str
    role: str
    permissions: list


class User(BaseModel):
    """用户模型"""
    id: str
    username: str
    corp_id: str
    role: str
    permissions: list
    is_active: bool = True


class AuthService:
    """认证服务"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """生成密码哈希"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})

        return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """创建刷新令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({
            "exp": expire,
            "type": "refresh"
        })

        return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """验证令牌"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

            # 检查是否是刷新令牌
            if payload.get("type") == "refresh":
                return None

            user_id: str = payload.get("sub")
            corp_id: str = payload.get("corp_id")
            role: str = payload.get("role", "user")
            permissions: list = payload.get("permissions", [])

            if user_id is None or corp_id is None:
                return None

            token_data = TokenData(
                user_id=user_id,
                corp_id=corp_id,
                role=role,
                permissions=permissions
            )

            return token_data

        except jwt.PyJWTError:
            return None

    @staticmethod
    def create_user_tokens(user: User) -> Dict[str, str]:
        """为用户创建访问令牌和刷新令牌"""
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={
                "sub": user.id,
                "corp_id": user.corp_id,
                "role": user.role,
                "permissions": user.permissions
            },
            expires_delta=access_token_expires
        )

        refresh_token = AuthService.create_refresh_token(
            data={
                "sub": user.id,
                "corp_id": user.corp_id
            }
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds())
        }


class PermissionChecker:
    """权限检查器"""

    def __init__(self, required_permissions: list):
        self.required_permissions = required_permissions

    def __call__(self, user: User) -> bool:
        """检查用户是否有所需权限"""
        if not user.is_active:
            return False

        # 超级管理员有所有权限
        if "admin" in user.permissions or "superadmin" in user.permissions:
            return True

        # 检查是否拥有所有必需权限
        user_permissions = set(user.permissions)
        required_permissions = set(self.required_permissions)

        return required_permissions.issubset(user_permissions)


def require_permission(permissions: list):
    """权限检查装饰器工厂"""
    return PermissionChecker(permissions)