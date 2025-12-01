# -*- coding: utf-8 -*-
"""回调消息处理测试"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from core.crypto import WxKfCrypto
from core.callback_handler import CallbackHandler
from models.callback import CallbackProcessResult


class TestCallbackHandler:
    """回调处理器测试类"""

    @pytest.fixture
    def crypto_instance(self):
        """创建加密工具实例"""
        # 使用测试用的加密密钥
        token = "test_token"
        encoding_aes_key = "4jpk9t1dbimt2qg66wsl75d2w3me5zpmvle47xptpz9iaj3bq" + "=" * 4
        corp_id = "test_corp_id"
        return WxKfCrypto(token, encoding_aes_key, corp_id)

    @pytest.fixture
    def callback_handler(self, crypto_instance):
        """创建回调处理器实例"""
        return CallbackHandler(crypto_instance)

    @pytest.fixture
    def sample_text_xml(self):
        """示例文本消息XML"""
        return """<xml>
    <ToUserName><![CDATA[toUser]]></ToUserName>
    <FromUserName><![CDATA[fromUser]]></FromUserName>
    <CreateTime>1348831860</CreateTime>
    <MsgType><![CDATA[text]]></MsgType>
    <Content><![CDATA[this is a test]]></Content>
    <MsgId>1234567890123456</MsgId>
    <AgentID>1</AgentID>
</xml>"""

    @pytest.fixture
    def sample_image_xml(self):
        """示例图片消息XML"""
        return """<xml>
    <ToUserName><![CDATA[toUser]]></ToUserName>
    <FromUserName><![CDATA[fromUser]]></FromUserName>
    <CreateTime>1348831860</CreateTime>
    <MsgType><![CDATA[image]]></MsgType>
    <PicUrl><![CDATA[this is a url]]></PicUrl>
    <MediaId><![CDATA[media_id]]></MediaId>
    <MsgId>1234567890123456</MsgId>
    <AgentID>1</AgentID>
</xml>"""

    @pytest.fixture
    def sample_event_xml(self):
        """示例事件消息XML"""
        return """<xml>
    <ToUserName><![CDATA[toUser]]></ToUserName>
    <FromUserName><![CDATA[fromUser]]></FromUserName>
    <CreateTime>1348831860</CreateTime>
    <MsgType><![CDATA[event]]></MsgType>
    <Event><![CDATA[enter_session]]></Event>
    <OpenKfId><![CDATA[kf001@abc]]></OpenKfId>
    <WelcomeCode><![CDATA[welcome_code_123]]></WelcomeCode>
    <Scene><![CDATA[1]]></Scene>
</xml>"""

    @pytest.fixture
    def sample_suite_ticket_xml(self):
        """示例suite_ticket事件XML"""
        return """<xml>
    <SuiteId><![CDATA[wx3c6e8d49a9b7d5b4]]></SuiteId>
    <InfoType><![CDATA[suite_ticket]]></InfoType>
    <TimeStamp>1403610513</TimeStamp>
    <SuiteTicket><![CDATA[asdfasdfasdfasdfasdf]]></SuiteTicket>
