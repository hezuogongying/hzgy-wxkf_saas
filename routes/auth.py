# -*- coding: utf-8 -*-
"""认证相关路由"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from core.auth import AuthService, User, TokenData
from middleware.auth import get_current_user, get_current_active_user

router = APIRouter(prefix="/auth", tags=["认证"])

# OAuth2 scheme for token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# 请求模型
class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: dict


class RefreshTokenRequest(BaseModel):
    """刷新Token请求"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """刷新Token响应"""
    access_token: str
    token_type: str
    expires_in: int


class UserRegister(BaseModel):
    """用户注册"""
    username: str
    email: EmailStr
    password: str
    corp_id: str
    role: str = "user"


class UserInfo(BaseModel):
    """用户信息"""
    id: str
    username: str
    email: str
    corp_id: str
    role: str
    permissions: list
    is_active: bool
    created_at: datetime


# 模拟用户数据库
MOCK_USERS = {
    "admin": {
        "id": "admin",
        "username": "admin",
        "password": AuthService.get_password_hash("admin123"),
        "email": "admin@example.com",
        "corp_id": "ww4c543662478cf668",
        "role": "admin",
        "permissions": ["admin", "read", "write", "delete"],
        "is_active": True,
        "created_at": datetime.now()
    },
    "user1": {
        "id": "user1",
        "username": "user1",
        "password": AuthService.get_password_hash("user123"),
        "email": "user1@example.com",
        "corp_id": "ww4c543662478cf669",
        "role": "user",
        "permissions": ["read", "write"],
        "is_active": True,
        "created_at": datetime.now()
    }
}


# 模拟刷新Token存储
REFRESH_TOKENS = {}


@router.post("/login", response_model=LoginResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """用户登录"""
    # 验证用户
    user_data = MOCK_USERS.get(form_data.username)
    if not user_data or not AuthService.verify_password(form_data.password, user_data["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user_data["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )

    # 创建用户对象
    user = User(
        id=user_data["id"],
        username=user_data["username"],
        corp_id=user_data["corp_id"],
        role=user_data["role"],
        permissions=user_data["permissions"],
        is_active=user_data["is_active"]
    )

    # 创建Tokens
    tokens = AuthService.create_user_tokens(user)

    # 保存刷新Token
    REFRESH_TOKENS[tokens["refresh_token"]] = user.id

    return LoginResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        expires_in=tokens["expires_in"],
        user={
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "permissions": user.permissions,
            "corp_id": user.corp_id
        }
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(request_data: RefreshTokenRequest):
    """刷新访问令牌"""
    refresh_token = request_data.refresh_token

    # 验证刷新Token
    user_id = REFRESH_TOKENS.get(refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌"
        )

    user_data = MOCK_USERS.get(user_id)
    if not user_data or not user_data["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已禁用"
        )

    # 创建新的访问令牌
    user = User(
        id=user_data["id"],
        username=user_data["username"],
        corp_id=user_data["corp_id"],
        role=user_data["role"],
        permissions=user_data["permissions"],
        is_active=user_data["is_active"]
    )

    access_token_expires = datetime.utcnow() + timedelta(minutes=60 * 24 * 7)
    access_token = AuthService.create_access_token(
        data={
            "sub": user.id,
            "corp_id": user.corp_id,
            "role": user.role,
            "permissions": user.permissions
        },
        expires_delta=access_token_expires - datetime.utcnow()
    )

    return RefreshTokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=int((access_token_expires - datetime.utcnow()).total_seconds())
    )


@router.post("/register", response_model=dict)
async def register(user_data: UserRegister):
    """用户注册"""
    # 检查用户是否已存在
    if user_data.username in MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # TODO: 验证corp_id是否有效

    # 创建用户（模拟）
    new_user = {
        "id": f"user_{datetime.now().timestamp()}",
        "username": user_data.username,
        "password": AuthService.get_password_hash(user_data.password),
        "email": user_data.email,
        "corp_id": user_data.corp_id,
        "role": user_data.role,
        "permissions": ["read"] if user_data.role == "user" else ["read", "write"],
        "is_active": True,
        "created_at": datetime.now()
    }

    MOCK_USERS[user_data.username] = new_user

    return {
        "message": "用户注册成功",
        "user_id": new_user["id"],
        "username": new_user["username"]
    }


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户信息"""
    user_data = MOCK_USERS.get(current_user.username)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return UserInfo(
        id=user_data["id"],
        username=user_data["username"],
        email=user_data["email"],
        corp_id=user_data["corp_id"],
        role=user_data["role"],
        permissions=user_data["permissions"],
        is_active=user_data["is_active"],
        created_at=user_data["created_at"]
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """用户登出"""
    # TODO: 将Token加入黑名单或删除
    return {"message": "登出成功"}


@router.get("/verify-token")
async def verify_token(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user)
):
    """验证Token有效性"""
    return {
        "valid": True,
        "user_id": current_user.id,
        "corp_id": current_user.corp_id,
        "role": current_user.role
    }