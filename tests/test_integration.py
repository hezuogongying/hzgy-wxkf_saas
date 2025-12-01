# -*- coding: utf-8 -*-
"""集成测试"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
import json

from wxkf_saas.core.client import WxKfSaasClient
from wxkf_saas.models.tenant import Tenant, TenantToken


@pytest.mark.asyncio
async def test_full_api_workflow(test_config):
    """测试完整的API工作流程"""
    from wxkf_saas.core.database import get_async_db
    from wxkf_saas.core.token_manager import MultiTenantTokenManager

    async with get_async_db() as session:
        # 创建测试租户
        tenant = Tenant(
            corp_id="test_corp_001",
            corp_name="测试企业001",
            permanent_code="test_perm_code_001",
            contact_name="测试联系人001",
            contact_phone="13800138001",
            contact_email="test001@example.com",
            is_active=True,
            is_authorized=True
        )
        session.add(tenant)
        await session.commit()

        # 创建客户端
        client = WxKfSaasClient(test_config)
        token_manager = MultiTenantTokenManager(test_config)

        # 测试客服账号创建
        with patch('wxkf_saas.api.kf_account.KfAccountApi.add') as mock_add:
            mock_add.return_value = AsyncMock()
            mock_add.return_value.open_kfid = "test_kf_001"
            mock_add.return_value.errcode = 0
            mock_add.return_value.errmsg = "ok"
            mock_add.return_value.request_id = "test_req_001"

            result = await client.kf_account.add(
                corp_id="test_corp_001",
                name="测试客服001",
                media_id="test_media_001"
            )

            assert result.open_kfid == "test_kf_001"
            assert result.errcode == 0
            assert result.request_id == "test_req_001"

        # 测试消息发送
        with patch('wxkf_saas.api.message.MessageApi.send_text') as mock_send:
            mock_send.return_value = AsyncMock()
            mock_send.return_value.msgid = "test_msg_001"
            mock_send.return_value.errcode = 0
            mock_send.return_value.errmsg = "ok"
            mock_send.return_value.request_id = "test_req_002"

            result = await client.message.send_text(
                corp_id="test_corp_001",
                touser="test_user_001",
                content="测试消息内容"
            )

            assert result.msgid == "test_msg_001"
            assert result.errcode == 0
            assert result.request_id == "test_req_002"

        # 验证Token创建和管理
        access_token = await token_manager.get_access_token("test_corp_001")
        assert access_token is not None
        assert isinstance(access_token, str)

        provider_token = await token_manager.get_provider_token()
        assert provider_token is not None
        assert isinstance(provider_token, str)


@pytest.mark.asyncio
async def test_database_operations(test_database):
    """测试数据库操作的集成"""
    from wxkf_saas.models.tenant import Tenant

    async with test_database['async_session']() as session:
        # 测试批量插入
        tenants = [
            Tenant(
                corp_id=f"test_corp_{str(i).zfill(3)}",
                corp_name=f"测试企业{str(i).zfill(3)}",
                permanent_code=f"test_code_{str(i)}",
                is_active=True
            ) for i in range(10)
        ]

        session.add_all(tenants)
        await session.commit()

        # 验证批量插入
        result = await session.execute(
            "SELECT COUNT(*) FROM tenants WHERE corp_id LIKE 'test_corp%'"
        )
        assert result.scalar() == 10

        # 测试复杂查询
        result = await session.execute("""
            SELECT corp_name, COUNT(*) as tenant_count
            FROM tenants
            WHERE corp_name LIKE '测试企业%'
            GROUP BY corp_name
            ORDER BY tenant_count DESC
            LIMIT 5
        """)
        rows = result.fetchall()
        assert len(rows) <= 5
        for row in rows:
            assert 'tenant_count' in row and row['tenant_count'] > 0


@pytest.mark.asyncio
async def test_token_management_integration():
    """测试Token管理的集成"""
    from wxkf_saas.core.token_manager import MultiTenantTokenManager

    token_manager = MultiTenantTokenManager(test_config)

    # 测试多个租户Token同时管理
    test_corps = ["test_corp_001", "test_corp_002", "test_corp_003"]

    async def get_tokens_for_corps():
        tasks = []
        for corp_id in test_corps:
            access_token = await token_manager.get_access_token(corp_id)
            if access_token:
                tasks.append(access_token)
        return await asyncio.gather(*tasks)

    # 并发获取多个租户的Token
    tokens = await get_tokens_for_corps()
    assert len(tokens) == 3


@pytest.mark.asyncio
async def test_error_scenarios():
    """测试错误场景"""
    from wxkf_saas.core.exceptions import TenantNotFoundError, TenantNotAuthorizedError
    from wxkf_saas.core.client import WxKfSaasClient

    client = WxKfSaasClient(test_config)

    # 测试租户不存在错误
    with patch('wxkf_saas.core.database.get_db_manager') as mock_get_db:
        mock_get_db.side_effect = RuntimeError("Database not initialized")

        with pytest.raises(RuntimeError):
            await client.kf_account.add(
                corp_id="nonexistent_corp",
                name="测试客服"
            )

    # 测试租户未授权错误
    with patch.object(client, '_get_access_token', return_value=None):
        with pytest.raises(TenantNotAuthorizedError) as exc_info:
            await client.message.send_text(
                corp_id="unauthorized_corp",
                content="测试消息"
            )

        assert "unauthorized_corp" in str(exc_info.value)


@pytest.mark.asyncio
async def test_concurrent_requests():
    """测试并发请求"""
    from wxkf_saas.core.client import WxKfSaasClient

    client = WxKfSaasClient(test_config)

    async def send_messages(corp_id, count):
        tasks = []
        for i in range(count):
            task = client.message.send_text(
                corp_id=corp_id,
                touser=f"test_user_{str(i)}",
                content=f"测试消息 {str(i)}"
            )
            tasks.append(task)
        return await asyncio.gather(*tasks)

    # 并发发送多条消息
    results = await send_messages("test_concurrent_corp", 5)
    assert len(results) == 5
    assert all(hasattr(r, 'errcode') and r.errcode == 0 for r in results)


def test_api_response_format():
    """测试API响应格式"""
    from wxkf_saas.models.kf_account import KfAccountResponse
    from wxkf_saas.models.message import MessageListResponse, MessageResponse
    from wxkf_saas.models.media import MediaUploadResponse, MediaDownloadResponse

    # 测试客服账号响应
    kf_data = {
        "errcode": 0,
        "errmsg": "ok",
        "open_kfid": "test_kf"
    }
    kf_response = KfAccountResponse(**kf_data)

    assert kf_response.errcode == 0
    assert kf_response.errmsg == "ok"
    assert kf_response.open_kfid == "test_kf"
    assert kf_response.model_dump(exclude_none=True) == kf_data

    # 测试消息列表响应
    msg_list_data = {
        "errcode": 0,
        "errmsg": "ok",
        "message": [
            {
                "msgid": "test_msg_001",
                "msgid": "test_msg_002"
            }
        ]
    }
    msg_list_response = MessageListResponse(**msg_list_data)

    assert msg_list_response.errcode == 0
    assert msg_list_response.has_more is False
    assert len(msg_list_response.message) == 2

    # 测试消息响应
    msg_data = {
        "errcode": 0,
        "errmsg": "ok",
        "msgid": "test_msg_001"
    }
    msg_response = MessageResponse(**msg_data)

    assert msg_response.errcode == 0
    assert msg_response.msgid == "test_msg_001"

    # 测试素材上传响应
    upload_data = {
        "errcode": 0,
        "errmsg": "ok",
        "media_id": "test_media_001",
        "url": "https://test.com/media.jpg"
    }
    upload_response = MediaUploadResponse(**upload_data)

    assert upload_response.errcode == 0
    assert upload_response.media_id == "test_media_001"
    assert "url" in upload_response.url