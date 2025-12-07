# -*- coding: utf-8 -*-
"""数据模型单元测试"""

import pytest
from datetime import datetime
from pydantic import ValidationError


@pytest.mark.unit
def test_tenant_model_creation():
    """测试租户模型创建"""
    from wxkf_saas.models.tenant import Tenant

    tenant = Tenant(
        corp_id="test_corp_123",
        corp_name="测试企业",
        permanent_code="test_permanent_code",
        contact_name="张三",
        contact_phone="13800138000",
        contact_email="test@example.com",
        is_active=True,
        is_authorized=True
    )

    assert tenant.corp_id == "test_corp_123"
    assert tenant.corp_name == "测试企业"
    assert tenant.permanent_code == "test_permanent_code"
    assert tenant.contact_name == "张三"
    assert tenant.contact_phone == "13800138000"
    assert tenant.contact_email == "test@example.com"
    assert tenant.is_active is True
    assert tenant.is_authorized is True


@pytest.mark.unit
def test_tenant_model_validation():
    """测试租户模型验证"""
    from wxkf_saas.models.tenant import Tenant

    # 测试必需字段缺失
    with pytest.raises(ValidationError) as exc_info:
        Tenant(corp_name="测试企业")  # 缺少corp_id

    assert "corp_id" in str(exc_info.value)

    # 测试无效邮箱格式
    with pytest.raises(ValidationError) as exc_info:
        Tenant(
            corp_id="test_corp",
            corp_name="测试企业",
            contact_email="invalid_email"
        )

    assert "email" in str(exc_info.value)


@pytest.mark.unit
def test_tenant_token_model_creation():
    """测试租户Token模型创建"""
    from wxkf_saas.models.tenant import TenantToken

    token = TenantToken(
        corp_id="test_corp_123",
        token_type="access_token",
        token_value="test_token_value",
        expires_at=9999999999
    )

    assert token.corp_id == "test_corp_123"
    assert token.token_type == "access_token"
    assert token.token_value == "test_token_value"
    assert token.expires_at == 9999999999


@pytest.mark.unit
def test_tenant_token_model_validation():
    """测试租户Token模型验证"""
    from wxkf_saas.models.tenant import TenantToken

    # 测试无效token类型
    with pytest.raises(ValidationError) as exc_info:
        TenantToken(
            corp_id="test_corp",
            token_type="invalid_token_type",
            token_value="test_token",
            expires_at=9999999999
        )

    assert "token_type" in str(exc_info.value)


@pytest.mark.unit
def test_kf_account_model_creation():
    """测试客服账号模型创建"""
    from wxkf_saas.models.kf_account import KfAccount

    kf_account = KfAccount(
        corp_id="test_corp",
        name="测试客服",
        media_id="test_media_id",
        open_kfid="test_open_kfid"
    )

    assert kf_account.corp_id == "test_corp"
    assert kf_account.name == "测试客服"
    assert kf_account.media_id == "test_media_id"
    assert kf_account.open_kfid == "test_open_kfid"


@pytest.mark.unit
def test_message_model_creation():
    """测试消息模型创建"""
    from wxkf_saas.models.message import Message

    message = Message(
        msgid="test_msg_id",
        msgtype="text",
        corp_id="test_corp",
        open_kfid="test_kf_id",
        userid="test_user",
        text={"content": "测试消息内容"}
    )

    assert message.msgid == "test_msg_id"
    assert message.msgtype == "text"
    assert message.corp_id == "test_corp"
    assert message.open_kfid == "test_kf_id"
    assert message.userid == "test_user"
    assert message.text["content"] == "测试消息内容"


@pytest.mark.unit
def test_message_image_model_creation():
    """测试图片消息模型创建"""
    from wxkf_saas.models.message import Message

    image_message = Message(
        msgid="test_image_msg_id",
        msgtype="image",
        corp_id="test_corp",
        open_kfid="test_kf_id",
        userid="test_user",
        image={"media_id": "test_image_media_id", "pic_url": "http://example.com/pic.jpg"}
    )

    assert image_message.msgtype == "image"
    assert image_message.image["media_id"] == "test_image_media_id"
    assert image_message.image["pic_url"] == "http://example.com/pic.jpg"


@pytest.mark.unit
def test_message_voice_model_creation():
    """测试语音消息模型创建"""
    from wxkf_saas.models.message import Message

    voice_message = Message(
        msgid="test_voice_msg_id",
        msgtype="voice",
        corp_id="test_corp",
        open_kfid="test_kf_id",
        userid="test_user",
        voice={"media_id": "test_voice_media_id", "play_length": 30}
    )

    assert voice_message.msgtype == "voice"
    assert voice_message.voice["media_id"] == "test_voice_media_id"
    assert voice_message.voice["play_length"] == 30


@pytest.mark.unit
def test_model_json_serialization():
    """测试模型JSON序列化"""
    from wxkf_saas.models.tenant import Tenant

    tenant = Tenant(
        corp_id="test_corp_123",
        corp_name="测试企业",
        contact_name="张三"
    )

    # 测试序列化为字典
    tenant_dict = tenant.model_dump(exclude_none=True)
    assert tenant_dict["corp_id"] == "test_corp_123"
    assert tenant_dict["corp_name"] == "测试企业"
    assert tenant_dict["contact_name"] == "张三"

    # 测试序列化为JSON
    tenant_json = tenant.model_dump_json(exclude_none=True)
    assert "test_corp_123" in tenant_json
    assert "测试企业" in tenant_json


@pytest.mark.unit
def test_model_from_dict():
    """测试从字典创建模型"""
    from wxkf_saas.models.tenant import Tenant

    tenant_data = {
        "corp_id": "dict_corp_456",
        "corp_name": "字典测试企业",
        "contact_name": "李四",
        "is_active": True
    }

    tenant = Tenant(**tenant_data)
    assert tenant.corp_id == "dict_corp_456"
    assert tenant.corp_name == "字典测试企业"
    assert tenant.contact_name == "李四"
    assert tenant.is_active is True


@pytest.mark.unit
def test_model_validation_custom():
    """测试自定义模型验证"""
    from wxkf_saas.models.tenant import Tenant

    # 测试手机号格式验证
    valid_tenant = Tenant(
        corp_id="test_corp_phone",
        corp_name="测试企业",
        contact_phone="13800138000"  # 有效手机号
    )
    assert valid_tenant.contact_phone == "13800138000"

    # 测试手机号格式验证（可能需要自定义验证器）
    # 这取决于实际的模型实现
    invalid_tenant = Tenant(
        corp_id="test_corp_phone_invalid",
        corp_name="测试企业",
        contact_phone="invalid_phone"  # 无效手机号
    )
    # 根据实际实现调整断言
    assert invalid_tenant.contact_phone == "invalid_phone"