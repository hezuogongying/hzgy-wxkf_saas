# -*- coding: utf-8 -*-
"""回调消息数据模型"""

from typing import Optional, Dict, Any, List
from pydantic import Field
from models.base import WxKfBaseModel


# ===== 基础回调消息模型 =====

class CallbackMessageBase(WxKfBaseModel):
    """回调消息基类"""
    touser: str = Field(..., description="接收方企业微信CorpID")
    fromuser: str = Field(..., description="发送方UserID，可能是客户或客服")
    createtime: int = Field(..., description="消息创建时间，Unix时间戳")
    msgtype: str = Field(..., description="消息类型")
    msgid: Optional[str] = Field(None, description="消息ID，64位整型数字")
    agentid: Optional[str] = Field(None, description="企业应用的id")


# ===== 基础事件消息模型 =====

class CallbackEventBase(WxKfBaseModel):
    """回调事件基类"""
    touser: str = Field(..., description="接收方企业微信CorpID")
    fromuser: str = Field(..., description="发送方UserID")
    createtime: int = Field(..., description="消息创建时间，Unix时间戳")
    event: str = Field(..., description="事件类型")
    agentid: Optional[str] = Field(None, description="企业应用的id")


# ===== 客户消息类型 =====

class TextCallbackMessage(CallbackMessageBase):
    """文本消息回调"""
    content: str = Field(..., description="文本消息内容")


class ImageCallbackMessage(CallbackMessageBase):
    """图片消息回调"""
    media_id: str = Field(..., description="图片媒体文件id")
    pic_url: str = Field(..., description="图片链接")
    recognition: Optional[str] = Field(None, description="图片识别结果，ocr由于图片内容而可能不同")


class VoiceCallbackMessage(CallbackMessageBase):
    """语音消息回调"""
    media_id: str = Field(..., description="语音媒体文件id")
    format: str = Field(..., description="语音格式，如amr、speex等")
    recognition: Optional[str] = Field(None, description="语音识别结果")


class VideoCallbackMessage(CallbackMessageBase):
    """视频消息回调"""
    media_id: str = Field(..., description="视频媒体文件id")
    thumb_media_id: str = Field(..., description="视频缩略图的媒体id")
    location: Optional[str] = Field(None, description="视频的位置信息")


class FileCallbackMessage(CallbackMessageBase):
    """文件消息回调"""
    media_id: str = Field(..., description="文件媒体文件id")
    title: str = Field(..., description="文件名")
    file_ext: str = Field(..., description="文件扩展名")
    file_size: int = Field(..., description="文件大小")


class LocationCallbackMessage(CallbackMessageBase):
    """位置消息回调"""
    location_x: float = Field(..., description="地理位置纬度")
    location_y: float = Field(..., description="地理位置经度")
    scale: int = Field(..., description="地图缩放大小")
    label: str = Field(..., description="地理位置信息")
    poi_name: str = Field(..., description="POI名称")


class MiniProgramCallbackMessage(CallbackMessageBase):
    """小程序消息回调"""
    title: str = Field(..., description="小程序标题")
    appid: str = Field(..., description="小程序appid")
    pagepath: str = Field(..., description="小程序页面路径")
    thumb_media_id: str = Field(..., description="小程序消息封面媒体id")
    thumb_url: str = Field(..., description="小程序消息封面url")


class ChannelsShopProductCallbackMessage(CallbackMessageBase):
    """视频号商品消息回调"""
    product_id: str = Field(..., description="商品ID")
    head_image: str = Field(..., description="商品图片")
    title: str = Field(..., description="商品标题")
    price_wording: str = Field(..., description="商品价格描述")
    shop_nickname: str = Field(..., description="店铺名称")
    shop_head_image: str = Field(..., description="店铺头像")
    finder_nickname: str = Field(..., description="推荐人昵称")
    finder_head_image: str = Field(..., description="推荐人头像")


class ChannelsShopOrderCallbackMessage(CallbackMessageBase):
    """视频号订单消息回调"""
    order_id: str = Field(..., description="订单号")
    product_titles: str = Field(..., description="商品标题")
    price_wording: str = Field(..., description="订单价格描述")
    state: str = Field(..., description="订单状态")
    image_url: str = Field(..., description="订单缩略图")
    shop_nickname: str = Field(..., description="店铺名称")
    shop_head_image: str = Field(..., description="店铺头像")
    finder_nickname: str = Field(..., description="推荐人昵称")
    finder_head_image: str = Field(..., description="推荐人头像")
    create_time: int = Field(..., description="订单创建时间")
    pay_time: int = Field(..., description="订单支付时间")
    ship_time: Optional[int] = Field(None, description="订单发货时间")
    finish_time: Optional[int] = Field(None, description="订单完成时间")


