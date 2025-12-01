# -*- coding: utf-8 -*-
"""API模块单元测试"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import pytest_asyncio
import json
from datetime import datetime


def test_client_initialization(test_config):
    """测试客户端初始化"""
    from wxkf_saas.core.client import WxKfSaasClient
    from wxkf_saas.api.kf_account import KfAccountApi
    from wxkf_saas.api.message import MessageApi
    from wxkf_saas.api.media import MediaApi

    client = WxKfSaasClient(test_config)

    assert client.config == test_config
    assert isinstance(client.kf_account, KfAccountApi)
    assert isinstance(client.message, MessageApi)
    assert isinstance(client.media, MediaApi)


@pytest.mark.asyncio
async def test_kf_account_api():
    """测试客服账号API"""
    from wxkf_saas.api.kf_account import KfAccountApi
    from wxkf_saas.models.kf_account import KfAccount

    # 模拟客户端
    mock_client = AsyncMock()
    kf_api = KfAccountApi(mock_client)

    # 测试添加客服账号
    mock_response = AsyncMock()
    mock_response.open_kfid = "test_kf_id"
    mock_response.request_id = "test_request_id"

    mock_client._request.return_value = mock_response

    with patch('wxkf_saas.api.kf_account.KfAccountApi.add') as mock_add:
        mock_add.return_value = mock_response

        result = await kf_api.add(
            corp_id="test_corp",
            name="测试客服",
            media_id="test_media"
        )

        mock_add.assert_called_once_with(
            corp_id="test_corp",
            name="测试客服",
            media_id="test_media"
        )
        assert result.open_kfid == "test_kf_id"
        assert result.request_id == "test_request_id"


@pytest.mark.asyncio
async def test_message_api():
    """测试消息API"""
    from wxkf_saas.api.message import MessageApi

    mock_client = AsyncMock()
    msg_api = MessageApi(mock_client)

    # 测试发送文本消息
    mock_response = AsyncMock()
    mock_response.msgid = "test_msg_id"
    mock_response.request_id = "test_msg_request_id"

    mock_client._request.return_value = mock_response

    with patch('wxkf_saas.api.message.MessageApi.send_text') as mock_send:
        mock_send.return_value = mock_response

        result = await msg_api.send_text(
            corp_id="test_corp",
            touser="test_user",
            content="测试消息"
        )

        mock_send.assert_called_once_with(
            corp_id="test_corp",
            touser="test_user",
            content="测试消息"
        )
        assert result.msgid == "test_msg_id"
        assert result.request_id == "test_msg_request_id"

    # 测试同步消息
    with patch('wxkf_saas.api.message.MessageApi.sync_msg') as mock_sync:
        mock_response = AsyncMock()
        mock_response.msg_list = []
        mock_response.has_more = False
        mock_response.next_cursor = ""

        mock_sync.return_value = mock_response

        result = await msg_api.sync_msg(
            corp_id="test_corp",
            limit=100
        )

        mock_sync.assert_called_once_with(
            corp_id="test_corp",
            limit=100,
            cursor=""
        )
        assert result.msg_list == []
        assert not result.has_more
        assert result.next_cursor == ""


@pytest.mark.asyncio
async def test_media_api():
    """测试素材API"""
    from wxkf_saas.api.media import MediaApi

    mock_client = AsyncMock()
    media_api = MediaApi(mock_client)

    # 测试上传图片
    mock_response = AsyncMock()
    mock_response.media_id = "test_media_id"
    mock_response.url = "https://test.com/media.jpg"
    mock_response.created_at = datetime.now()

    mock_client._request.return_value = mock_response

    with patch('wxkf_saas.api.media.MediaApi.upload') as mock_upload:
        mock_upload.return_value = mock_response

        result = await media_api.upload(
            corp_id="test_corp",
            media_type="image",
            file_path="/path/to/test.jpg"
        )

        mock_upload.assert_called_once_with(
            corp_id="test_corp",
            media_type="image",
            file_path="/path/to/test.jpg"
        )
        assert result.media_id == "test_media_id"
        assert result.url == "https://test.com/media.jpg"

    # 测试下载素材
    with patch('wxkf_saas.api.media.MediaApi.download') as mock_download:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "image/jpeg"}
        mock_response.content = b"fake_image_data"

        mock_download.return_value = mock_response

        result = await media_api.download(
            corp_id="test_corp",
            media_id="test_media",
            save_path="/path/to/save.jpg"
        )

        mock_download.assert_called_once_with(
            corp_id="test_corp",
            media_id="test_media",
            save_path="/path/to/save.jpg"
        )
        assert result.status_code == 200
        assert result.content == b"fake_image_data"


def test_api_response_models():
    """测试API响应模型"""
    from wxkf_saas.models.kf_account import KfAccountResponse
    from wxkf_saas.models.message import MessageListResponse, MessageResponse
    from wxkf_saas.models.media import MediaUploadResponse, MediaDownloadResponse

    # 测试响应模型验证
    response_data = {
        "errcode": 0,
        "errmsg": "ok",
        "open_kfid": "test_kf_id"
    }

    # 验证客服账号响应
    kf_response = KfAccountResponse(**response_data)
    assert kf_response.errcode == 0
    assert kf_response.errmsg == "ok"
    assert kf_response.open_kfid == "test_kf_id"

    # 验证消息列表响应
    msg_list_response = MessageListResponse(**response_data, has_more=False, next_cursor="")
    assert msg_list_response.errcode == 0
    assert msg_list_response.has_more is False

    # 验证消息响应
    msg_response = MessageResponse(**response_data, msgid="test_msg_id")
    assert msg_response.errcode == 0
    assert msg_response.msgid == "test_msg_id"

    # 验证素材上传响应
    upload_response = MediaUploadResponse(**response_data, media_id="test_media_id")
    assert upload_response.errcode == 0
    assert upload_response.media_id == "test_media_id"


def test_error_handling():
    """测试错误处理"""
    from wxkf_saas.core.exceptions import WxKfApiError, TenantNotFoundError
    from wxkf_saas.core.client import WxKfSaasClient

    # 模拟微信API错误
    api_error_response = {
        "errcode": 40001,
        "errmsg": "invalid corp_id"
    }

    client = WxKfSaasClient(test_config)

    with patch('wxkf_saas.core.client.WxKfSaasClient._request') as mock_request:
        mock_request.return_value = api_error_response

        with pytest.raises(WxKfApiError) as exc_info:
            await client.kf_account.add(
                corp_id="invalid_corp",
                name="测试客服"
            )

        assert exc_info.value.errcode == 40001
        assert exc_info.value.errmsg == "invalid corp_id"
        assert "invalid corp_id" in str(exc_info.value)

    # 测试租户未找到错误
    with patch('wxkf_saas.core.database.get_db_manager') as mock_get_db:
        mock_get_db.side_effect = RuntimeError("Database not initialized")

        with pytest.raises(RuntimeError) as exc_info:
            await client.kf_account.add(corp_id="test_corp", name="测试客服")

        assert "Database not initialized" in str(exc_info.value)


def test_api_client_methods():
    """测试客户端方法"""
    from wxkf_saas.core.client import WxKfSaasClient
    from wxkf_saas.core.config import WxKfSaasConfig

    config = WxKfSaasConfig(
        SUITE_ID="test_suite",
        SUITE_SECRET="test_secret",
        PROVIDER_SECRET="test_provider",
        PROVIDER_TOKEN="test_token",
        PROVIDER_ENCODING_AES_KEY="test_key"
        DB_TYPE="mysql",
        DB_HOST="localhost",
        DB_PORT=3306,
        DB_NAME="test_db",
        DB_USER="test_user",
        DB_PASSWORD="test_pass"
    )

    client = WxKfSaasClient(config)

    # 测试方法存在性
    assert hasattr(client, 'kf_account')
    assert hasattr(client, 'message')
    assert hasattr(client, 'media')
    assert hasattr(client, '_request')
    assert hasattr(client, '_request_async')

    # 测试方法类型
    from wxkf_saas.api.kf_account import KfAccountApi
    from wxkf_saas.api.message import MessageApi
    from wxkf_saas.api.media import MediaApi

    assert isinstance(client.kf_account, KfAccountApi)
    assert isinstance(client.message, MessageApi)
    assert isinstance(client.media, MediaApi)

    # 测试客户端配置
    assert client.config == config