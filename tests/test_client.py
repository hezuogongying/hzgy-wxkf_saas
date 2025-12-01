# -*- coding: utf-8 -*-
"""客户端模块单元测试"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from datetime import datetime


@pytest.mark.unit
def test_client_initialization(test_config):
    """测试客户端初始化"""
    from wxkf_saas.core.client import WxKfSaasClient

    client = WxKfSaasClient(test_config)
    assert client.config == test_config
    assert client._http_client is not None


@pytest.mark.unit
def test_client_url_building(test_config):
    """测试客户端URL构建"""
    from wxkf_saas.core.client import WxKfSaasClient

    client = WxKfSaasClient(test_config)

    # 测试基础URL
    base_url = client._build_url("/test")
    assert base_url.endswith("/test")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_client_request_with_provider_token(test_config):
    """测试使用provider_token的请求"""
    from wxkf_saas.core.client import WxKfSaasClient

    client = WxKfSaasClient(test_config)

    # Mock HTTP客户端
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}

    client._http_client = AsyncMock()
    client._http_client.request.return_value = mock_response

    # Mock token manager
    with patch('wxkf_saas.core.token_manager.MultiTenantTokenManager') as mock_token_manager:
        mock_token_manager.return_value.get_token.return_value = "test_provider_token"

        result = await client._request(
            "POST",
            "/api/test",
            use_provider_token=True
        )

        assert result.errcode == 0
        assert result.errmsg == "ok"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_client_request_with_corp_id(test_config):
    """测试使用corp_id的请求"""
    from wxkf_saas.core.client import WxKfSaasClient

    client = WxKfSaasClient(test_config)

    # Mock HTTP客户端
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"errcode": 0, "errmsg": "ok", "data": {"id": "123"}}

    client._http_client = AsyncMock()
    client._http_client.request.return_value = mock_response

    # Mock token manager
    with patch('wxkf_saas.core.token_manager.MultiTenantTokenManager') as mock_token_manager:
        mock_token_manager.return_value.get_token.return_value = "test_access_token"

        from pydantic import BaseModel

        class TestResponse(BaseModel):
            errcode: int
            errmsg: str
            data: dict = None

        result = await client._request(
            "POST",
            "/api/test",
            corp_id="test_corp",
            response_model=TestResponse
        )

        assert result.errcode == 0
        assert result.data["id"] == "123"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_client_request_error_handling(test_config):
    """测试客户端请求错误处理"""
    from wxkf_saas.core.client import WxKfSaasClient
    from wxkf_saas.core.exceptions import WxKfApiError

    client = WxKfSaasClient(test_config)

    # Mock HTTP客户端 - API错误
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"errcode": 40001, "errmsg": "invalid credential"}

    client._http_client = AsyncMock()
    client._http_client.request.return_value = mock_response

    # Mock token manager
    with patch('wxkf_saas.core.token_manager.MultiTenantTokenManager') as mock_token_manager:
        mock_token_manager.return_value.get_token.return_value = "invalid_token"

        with pytest.raises(WxKfApiError) as exc_info:
            await client._request(
                "POST",
                "/api/test",
                use_provider_token=True
            )

        assert exc_info.value.errcode == 40001
        assert "invalid credential" in str(exc_info.value)


@pytest.mark.asyncio
@pytest.mark.unit
async def test_client_file_upload(test_config):
    """测试文件上传"""
    from wxkf_saas.core.client import WxKfSaasClient

    client = WxKfSaasClient(test_config)

    # Mock HTTP客户端
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"errcode": 0, "errmsg": "ok", "media_id": "test_media_id"}

    client._http_client = AsyncMock()
    client._http_client.request.return_value = mock_response

    # Mock token manager
    with patch('wxkf_saas.core.token_manager.MultiTenantTokenManager') as mock_token_manager:
        mock_token_manager.return_value.get_token.return_value = "test_access_token"

        # 模拟文件上传
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            result = await client._upload_file(
                "/media/upload",
                "test.jpg",
                corp_id="test_corp"
            )

            assert result.media_id == "test_media_id"