class MergedMsgCallbackMessage(CallbackMessageBase):
    """聊天记录消息回调"""
    title: str = Field(..., description="聊天记录标题")
    item_count: int = Field(..., description="消息记录内的消息数量")
    item_list: List[Dict[str, Any]] = Field(..., description="消息记录内的消息内容")


class ChannelsCallbackMessage(CallbackMessageBase):
    """视频号消息回调"""
    sub_type: int = Field(..., description="视频号消息类型，1视频号动态、2视频号直播、3视频号名片")
    finder_nickname: Optional[str] = Field(None, description="视频号名称")
    avatar_url: Optional[str] = Field(None, description="视频号头像")
    title: Optional[str] = Field(None, description="视频号动态标题")
    live_status: Optional[int] = Field(None, description="直播状态，1直播中 2已结束")
    start_time: Optional[int] = Field(None, description="直播开始时间")
    end_time: Optional[int] = Field(None, description="直播结束时间")
    viewer_num: Optional[int] = Field(None, description="观看人数")


class NoteCallbackMessage(CallbackMessageBase):
    """笔记消息回调"""
    # 笔记消息目前暂不返回详细消息内容
    pass


# ===== 事件消息类型 =====

class EnterSessionCallbackEvent(CallbackEventBase):
    """用户进入会话事件"""
    service_userid: Optional[str] = Field(None, description="接待用户的客服userid")
    open_kfid: str = Field(..., description="客服账号ID")
    welcome_code: str = Field(..., description="欢迎语code，用于发送欢迎语")
    scene: str = Field(..., description="进入会话的场景值")
    scene_param: Optional[str] = Field(None, description="场景参数")
    wechat_channels: Optional[Dict[str, Any]] = Field(None, description="进入会话的视频号信息")


class CloseSessionCallbackEvent(CallbackEventBase):
    """用户离开会话事件"""
    open_kfid: str = Field(..., description="客服账号ID")
    close_type: int = Field(..., description="会话关闭类型")


class MsgSendFailCallbackEvent(CallbackEventBase):
    """消息发送失败事件"""
    fail_type: int = Field(..., description="失败类型")
    fail_msgid: str = Field(..., description="发送失败的消息ID")
    fail_time: int = Field(..., description="失败发送时间")


class UserRecallMsgCallbackEvent(CallbackEventBase):
    """用户撤回消息事件"""
    recall_msgid: str = Field(..., description="撤回的消息ID")
    recall_time: int = Field(..., description="撤回消息时间")


class CardClickCallbackEvent(CallbackEventBase):
    """用户点击客服名片事件"""
    open_kfid: str = Field(..., description="客服账号ID")
    scene: str = Field(..., description="点击名片的场景")
    scene_param: Optional[str] = Field(None, description="场景参数")


# ===== 服务商授权事件类型 =====

class ProviderCallbackEvent(WxKfBaseModel):
    """服务商回调事件"""
    infotype: str = Field(..., description="信息类型")
    suiteid: str = Field(..., description="套件ID")
    timestamp: int = Field(..., description="时间戳")
    suite_ticket: Optional[str] = Field(None, description="套票ticket")
    auth_corp_info: Optional[Dict[str, Any]] = Field(None, description="授权企业信息")


class SuiteCallbackEvent(WxKfBaseModel):
    """企业授权事件"""
    infotype: str = Field(..., description="信息类型")
    suiteid: str = Field(..., description="套件ID")
    timestamp: int = Field(..., description="时间戳")
    auth_corp_info: Optional[Dict[str, Any]] = Field(None, description="授权企业信息")
    auth_info: Optional[Dict[str, Any]] = Field(None, description="授权信息")
    user_userid: Optional[str] = Field(None, description="用户ID")
    external_userid: Optional[str] = Field(None, description="外部联系人ID")
    change_type: Optional[str] = Field(None, description="变更类型")


# ===== XML解析相关模型 =====

class XmlCallbackMessage(WxKfBaseModel):
    """XML回调消息原始数据"""
    xml_data: Dict[str, Any] = Field(..., description="原始XML数据")
    msg_type: str = Field(..., description="消息类型")
    event_type: Optional[str] = Field(None, description="事件类型")
    info_type: Optional[str] = Field(None, description="信息类型")


# ===== 回调响应模型 =====

class CallbackResponse(WxKfBaseModel):
    """回调响应"""
    code: int = Field(0, description="响应码")
    message: str = Field("success", description="响应消息")


# ===== 消息处理结果模型 =====

class CallbackProcessResult(WxKfBaseModel):
    """回调处理结果"""
    success: bool = Field(..., description="处理是否成功")
    message: str = Field(..., description="处理结果描述")
    msgid: Optional[str] = Field(None, description="消息ID")
    event_type: Optional[str] = Field(None, description="事件类型")
    process_time: Optional[int] = Field(None, description="处理时间戳(毫秒)")