</xml>"""

    @pytest.mark.asyncio
    async def test_decrypt_message_success(self, crypto_instance, sample_text_xml):
        """测试消息解密成功"""
        # 先加密消息
        encrypted_msg, timestamp, nonce = crypto_instance.encrypt_msg(sample_text_xml)

        # 计算签名
        signature = crypto_instance.get_sha1(
            crypto_instance.token, timestamp, nonce, encrypted_msg
        )

        # 解密消息
        decrypted_msg, msgid = crypto_instance.decrypt_msg(
            encrypted_msg, signature, timestamp, nonce
        )

        assert decrypted_msg == sample_text_xml
        assert msgid == 1234567890123456

    @pytest.mark.asyncio
    async def test_decrypt_message_invalid_signature(self, crypto_instance, sample_text_xml):
        """测试消息解密 - 签名验证失败"""
        encrypted_msg, timestamp, nonce = crypto_instance.encrypt_msg(sample_text_xml)

        # 使用错误的签名
        wrong_signature = "wrong_signature"

        with pytest.raises(ValueError, match="签名验证失败"):
            crypto_instance.decrypt_msg(encrypted_msg, wrong_signature, timestamp, nonce)

    @pytest.mark.asyncio
    async def test_process_text_message(self, callback_handler, sample_text_xml):
        """测试处理文本消息"""
        # 加密文本消息
        encrypted_msg, timestamp, nonce = callback_handler.crypto.encrypt_msg(sample_text_xml)

        # 计算签名
        signature = callback_handler.crypto.get_sha1(
            callback_handler.crypto.token, timestamp, nonce, encrypted_msg
        )

        # 处理回调消息
        result = await callback_handler.process_callback_message(
            encrypted_msg, signature, timestamp, nonce
        )

        assert isinstance(result, CallbackProcessResult)
        assert result.success is True
        assert result.message == "文本消息处理成功"
        assert result.event_type == 'text'
        assert result.msgid == "1234567890123456"

    @pytest.mark.asyncio
    async def test_process_image_message(self, callback_handler, sample_image_xml):
        """测试处理图片消息"""
        # 加密图片消息
        encrypted_msg, timestamp, nonce = callback_handler.crypto.encrypt_msg(sample_image_xml)

        # 计算签名
        signature = callback_handler.crypto.get_sha1(
            callback_handler.crypto.token, timestamp, nonce, encrypted_msg
        )

        # 处理回调消息
        result = await callback_handler.process_callback_message(
            encrypted_msg, signature, timestamp, nonce
        )

        assert isinstance(result, CallbackProcessResult)
        assert result.success is True
        assert result.message == "图片消息处理成功"
        assert result.event_type == 'image'

    @pytest.mark.asyncio
    async def test_process_enter_session_event(self, callback_handler, sample_event_xml):
        """测试处理用户进入会话事件"""
        # 加密事件消息
        encrypted_msg, timestamp, nonce = callback_handler.crypto.encrypt_msg(sample_event_xml)

        # 计算签名
        signature = callback_handler.crypto.get_sha1(
            callback_handler.crypto.token, timestamp, nonce, encrypted_msg
        )

        # 处理回调消息
        result = await callback_handler.process_callback_message(
            encrypted_msg, signature, timestamp, nonce
        )

        assert isinstance(result, CallbackProcessResult)
        assert result.success is True
        assert result.message == "用户进入会话事件处理成功"
        assert result.event_type == 'enter_session'

    @pytest.mark.asyncio
    async def test_process_suite_ticket_event(self, callback_handler, sample_suite_ticket_xml):
        """测试处理suite_ticket事件"""
        # 加密suite_ticket消息
        encrypted_msg, timestamp, nonce = callback_handler.crypto.encrypt_msg(sample_suite_ticket_xml)

        # 计算签名
        signature = callback_handler.crypto.get_sha1(
            callback_handler.crypto.token, timestamp, nonce, encrypted_msg
        )

        # 处理回调消息
        result = await callback_handler.process_callback_message(
            encrypted_msg, signature, timestamp, nonce
        )

        assert isinstance(result, CallbackProcessResult)
        assert result.success is True
        assert result.message == "suite_ticket推送事件处理成功"
        assert result.event_type == 'suite_ticket'

    @pytest.mark.asyncio
    async def test_process_empty_message(self, callback_handler):
        """测试处理空消息"""
        result = await callback_handler.process_callback_message(
            "", "signature", "timestamp", "nonce"
        )

        assert isinstance(result, CallbackProcessResult)
        assert result.success is False
        assert "签名验证失败" in result.message or "处理失败" in result.message

    @pytest.mark.asyncio
    async def test_process_invalid_xml(self, callback_handler):
        """测试处理无效XML消息"""
        invalid_xml = "<invalid><xml>"

        # 加密无效XML
        encrypted_msg, timestamp, nonce = callback_handler.crypto.encrypt_msg(invalid_xml)

        # 计算签名
        signature = callback_handler.crypto.get_sha1(
            callback_handler.crypto.token, timestamp, nonce, encrypted_msg
        )

        # 处理回调消息
        result = await callback_handler.process_callback_message(
            encrypted_msg, signature, timestamp, nonce
        )

        assert isinstance(result, CallbackProcessResult)
        assert result.success is False
        assert "XML" in result.message or "解析" in result.message

    def test_safe_int_conversion(self, callback_handler):
        """测试安全整数转换"""
        # 测试正常转换
        assert callback_handler._safe_int("123") == 123
        assert callback_handler._safe_int("456") == 456

        # 测试None值
        assert callback_handler._safe_int(None) is None

        # 测试无效值
        assert callback_handler._safe_int("invalid") is None
        assert callback_handler._safe_int("") is None

    def test_parse_wechat_channels(self, callback_handler):
        """测试视频号信息解析"""
        # 测试有效JSON
        valid_json = '{"name": "test", "id": "123"}'
        result = callback_handler._parse_wechat_channels(valid_json)
        assert result == {"name": "test", "id": "123"}

        # 测试空值
        assert callback_handler._parse_wechat_channels("") is None
        assert callback_handler._parse_wechat_channels(None) is None

        # 测试无效JSON
        invalid_json = '{"invalid json"'
        assert callback_handler._parse_wechat_channels(invalid_json) is None

    @pytest.mark.asyncio
    async def test_save_message_to_db_mock(self, callback_handler):
        """测试保存消息到数据库（使用mock）"""
        message_data = {
            "msgid": "123",
            "content": "test message",
            "fromuser": "test_user"
        }

        # 由于数据库操作是TODO状态，我们只测试不会抛出异常
        try:
            await callback_handler._save_message_to_db(message_data, "text")
        except Exception as e:
            pytest.fail(f"保存消息到数据库不应该抛出异常: {str(e)}")

    @pytest.mark.asyncio
    async def test_save_event_to_db_mock(self, callback_handler):
        """测试保存事件到数据库（使用mock）"""
        event_data = {
            "event": "enter_session",
            "fromuser": "test_user",
            "open_kfid": "kf001"
        }

        # 由于数据库操作是TODO状态，我们只测试不会抛出异常
        try:
            await callback_handler._save_event_to_db(event_data, "enter_session")
        except Exception as e:
            pytest.fail(f"保存事件到数据库不应该抛出异常: {str(e)}")


class TestCallbackCrypto:
    """加密工具测试类"""

    @pytest.fixture
    def crypto_instance(self):
        """创建加密工具实例"""
        token = "test_token"
        encoding_aes_key = "4jpk9t1dbimt2qg66wsl75d2w3me5zpmvle47xptpz9iaj3bq" + "=" * 4
        corp_id = "test_corp_id"
        return WxKfCrypto(token, encoding_aes_key, corp_id)

    def test_encrypt_decrypt_roundtrip(self, crypto_instance):
        """测试加密解密往返"""
        original_msg = "<xml><test>content</test></xml>"

        # 加密
        encrypted_msg, timestamp, nonce = crypto_instance.encrypt_msg(original_msg)

        # 计算签名
        signature = crypto_instance.get_sha1(
            crypto_instance.token, timestamp, nonce, encrypted_msg
        )

        # 解密
        decrypted_msg, msgid = crypto_instance.decrypt_msg(
            encrypted_msg, signature, timestamp, nonce
        )

        assert decrypted_msg == original_msg

    def test_signature_verification(self, crypto_instance):
        """测试签名验证"""
        test_msg = "test_message"
        timestamp = "1234567890"
        nonce = "test_nonce"

        # 计算正确签名
        correct_signature = crypto_instance.get_sha1(
            crypto_instance.token, timestamp, nonce, test_msg
        )

        # 验证正确签名
        assert crypto_instance.check_signature(
            correct_signature, timestamp, nonce, test_msg
        )

        # 验证错误签名
        wrong_signature = "wrong_signature"
        assert not crypto_instance.check_signature(
            wrong_signature, timestamp, nonce, test_msg
        )

    def test_xml_to_dict_conversion(self, crypto_instance):
        """测试XML转字典"""
        xml_str = """<xml>
    <Field1>Value1</Field1>
    <Field2>Value2</Field2>
    <Field3>Value3</Field3>
