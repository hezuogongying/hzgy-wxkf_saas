# -*- coding: utf-8 -*-
"""消息相关数据模型"""

from typing import Optional, List, Dict, Any
from pydantic import Field
from wxkf_saas.models.base import WxKfBaseModel, SuccessResponse


# ===== 发送消息请求模型 =====

class SendMessageRequest(WxKfBaseModel):
    """发送消息请求基类"""
    touser: str = Field(..., description="指定接收消息的客户UserID")
    open_kfid: str = Field(..., description="指定发送消息的客服账号ID")
    msgid: Optional[str] = Field(None, description="消息ID,用于去重")
    msgtype: str = Field(..., description="消息类型")


class TextContent(WxKfBaseModel):
    """文本消息内容"""
    content: str = Field(..., description="文本内容,最长不超过2048个字节")


class SendTextMessageRequest(SendMessageRequest):
    """发送文本消息请求"""
    msgtype: str = Field("text", description="消息类型")
    text: TextContent = Field(..., description="文本消息内容")


class ImageContent(WxKfBaseModel):
    """图片消息内容"""
    media_id: str = Field(..., description="图片媒体文件ID")


class SendImageMessageRequest(SendMessageRequest):
    """发送图片消息请求"""
    msgtype: str = Field("image", description="消息类型")
    image: ImageContent = Field(..., description="图片消息内容")


class VoiceContent(WxKfBaseModel):
    """语音消息内容"""
    media_id: str = Field(..., description="语音媒体文件ID")


class SendVoiceMessageRequest(SendMessageRequest):
    """发送语音消息请求"""
    msgtype: str = Field("voice", description="消息类型")
    voice: VoiceContent = Field(..., description="语音消息内容")


class VideoContent(WxKfBaseModel):
    """视频消息内容"""
    media_id: str = Field(..., description="视频媒体文件ID")


class SendVideoMessageRequest(SendMessageRequest):
    """发送视频消息请求"""
    msgtype: str = Field("video", description="消息类型")
    video: VideoContent = Field(..., description="视频消息内容")


class FileContent(WxKfBaseModel):
    """文件消息内容"""
    media_id: str = Field(..., description="文件媒体文件ID")


class SendFileMessageRequest(SendMessageRequest):
    """发送文件消息请求"""
    msgtype: str = Field("file", description="消息类型")
    file: FileContent = Field(..., description="文件消息内容")


# ===== 同步消息相关模型 =====

class SyncMsgRequest(WxKfBaseModel):
    """同步消息请求"""
    cursor: Optional[str] = Field(
        None,
        max_length=64,
        description="上一次调用时返回的next_cursor,第一次拉取可以不填"
    )
    token: Optional[str] = Field(
        None,
        max_length=128,
        description="回调事件返回的token字段,10分钟内有效"
    )
    limit: int = Field(1000, ge=1, le=1000, description="期望请求的数据量,默认和最大值都为1000")
    voice_format: int = Field(0, ge=0, le=1, description="语音消息类型,0-Amr 1-Silk,默认0")
    open_kfid: Optional[str] = Field(None, description="指定拉取某个客服账号的消息")


class MessageItem(WxKfBaseModel):
    """消息项"""
    msgid: str = Field(..., description="消息ID")
    open_kfid: str = Field(..., description="客服账号ID")
    external_userid: str = Field(..., description="客户UserID")
    send_time: int = Field(..., description="消息发送时间戳")
    origin: int = Field(..., description="消息来源,3-客户回复 4-系统推送")
    msgtype: str = Field(..., description="消息类型")
    # 根据msgtype不同,会有不同的消息内容字段
    text: Optional[TextContent] = Field(None, description="文本消息内容")
    image: Optional[ImageContent] = Field(None, description="图片消息内容")
    voice: Optional[VoiceContent] = Field(None, description="语音消息内容")
    video: Optional[VideoContent] = Field(None, description="视频消息内容")
    file: Optional[FileContent] = Field(None, description="文件消息内容")
    event: Optional[Dict[str, Any]] = Field(None, description="事件内容")


class SyncMsgResponse(SuccessResponse):
    """同步消息响应"""
    next_cursor: str = Field(..., description="下次调用带上该值,实现增量拉取")
    has_more: int = Field(..., description="是否还有更多数据,0-否 1-是")
    msg_list: List[MessageItem] = Field(default_factory=list, description="消息列表")


# ===== 发送消息响应模型 =====

class SendMessageResponse(SuccessResponse):
    """发送消息响应"""
    msgid: str = Field(..., description="消息ID")


# ===== 发送欢迎语相关模型 =====

class SendWelcomeRequest(WxKfBaseModel):
    """发送欢迎语请求"""
    welcome_code: str = Field(..., description="通过进入会话事件获取的welcome_code")
    msgtype: str = Field(..., description="消息类型")
    # 根据msgtype不同,需要包含不同的消息内容字段
    text: Optional[TextContent] = Field(None, description="文本消息内容")
    image: Optional[ImageContent] = Field(None, description="图片消息内容")


class SendWelcomeResponse(SuccessResponse):
    """发送欢迎语响应"""
    pass


# ===== 撤回消息相关模型 =====

class RecallMessageRequest(WxKfBaseModel):
    """撤回消息请求"""
    msgid: str = Field(..., description="要撤回的消息ID")


class RecallMessageResponse(SuccessResponse):
    """撤回消息响应"""
    pass
