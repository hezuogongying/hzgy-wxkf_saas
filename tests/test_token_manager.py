# -*- coding: utf-8 -*-
"""Token管理器单元测试"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import time
from datetime import datetime, timedelta


@pytest.mark.unit
def test_token_manager_initialization(test_config, mock_db_session):
    """测试Token管理器初始化"""
    from wxkf_saas.core.token_manager import MultiTenantTokenManager

    manager = MultiTenantTokenManager(test_config, mock_db_session)
    assert manager.config == test_config


@pytest.mark.asyncio
@pytest.mark.unit
async def test_provider_token_storage(test_database):
    """测试provider_token存储"""
    from wxkf_saas.core.token_manager import MultiTenantTokenManager
    from wxkf_saas.models.tenant import TenantToken

    config = test_database['config']
    manager = MultiTenantTokenManager(config)

    async with test_database['async_session']() as session:
        manager.session = session

        # 存储provider_token
        expires_at = int(time.time()) + 7200  # 2小时后过期
        token = TenantToken(
            corp_id="_provider_",
            token_type="provider_access_token",
            token_value="test_provider_token",
            expires_at=expires_at
        )

        session.add(token)
        await session.commit()

        # 检索token
        result = await manager.get_token("_provider_", "provider_access_token")
        assert result == "test_provider_token"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_suite_token_storage(test_database):
    """测试suite_token存储"""
    from wxkf_saas.core.token_manager import MultiTenantTokenManager
    from wxkf_saas.models.tenant import TenantToken

    config = test_database['config']
    manager = MultiTenantTokenManager(config)

    async with test_database['async_session']() as session:
        manager.session = session

        # 存储suite_token
        expires_at = int(time.time()) + 3600  # 1小时后过期
        token = TenantToken(
            corp_id="_suite_",
            token_type="suite_access_token",
            token_value="test_suite_token",
            expires_at=expires_at
        )

        session.add(token)
        await session.commit()

        # 检索token
        result = await manager.get_token("_suite_", "suite_access_token")
        assert result == "test_suite_token"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_tenant_token_storage(test_database):
    """测试租户token存储"""
    from wxkf_saas.core.token_manager import MultiTenantTokenManager
    from wxkf_saas.models.tenant import TenantToken

    config = test_database['config']
    manager = MultiTenantTokenManager(config)

    async with test_database['async_session']() as session:
        manager.session = session

        # 存储租户token
        corp_id = "test_corp_123"
        expires_at = int(time.time()) + 7200  # 2小时后过期
        token = TenantToken(
            corp_id=corp_id,
            token_type="access_token",
            token_value="test_access_token",
            expires_at=expires_at
        )

        session.add(token)
        await session.commit()

        # 检索token
        result = await manager.get_token(corp_id, "access_token")
        assert result == "test_access_token"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_token_expiration_handling(test_database):
    """测试token过期处理"""
    from wxkf_saas.core.token_manager import MultiTenantTokenManager
    from wxkf_saas.models.tenant import TenantToken
    from wxkf_saas.core.exceptions import TokenExpiredError

    config = test_database['config']
    manager = MultiTenantTokenManager(config)

    async with test_database['async_session']() as session:
        manager.session = session

        # 存储已过期的token
        expires_at = int(time.time()) - 3600  # 1小时前就过期了
        token = TenantToken(
            corp_id="test_corp_expired",
            token_type="access_token",
            token_value="expired_token",
            expires_at=expires_at
        )

        session.add(token)
        await session.commit()

        # 尝试检索过期token应该返回None
        result = await manager.get_token("test_corp_expired", "access_token")
        assert result is None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_token_auto_refresh(test_database):
    """测试token自动刷新"""
    from wxkf_saas.core.token_manager import MultiTenantTokenManager
    from wxkf_saas.models.tenant import TenantToken

    config = test_database['config']
    manager = MultiTenantTokenManager(config)

    # Mock HTTP客户端用于刷新token
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "errcode": 0,
        "errmsg": "ok",
        "provider_access_token": "new_provider_token",
        "expires_in": 7200
    }

    manager._http_client = AsyncMock()
    manager._http_client.post.return_value = mock_response

    async with test_database['async_session']() as session:
        manager.session = session

        # 存储即将过期的token
        expires_at = int(time.time()) + 30  # 30秒后过期（触发刷新）
        token = TenantToken(
            corp_id="_provider_",
            token_type="provider_access_token",
            token_value="old_provider_token",
            expires_at=expires_at
        )

        session.add(token)
        await session.commit()

        # Mock provider token refresh
        with patch.object(manager, '_refresh_provider_token', new_callable=AsyncMock) as mock_refresh:
            mock_refresh.return_value = "new_provider_token"

            result = await manager.get_token("_provider_", "provider_access_token")
            assert result == "new_provider_token"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_redis_token_caching(mock_db_session):
    """测试Redis token缓存"""
    from wxkf_saas.core.token_manager import MultiTenantTokenManager

    config = MagicMock()
    config.redis_host = "localhost"
    config.redis_port = 6379
    config.redis_db = 1
    config.redis_key_prefix = "test:"

    # Mock Redis客户端
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.setex.return_value = True

    manager = MultiTenantTokenManager(config, mock_db_session)
    manager._redis_client = mock_redis

    # 测试缓存未命中
    result = await manager._get_cached_token("test_corp", "access_token")
    assert result is None

    # 测试设置缓存
    await manager._set_cached_token("test_corp", "access_token", "test_token", 7200)
    mock_redis.setex.assert_called_once()

    # 测试缓存命中
    mock_redis.get.return_value = "test_token"
    result = await manager._get_cached_token("test_corp", "access_token")
    assert result == "test_token"