</xml>"""

        result = crypto_instance.xml_to_dict(xml_str)
        expected = {
            "Field1": "Value1",
            "Field2": "Value2",
            "Field3": "Value3"
        }
        assert result == expected

    def test_dict_to_xml_conversion(self, crypto_instance):
        """测试字典转XML"""
        data = {
            "Field1": "Value1",
            "Field2": "Value2",
            "Field3": "Value3"
        }

        xml_str = crypto_instance.dict_to_xml(data, "test_xml")

        # 验证XML包含所有字段
        assert "Field1" in xml_str
        assert "Value1" in xml_str
        assert "Field2" in xml_str
        assert "Value2" in xml_str
        assert "Field3" in xml_str
        assert "Value3" in xml_str

    def test_extract_xml_field(self, crypto_instance):
        """测试从XML提取字段"""
        xml_str = """<xml>
    <TargetField>TargetValue</TargetField>
    <OtherField>OtherValue</OtherField>
</xml>"""

        # 提取存在的字段
        value = crypto_instance.extract_xml_field(xml_str, "TargetField")
        assert value == "TargetValue"

        # 提取不存在的字段
        value = crypto_instance.extract_xml_field(xml_str, "NonExistentField")
        assert value is None

    def test_invalid_xml_handling(self, crypto_instance):
        """测试无效XML处理"""
        invalid_xml = "<invalid><xml>"

        # XML转字典应该返回空字典而不是抛出异常
        result = crypto_instance.xml_to_dict(invalid_xml)
        assert result == {}

        # 提取字段应该返回None而不是抛出异常
        value = crypto_instance.extract_xml_field(invalid_xml, "AnyField")
        assert value is None


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])