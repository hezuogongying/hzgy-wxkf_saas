#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JWT认证集成测试
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.auth import AuthService, User


def test_password_hashing():
    """测试密码哈希功能"""
    print("测试密码哈希功能...")

    # 测试正常长度密码
    password1 = "admin123"
    hash1 = AuthService.get_password_hash(password1)
    assert hash1 != password1, "密码哈希应该与原密码不同"
    assert AuthService.verify_password(password1, hash1), "应该能验证正确的密码"

    # 测试长密码（超过72字节）
    long_password = "a" * 100  # 100字节
    hash2 = AuthService.get_password_hash(long_password)
    assert AuthService.verify_password(long_password, hash2), "应该能验证长密码"

    print("✅ 密码哈希功能测试通过")


def test_token_creation():
    """测试Token创建功能"""
    print("\n测试Token创建功能...")

    # 创建测试用户
    user = User(
        id="test_user",
        username="testuser",
        corp_id="test_corp",
        role="user",
        permissions=["read", "write"],
        is_active=True
    )

    # 创建Tokens
    tokens = AuthService.create_user_tokens(user)

    assert "access_token" in tokens, "应该包含访问令牌"
    assert "refresh_token" in tokens, "应该包含刷新令牌"
    assert "token_type" in tokens, "应该包含令牌类型"
    assert "expires_in" in tokens, "应该包含过期时间"

    print(f"✅ Token创建成功")
    print(f"   访问令牌长度: {len(tokens['access_token'])}")
    print(f"   刷新令牌长度: {len(tokens['refresh_token'])}")
    print(f"   令牌类型: {tokens['token_type']}")
    print(f"   过期时间: {tokens['expires_in']}秒")

    return tokens


def test_token_verification(tokens):
    """测试Token验证功能"""
    print("\n测试Token验证功能...")

    # 验证访问令牌
    token_data = AuthService.verify_token(tokens["access_token"])

    assert token_data is not None, "访问令牌应该是有效的"
    assert token_data.user_id == "test_user", "用户ID应该正确"
    assert token_data.corp_id == "test_corp", "企业ID应该正确"
    assert token_data.role == "user", "角色应该正确"
    assert token_data.permissions == ["read", "write"], "权限应该正确"

    print("✅ 访问令牌验证通过")

    # 验证刷新令牌（应该返回None，因为它是刷新令牌）
    refresh_token_data = AuthService.verify_token(tokens["refresh_token"])
    assert refresh_token_data is None, "刷新令牌应该不被验证为访问令牌"
    print("✅ 刷新令牌类型正确")


def test_invalid_token():
    """测试无效Token"""
    print("\n测试无效Token处理...")

    invalid_token = "invalid.jwt.token"
    token_data = AuthService.verify_token(invalid_token)

    assert token_data is None, "无效Token应该返回None"
    print("✅ 无效Token正确处理")


def test_user_model():
    """测试用户模型"""
    print("\n测试用户模型...")

    user = User(
        id="user123",
        username="testuser",
        corp_id="corp123",
        role="admin",
        permissions=["read", "write", "delete"],
        is_active=True
    )

    assert user.id == "user123"
    assert user.username == "testuser"
    assert user.corp_id == "corp123"
    assert user.role == "admin"
    assert user.permissions == ["read", "write", "delete"]
    assert user.is_active is True

    print("✅ 用户模型测试通过")


def test_mock_users():
    """测试模拟用户数据"""
    print("\n测试模拟用户数据...")

    from core.mock_users import get_users, get_refresh_tokens

    # 获取用户数据
    users = get_users()

    assert "admin" in users, "应该包含admin用户"
    assert "user1" in users, "应该包含user1用户"

    # 检查admin用户
    admin_user = users["admin"]
    assert admin_user["username"] == "admin"
    assert admin_user["corp_id"] == "ww4c543662478cf668"
    assert admin_user["role"] == "admin"
    assert AuthService.verify_password("admin123", admin_user["password"])

    print("✅ 模拟用户数据测试通过")

    # 获取刷新令牌存储
    refresh_tokens = get_refresh_tokens()
    assert isinstance(refresh_tokens, dict), "刷新令牌存储应该是字典"
    print("✅ 刷新令牌存储测试通过")


def main():
    """主函数"""
    print("="*80)
    print("JWT认证集成测试")
    print("="*80)

    try:
        # 运行各项测试
        test_password_hashing()
        test_user_model()
        test_mock_users()

        # Token相关测试
        tokens = test_token_creation()
        test_token_verification(tokens)
        test_invalid_token()

        print("\n" + "="*80)
        print("🎉 所有JWT认证测试通过！")
        print("="*80)
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)