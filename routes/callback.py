# -*- coding: utf-8 -*-
"""回调路由"""

from fastapi import APIRouter, Request, HTTPException, Form, Body, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any

from core.config import WxKfSaasConfig
from core.crypto import WxKfCrypto
from core.callback_handler import CallbackHandler
from models.callback import CallbackResponse, CallbackProcessResult
import logging

router = APIRouter(prefix="/callback", tags=["回调"])

# 全局回调处理器实例
_callback_handler: Optional[CallbackHandler] = None


async def get_callback_handler() -> CallbackHandler:
    """获取回调处理器实例"""
    global _callback_handler
    if _callback_handler is None:
        config = WxKfSaasConfig()
        crypto = WxKfCrypto(
            token=config.provider_token,
            encoding_aes_key=config.provider_encoding_aes_key
        )
        _callback_handler = CallbackHandler(crypto)
    return _callback_handler


async def get_crypto() -> WxKfCrypto:
    """获取加解密实例"""
    config = WxKfSaasConfig()
    return WxKfCrypto(
        token=config.provider_token,
        encoding_aes_key=config.provider_encoding_aes_key
    )


# 统一的客服回调处理端点
@router.post("/customer-service", summary="处理客服会话回调")
@router.post("/suite", summary="处理企业授权事件回调")
@router.post("/provider", summary="处理服务商授权事件回调")
async def unified_callback(
    request: Request,
    msg_signature: str = Form(..., description="消息签名"),
    timestamp: str = Form(..., description="时间戳"),
    nonce: str = Form(..., description="随机数"),
):
    """统一处理微信客服回调消息

    支持处理各种类型的回调消息：
    - 客服会话消息（文本、图片、语音、视频、文件、位置、小程序等）
    - 客服会话事件（用户进入/结束会话、消息发送失败、用户撤回消息等）
    - 服务商授权事件（suite_ticket、企业授权/取消授权等）
    - 企业授权事件（通讯录变更、外部联系人变更、授权变更等）

    Args:
        request: HTTP请求
        msg_signature: 消息签名
        timestamp: 时间戳
        nonce: 随机数

    Returns:
        CallbackResponse: 回调响应

    文档:
        - 客服回调: https://kf.weixin.qq.com/api/doc/path/94745
        - 服务商回调: https://developer.work.weixin.qq.com/document/path/91392
        - 企业回调: https://developer.work.weixin.qq.com/document/path/91393
    """
    try:
        # 获取原始请求数据
        body = await request.body()

        # 如果是表单提交，需要从表单字段中提取加密消息
        if request.headers.get("content-type", "").startswith("application/x-www-form-urlencoded"):
            # 解析表单数据
            import urllib.parse
            form_data = urllib.parse.parse_qs(body.decode('utf-8'))
            encrypted_xml = form_data.get('echostr', [b''])[0].decode('utf-8') if 'echostr' in form_data else ''
        else:
            # 直接获取XML内容
            encrypted_xml = body.decode('utf-8')

        if not encrypted_xml:
            logging.warning("收到空的回调消息")
            return CallbackResponse()

        # 获取回调处理器
        handler = await get_callback_handler()

        # 处理回调消息
        result: CallbackProcessResult = await handler.process_callback_message(
            encrypted_xml, msg_signature, timestamp, nonce
        )

        if result.success:
            logging.info(f"回调消息处理成功: {result.message}")
            return CallbackResponse()
        else:
            logging.error(f"回调消息处理失败: {result.message}")
            # 即使处理失败，也要返回success响应，避免微信重复推送
            return CallbackResponse()

    except Exception as e:
        logging.error(f"统一处理回调消息失败: {str(e)}")
        # 即使发生异常，也要返回success响应，避免微信重复推送
        return CallbackResponse()


@router.get("/verify", summary="验证回调URL")
async def verify_callback_url(
    msg_signature: str = Query(..., description="消息签名"),
    timestamp: str = Query(..., description="时间戳"),
    nonce: str = Query(..., description="随机数"),
    echostr: str = Query(..., description="随机字符串"),
):
    """验证回调URL

    企业微信在设置回调URL时会发送验证请求。
    验证成功后，企业微信会向该URL推送各种回调消息。

    Args:
        msg_signature: 消息签名
        timestamp: 时间戳
        nonce: 随机数
        echostr: 随机字符串（加密内容）

    Returns:
        str: 返回echostr用于验证

    文档:
        - 服务商回调验证: https://developer.work.weixin.qq.com/document/path/91391
        - 企业应用回调验证: https://developer.work.weixin.qq.com/document/path/91391
    """
    try:
        crypto = await get_crypto()

        # 验证签名
        if crypto.check_signature(msg_signature, timestamp, nonce, echostr):
            logging.info("回调URL验证成功")
            return echostr
        else:
            logging.warning("回调URL验证失败：签名不匹配")
            raise HTTPException(status_code=403, detail="签名验证失败")

    except Exception as e:
        logging.error(f"验证回调URL失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# 支持GET请求的回调URL验证（兼容性）
@router.get("/provider", summary="验证服务商回调URL")
@router.get("/suite", summary="验证企业回调URL")
@router.get("/customer-service", summary="验证客服回调URL")
async def verify_callback_url_compat(
    msg_signature: str = Query(..., description="消息签名"),
    timestamp: str = Query(..., description="时间戳"),
    nonce: str = Query(..., description="随机数"),
    echostr: str = Query(..., description="随机字符串"),
):
    """兼容性回调URL验证接口

    支持通过GET请求验证各种回调URL，包括：
    - /callback/provider - 服务商回调URL
    - /callback/suite - 企业应用回调URL
    - /callback/customer-service - 客服回调URL

    Args:
        msg_signature: 消息签名
        timestamp: 时间戳
        nonce: 随机数
        echostr: 随机字符串（加密内容）

    Returns:
        str: 返回echostr用于验证
    """
    return await verify_callback_url(msg_signature, timestamp, nonce, echostr)