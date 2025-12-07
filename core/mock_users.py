# -*- coding: utf-8 -*-
"""模拟用户数据初始化"""

from datetime import datetime
from core.auth import AuthService, User


def get_mock_users():
    """获取模拟用户数据（延迟初始化）"""
    return {
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


# 全局变量，但不立即初始化
_MOCK_USERS = None
_REFRESH_TOKENS = {}


def get_users():
    """获取用户数据（单例模式）"""
    global _MOCK_USERS
    if _MOCK_USERS is None:
        _MOCK_USERS = get_mock_users()
    return _MOCK_USERS


def get_refresh_tokens():
    """获取刷新令牌存储"""
    return _REFRESH_TOKENS