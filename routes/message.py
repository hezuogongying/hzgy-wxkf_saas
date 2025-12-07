# -*- coding: utf-8 -*-
"""消息管理路由"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_async_db, get_db
from core.client import WxKfSaasClient
from core.config import WxKfSaasConfig
from api.message import MessageApi
from models.message import (
    SendVideoOrderNumberRequestModel,
    SendVideoOrderMessageRequestModel,
    SendChannelsShopProductRequest,
    SendChannelsShopOrderRequest,
)
from models.message import (
    SendMessageResponse,
    SyncMsgResponse,
    SendWelcomeResponse,
    RecallMessageResponse,
    SendVideoOrderNumberRequestModel,
    SendVideoOrderMessageRequestModel,
    SendChannelsShopProductRequest,
    SendChannelsShopOrderRequest,
    SendMergedMsgRequest,
    SendChannelsRequest,
    SendNoteRequest,
    TextContent,
    ImageContent,
    VoiceContent,
    VideoContent,
    FileContent,
    LocationContent,
    MiniProgramContent,
    ChannelsShopProductContent,
    ChannelsShopOrderContent,
    MergedMsgContent,
    ChannelsContent,
)
from models.callback import (
    ChannelsCallbackMessage,
    ChannelsShopProductCallbackMessage,
)

router = APIRouter(prefix="/api/messages", tags=["消息管理"])


# 请求模型
class SendTextMessageRequestModel(BaseModel):
    """发送文本消息请求模型"""
    corp_id: str
    touser: str
    open_kfid: str
    content: str
    msgid: Optional[str] = None


class SendVideoOrderNumberRequestModel(BaseModel):
    """发送视频号订单号消息请求模型"""
    corp_id: str
    touser: str
    open_kfid: str
    video_order_number: str
    msgid: Optional[str] = None


class SendVideoOrderMessageRequestModel(BaseModel):
    """发送视频号订单消息请求模型"""
    corp_id: str
    touser: str
    open_kfid: str
    video_order_message: str
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


class SendVideoOrderNumberRequestModel(BaseModel):
    """发送视频号订单号消息请求模型"""
    corp_id: str
    touser: str
    open_kfid: str
    video_order_number: str
    msgid: Optional[str] = None


class SendVideoOrderMessageRequestModel(BaseModel):
    """发送视频订单消息请求模型"""
    corp_id: str
    touser: str
    open_kfid: str
    video_order_message: str
    msgid: Optional[str] = None


class SyncMessageRequestModel(BaseModel):
    """同步消息请求模型"""
    corp_id: str
    cursor: Optional[str] = None
    token: Optional[str] = None
    limit: int = Query(1000, ge=1, le=1000, description="期望请求的数据量")
    voice_format: int = Query(0, ge=0, le=1, description="语音消息格式")
    open_kfid: Optional[str] = Query(None, description="指定拉取某个客服的消息")


class SendWelcomeMessageRequestModel(BaseModel):
    """发送欢迎语请求模型"""
    corp_id: str
    welcome_code: str
    msgtype: str
    content: Optional[str] = None
    media_id: Optional[str] = None


class RecallMessageRequestModel(BaseModel):
    """撤回消息请求模型"""
    corp_id: str
    msgid: str


# 响应模型
class APIResponse(BaseModel):
    """API通用响应模型"""
    code: int = 0
    message: str = "success"
    data: dict = {}


def get_db_session(db_gen=Depends(get_db)) -> Session:
    """从依赖注入的生成器中获取数据库会话"""
    return next(db_gen)


def get_client(db: Session = Depends(get_db_session)) -> WxKfSaasClient:
    """获取微信客服客户端实例"""
    config = WxKfSaasConfig()
    return WxKfSaasClient(config, db)


@router.post("/text", response_model=SendMessageResponse, summary="发送文本消息")
async def send_text_message(
    request_data: SendTextMessageRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """发送文本消息

    Args:
        request_data: 发送文本消息请求
        client: 微信客服客户端实例

    Returns:
        SendMessageResponse: 发送结果

    Raises:
        HTTPException: API调用失败
    """
    try:
        msg_api = MessageApi(client)
        response = await msg_api.send_text(
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
    """发送图片消息

    Args:
        request_data: 发送图片消息请求
        client: 微信客服客户端实例

    Returns:
        SendMessageResponse: 发送结果

    Raises:
        HTTPException: API调用失败
    """
    try:
        msg_api = MessageApi(client)
        response = await msg_api.send_image(
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
    """发送语音消息

    Args:
        request_data: 发送语音消息请求
        client: 微信客服客户端实例

    Returns:
        SendMessageResponse: 发送结果

    Raises:
        HTTPException: API调用失败
    """
    try:
        msg_api = MessageApi(client)
        response = await msg_api.send_voice(
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
    """发送视频消息

    Args:
        request_data: 发送视频消息请求
        client: 微信客服客户端实例

    Returns:
        SendMessageResponse: 发送结果

    Raises:
        HTTPException: API调用失败
    """
    try:
        msg_api = MessageApi(client)
        response = await msg_api.send_video(
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
    """发送文件消息

    Args:
        request_data: 发送文件消息请求
        client: 微信客服客户端实例

    Returns:
        SendMessageResponse: 发送结果

    Raises:
        HTTPException: API调用失败
    """
    try:
        msg_api = MessageApi(client)
        response = await msg_api.send_file(
            corp_id=request_data.corp_id,
            touser=request_data.touser,
            open_kfid=request_data.open_kfid,
            media_id=request_data.media_id,
            msgid=request_data.msgid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync", response_model=SyncMsgResponse, summary="同步消息")
async def sync_message(
    corp_id: str = Query(..., description="企业ID"),
    cursor: Optional[str] = Query(None, description="游标"),
    token: Optional[str] = Query(None, description="回调事件返回的token"),
    limit: int = Query(1000, ge=1, le=1000, description="期望请求的数据量"),
    voice_format: int = Query(0, ge=0, le=1, description="语音消息格式"),
    open_kfid: Optional[str] = Query(None, description="指定客服账号"),
    client: WxKfSaasClient = Depends(get_client)
):
    """同步消息

    获取客户主动发送的消息、发送消息失败事件、客户点击菜单消息的回复消息等。

    Args:
        corp_id: 企业ID
        cursor: 上一次调用时返回的next_cursor
        token: 回调事件返回的token字段
        limit: 期望请求的数据量，默认和最大值都为1000
        voice_format: 语音消息类型，0-Amr 1-Silk，默认0
        open_kfid: 指定拉取某个客服账号的消息
        client: 微信客服客户端实例

    Returns:
        SyncMsgResponse: 消息列表和分页信息

    Raises:
        HTTPException: API调用失败
    """
    try:
        msg_api = MessageApi(client)
        response = await msg_api.sync_msg(
            corp_id=corp_id,
            cursor=cursor,
            token=token,
            limit=limit,
            voice_format=voice_format,
            open_kfid=open_kfid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/welcome", response_model=SendWelcomeResponse, summary="发送欢迎语")
async def send_welcome_message(
    request_data: SendWelcomeMessageRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """发送欢迎语

    当客户进入会话且满足条件时，通过welcome_code发送欢迎语。

    Args:
        request_data: 发送欢迎语请求
        client: 微信客服客户端实例

    Returns:
        SendWelcomeResponse: 发送结果

    Raises:
        HTTPException: API调用失败
    """
    try:
        msg_api = MessageApi(client)
        response = await msg_api.send_welcome(
            corp_id=request_data.corp_id,
            welcome_code=request_data.welcome_code,
            msgtype=request_data.msgtype,
            content=request_data.content,
            media_id=request_data.media_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recall", response_model=RecallMessageResponse, summary="撤回消息")
async def recall_message(
    request_data: RecallMessageRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """撤回消息

    撤回通过接口发送的消息，撤回后客户会看到"对方撤回了一条消息"的提示。

    Args:
        request_data: 撤回消息请求
        client: 微信客服客户端实例

    Returns:
        RecallMessageResponse: 撤回结果

    Raises:
        HTTPException: API调用失败
    """
    try:
        msg_api = MessageApi(client)
        response = await msg_api.recall(
            corp_id=request_data.corp_id,
            msgid=request_data.msgid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send_video_order_number", response_model=SendMessageResponse, summary="发送视频号订单号消息")
async def send_video_order_number_message(
    request_data: SendVideoOrderNumberRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """发送视频号订单号消息

    Args:
        request_data: 发送视频号订单号消息请求
        client: 微信客服客户端实例

    Returns:
        SendMessageResponse: 发送结果

    Raises:
        HTTPException: API调用失败
    """
    try:
        msg_api = MessageApi(client)
        response = await msg_api.send_video_order_number(
            corp_id=request_data.corp_id,
            touser=request_data.touser,
            open_kfid=request_data.open_kfid,
            video_order_number=request_data.video_order_number,
            msgid=request_data.msgid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send_video_order_message", response_model=SendMessageResponse, summary="发送视频订单消息")
async def send_video_order_message(
    request_data: SendVideoOrderMessageRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """发送视频订单消息

    Args:
        request_data: 发送视频订单消息请求
        client: 微信客服客户端实例

    Returns:
        SendMessageResponse: 发送结果

    Raises:
        HTTPException: API调用失败
    """
    try:
        msg_api = MessageApi(client)
        response = await msg_api.send_video_order_message(
            corp_id=request_data.corp_id,
            touser=request_data.touser,
            open_kfid=request_data.open_kfid,
            video_order_message=request_data.video_order_message,
            msgid=request_data.msgid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))