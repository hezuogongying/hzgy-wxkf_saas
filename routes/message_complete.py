# -*- coding: utf-8 -*-
"""完整消息路由"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.client import WxKfSaasClient
from core.dependencies import get_client
from models.message import (
    SendMessageResponse,
    SyncMsgResponse,
    SendWelcomeResponse,
    RecallMessageResponse,
)

# ===== FastAPI路由 =====

router = APIRouter(prefix="/api/v1/message", tags=["消息管理"])


# ===== 请求模型 =====

class SendTextMessageRequestModel(BaseModel):
    """发送文本消息请求模型"""
    corp_id: str
    touser: str
    open_kfid: str
    content: str
    msgid: Optional[str] = None


class SendImageMessageRequestModel(BaseModel):
    """发送图片消息请求模型"""
    corp_id: str
    touser: str
    open_kfid: str
    media_id: str
    msgid: Optional[str] = None


class SendVoiceMessageRequestModel(BaseModel):
    """发送语音消息请求模型"""
    corp_id: str
    touser: str
    open_kfid: str
    media_id: str
    msgid: Optional[str] = None


class SendVideoMessageRequestModel(BaseModel):
    """发送视频消息请求模型"""
    corp_id: str
    touser: str
    open_kfid: str
    media_id: str
    msgid: Optional[str] = None


class SendFileMessageRequestModel(BaseModel):
    """发送文件消息请求模型"""
    corp_id: str
    touser: str
    open_kfid: str
    media_id: str
    msgid: Optional[str] = None


class SendLocationMessageRequestModel(BaseModel):
    """发送位置消息请求模型"""
    corp_id: str
    touser: str
    open_kfid: str
    latitude: float
    longitude: float
    name: Optional[str] = None
    address: Optional[str] = None
    msgid: Optional[str] = None


class SendMiniProgramMessageRequestModel(BaseModel):
    """发送小程序消息请求模型"""
    corp_id: str
    touser: str
    open_kfid: str
    title: str
    appid: str
    pagepath: str
    thumb_media_id: Optional[str] = None
    msgid: Optional[str] = None


class SendChannelsShopProductRequestModel(BaseModel):
    """发送视频号商品消息请求模型"""
    corp_id: str
    touser: str
    open_kfid: str
    product_id: str
    head_image: Optional[str] = None
    title: Optional[str] = None
    sales_price: Optional[str] = None
    shop_nickname: Optional[str] = None
    shop_head_image: Optional[str] = None
    msgid: Optional[str] = None


class SendChannelsShopOrderRequestModel(BaseModel):
    """发送视频号订单消息请求模型"""
    corp_id: str
    touser: str
    open_kfid: str
    order_id: str
    product_titles: Optional[str] = None
    price_wording: Optional[str] = None
    state: Optional[str] = None
    image_url: Optional[str] = None
    shop_nickname: Optional[str] = None
    msgid: Optional[str] = None


class SendMergedMessageRequestModel(BaseModel):
    """发送聊天记录消息请求模型"""
    corp_id: str
    touser: str
    open_kfid: str
    title: str
    item: List[Dict[str, Any]]
    msgid: Optional[str] = None


class SendChannelsMessageRequestModel(BaseModel):
    """发送视频号消息请求模型"""
    corp_id: str
    touser: str
    open_kfid: str
    sub_type: int
    nickname: Optional[str] = None
    title: Optional[str] = None
    msgid: Optional[str] = None


class SendNoteMessageRequestModel(BaseModel):
    """发送笔记消息请求模型"""
    corp_id: str
    touser: str
    open_kfid: str
    msgid: Optional[str] = None


class SyncMessageRequestModel(BaseModel):
    """同步消息请求模型"""
    corp_id: str
    cursor: Optional[str] = None
    token: Optional[str] = None
    limit: int = 1000
    voice_format: int = 0
    open_kfid: Optional[str] = None


class SendWelcomeMessageRequestModel(BaseModel):
    """发送欢迎语请求模型"""
    corp_id: str
    welcome_code: str
    msgtype: str
    content: Optional[str] = None
    media_id: Optional[str] = None
    title: Optional[str] = None
    appid: Optional[str] = None
    pagepath: Optional[str] = None
    thumb_media_id: Optional[str] = None


class RecallMessageRequestModel(BaseModel):
    """撤回消息请求模型"""
    corp_id: str
    msgid: str


# ===== 路由端点 =====

@router.post("/text", response_model=SendMessageResponse, summary="发送文本消息")
async def send_text_message(
    request_data: SendTextMessageRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """发送文本消息"""
    try:
        from api.message_complete import CompleteMessageApi
        message_api = CompleteMessageApi(client)

        response = await message_api.send_text(
            corp_id=request_data.corp_id,
            touser=request_data.touser,
            open_kfid=request_data.open_kfid,
            content=request_data.content,
            msgid=request_data.msgid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image", response_model=SendMessageResponse, summary="发送图片消息")
async def send_image_message(
    request_data: SendImageMessageRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """发送图片消息"""
    try:
        from api.message_complete import CompleteMessageApi
        message_api = CompleteMessageApi(client)

        response = await message_api.send_image(
            corp_id=request_data.corp_id,
            touser=request_data.touser,
            open_kfid=request_data.open_kfid,
            media_id=request_data.media_id,
            msgid=request_data.msgid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice", response_model=SendMessageResponse, summary="发送语音消息")
async def send_voice_message(
    request_data: SendVoiceMessageRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """发送语音消息"""
    try:
        from api.message_complete import CompleteMessageApi
        message_api = CompleteMessageApi(client)

        response = await message_api.send_voice(
            corp_id=request_data.corp_id,
            touser=request_data.touser,
            open_kfid=request_data.open_kfid,
            media_id=request_data.media_id,
            msgid=request_data.msgid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video", response_model=SendMessageResponse, summary="发送视频消息")
async def send_video_message(
    request_data: SendVideoMessageRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """发送视频消息"""
    try:
        from api.message_complete import CompleteMessageApi
        message_api = CompleteMessageApi(client)

        response = await message_api.send_video(
            corp_id=request_data.corp_id,
            touser=request_data.touser,
            open_kfid=request_data.open_kfid,
            media_id=request_data.media_id,
            msgid=request_data.msgid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/file", response_model=SendMessageResponse, summary="发送文件消息")
async def send_file_message(
    request_data: SendFileMessageRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """发送文件消息"""
    try:
        from api.message_complete import CompleteMessageApi
        message_api = CompleteMessageApi(client)

        response = await message_api.send_file(
            corp_id=request_data.corp_id,
            touser=request_data.touser,
            open_kfid=request_data.open_kfid,
            media_id=request_data.media_id,
            msgid=request_data.msgid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/location", response_model=SendMessageResponse, summary="发送位置消息")
async def send_location_message(
    request_data: SendLocationMessageRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """发送位置消息"""
    try:
        from api.message_complete import CompleteMessageApi
        message_api = CompleteMessageApi(client)

        response = await message_api.send_location(
            corp_id=request_data.corp_id,
            touser=request_data.touser,
            open_kfid=request_data.open_kfid,
            latitude=request_data.latitude,
            longitude=request_data.longitude,
            name=request_data.name,
            address=request_data.address,
            msgid=request_data.msgid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/miniprogram", response_model=SendMessageResponse, summary="发送小程序消息")
async def send_miniprogram_message(
    request_data: SendMiniProgramMessageRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """发送小程序消息"""
    try:
        from api.message_complete import CompleteMessageApi
        message_api = CompleteMessageApi(client)

        response = await message_api.send_miniprogram(
            corp_id=request_data.corp_id,
            touser=request_data.touser,
            open_kfid=request_data.open_kfid,
            title=request_data.title,
            appid=request_data.appid,
            pagepath=request_data.pagepath,
            thumb_media_id=request_data.thumb_media_id,
            msgid=request_data.msgid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/channels_shop_product", response_model=SendMessageResponse, summary="发送视频号商品消息")
async def send_channels_shop_product_message(
    request_data: SendChannelsShopProductRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """发送视频号商品消息"""
    try:
        from api.message_complete import CompleteMessageApi
        message_api = CompleteMessageApi(client)

        response = await message_api.send_channels_shop_product(
            corp_id=request_data.corp_id,
            touser=request_data.touser,
            open_kfid=request_data.open_kfid,
            product_id=request_data.product_id,
            head_image=request_data.head_image,
            title=request_data.title,
            sales_price=request_data.sales_price,
            shop_nickname=request_data.shop_nickname,
            shop_head_image=request_data.shop_head_image,
            msgid=request_data.msgid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/channels_shop_order", response_model=SendMessageResponse, summary="发送视频号订单消息")
async def send_channels_shop_order_message(
    request_data: SendChannelsShopOrderRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """发送视频号订单消息"""
    try:
        from api.message_complete import CompleteMessageApi
        message_api = CompleteMessageApi(client)

        response = await message_api.send_channels_shop_order(
            corp_id=request_data.corp_id,
            touser=request_data.touser,
            open_kfid=request_data.open_kfid,
            order_id=request_data.order_id,
            product_titles=request_data.product_titles,
            price_wording=request_data.price_wording,
            state=request_data.state,
            image_url=request_data.image_url,
            shop_nickname=request_data.shop_nickname,
            msgid=request_data.msgid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/merged_msg", response_model=SendMessageResponse, summary="发送聊天记录消息")
async def send_merged_message(
    request_data: SendMergedMessageRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """发送聊天记录消息"""
    try:
        from api.message_complete import CompleteMessageApi
        message_api = CompleteMessageApi(client)

        response = await message_api.send_merged_msg(
            corp_id=request_data.corp_id,
            touser=request_data.touser,
            open_kfid=request_data.open_kfid,
            title=request_data.title,
            item=request_data.item,
            msgid=request_data.msgid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/channels", response_model=SendMessageResponse, summary="发送视频号消息")
async def send_channels_message(
    request_data: SendChannelsMessageRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """发送视频号消息"""
    try:
        from api.message_complete import CompleteMessageApi
        message_api = CompleteMessageApi(client)

        response = await message_api.send_channels(
            corp_id=request_data.corp_id,
            touser=request_data.touser,
            open_kfid=request_data.open_kfid,
            sub_type=request_data.sub_type,
            nickname=request_data.nickname,
            title=request_data.title,
            msgid=request_data.msgid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/note", response_model=SendMessageResponse, summary="发送笔记消息")
async def send_note_message(
    request_data: SendNoteMessageRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """发送笔记消息"""
    try:
        from api.message_complete import CompleteMessageApi
        message_api = CompleteMessageApi(client)

        response = await message_api.send_note(
            corp_id=request_data.corp_id,
            touser=request_data.touser,
            open_kfid=request_data.open_kfid,
            msgid=request_data.msgid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync", response_model=SyncMsgResponse, summary="同步消息")
async def sync_message(
    request_data: SyncMessageRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """同步消息"""
    try:
        from api.message_complete import CompleteMessageApi
        message_api = CompleteMessageApi(client)

        response = await message_api.sync_msg(
            corp_id=request_data.corp_id,
            cursor=request_data.cursor,
            token=request_data.token,
            limit=request_data.limit,
            voice_format=request_data.voice_format,
            open_kfid=request_data.open_kfid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/welcome", response_model=SendWelcomeResponse, summary="发送欢迎语")
async def send_welcome_message(
    request_data: SendWelcomeMessageRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """发送欢迎语"""
    try:
        from api.message_complete import CompleteMessageApi
        message_api = CompleteMessageApi(client)

        response = await message_api.send_welcome(
            corp_id=request_data.corp_id,
            welcome_code=request_data.welcome_code,
            msgtype=request_data.msgtype,
            content=request_data.content,
            media_id=request_data.media_id,
            title=request_data.title,
            appid=request_data.appid,
            pagepath=request_data.pagepath,
            thumb_media_id=request_data.thumb_media_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recall", response_model=RecallMessageResponse, summary="撤回消息")
async def recall_message(
    request_data: RecallMessageRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """撤回消息"""
    try:
        from api.message_complete import CompleteMessageApi
        message_api = CompleteMessageApi(client)

        response = await message_api.recall(
            corp_id=request_data.corp_id,
            msgid=request_data.msgid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))