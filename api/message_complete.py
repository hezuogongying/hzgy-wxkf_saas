# -*- coding: utf-8 -*-
"""完整消息管理API"""

from typing import TYPE_CHECKING, Optional

from models.message import (
    SendTextMessageRequest,
    SendImageMessageRequest,
    SendVoiceMessageRequest,
    SendVideoMessageRequest,
    SendFileMessageRequest,
    SendLocationRequest,
    SendMiniProgramRequest,
    SendChannelsShopProductRequest,
    SendChannelsShopOrderRequest,
    SendMergedMsgRequest,
    SendChannelsRequest,
    SendNoteRequest,
    SendMessageResponse,
    SyncMsgRequest,
    SyncMsgResponse,
    SendWelcomeRequest,
    SendWelcomeResponse,
    RecallMessageRequest,
    RecallMessageResponse,
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

if TYPE_CHECKING:
    from wxkf_saas.core.client import WxKfSaasClient


class CompleteMessageApi:
    """完整消息管理API

    提供所有微信客服消息类型的收发、同步等功能
    """

    def __init__(self, client: "WxKfSaasClient"):
        """初始化消息API

        Args:
            client: WxKfSaasClient客户端实例
        """
        self._client = client

    def send_text(
        self,
        corp_id: str,
        touser: str,
        open_kfid: str,
        content: str,
        msgid: Optional[str] = None
    ) -> SendMessageResponse:
        """发送文本消息"""
        request_data = SendTextMessageRequest(
            touser=touser,
            open_kfid=open_kfid,
            msgid=msgid,
            msgtype="text",
            text=TextContent(content=content)
        )

        return self._client._request(
            "POST",
            "/kf/send_msg",
            response_model=SendMessageResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump(exclude_none=True)
        )

    def send_image(
        self,
        corp_id: str,
        touser: str,
        open_kfid: str,
        media_id: str,
        msgid: Optional[str] = None
    ) -> SendMessageResponse:
        """发送图片消息"""
        request_data = SendImageMessageRequest(
            touser=touser,
            open_kfid=open_kfid,
            msgid=msgid,
            msgtype="image",
            image=ImageContent(media_id=media_id)
        )

        return self._client._request(
            "POST",
            "/kf/send_msg",
            response_model=SendMessageResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump(exclude_none=True)
        )

    def send_voice(
        self,
        corp_id: str,
        touser: str,
        open_kfid: str,
        media_id: str,
        msgid: Optional[str] = None
    ) -> SendMessageResponse:
        """发送语音消息"""
        request_data = SendVoiceMessageRequest(
            touser=touser,
            open_kfid=open_kfid,
            msgid=msgid,
            msgtype="voice",
            voice=VoiceContent(media_id=media_id)
        )

        return self._client._request(
            "POST",
            "/kf/send_msg",
            response_model=SendMessageResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump(exclude_none=True)
        )

    def send_video(
        self,
        corp_id: str,
        touser: str,
        open_kfid: str,
        media_id: str,
        msgid: Optional[str] = None
    ) -> SendMessageResponse:
        """发送视频消息"""
        request_data = SendVideoMessageRequest(
            touser=touser,
            open_kfid=open_kfid,
            msgid=msgid,
            msgtype="video",
            video=VideoContent(media_id=media_id)
        )

        return self._client._request(
            "POST",
            "/kf/send_msg",
            response_model=SendMessageResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump(exclude_none=True)
        )

    def send_file(
        self,
        corp_id: str,
        touser: str,
        open_kfid: str,
        media_id: str,
        msgid: Optional[str] = None
    ) -> SendMessageResponse:
        """发送文件消息"""
        request_data = SendFileMessageRequest(
            touser=touser,
            open_kfid=open_kfid,
            msgid=msgid,
            msgtype="file",
            file=FileContent(media_id=media_id)
        )

        return self._client._request(
            "POST",
            "/kf/send_msg",
            response_model=SendMessageResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump(exclude_none=True)
        )

    def send_location(
        self,
        corp_id: str,
        touser: str,
        open_kfid: str,
        latitude: float,
        longitude: float,
        name: Optional[str] = None,
        address: Optional[str] = None,
        msgid: Optional[str] = None
    ) -> SendMessageResponse:
        """发送位置消息"""
        request_data = SendLocationRequest(
            touser=touser,
            open_kfid=open_kfid,
            msgid=msgid,
            msgtype="location",
            location=LocationContent(
                latitude=latitude,
                longitude=longitude,
                name=name,
                address=address
            )
        )

        return self._client._request(
            "POST",
            "/kf/send_msg",
            response_model=SendMessageResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump(exclude_none=True)
        )

    def send_miniprogram(
        self,
        corp_id: str,
        touser: str,
        open_kfid: str,
        title: str,
        appid: str,
        pagepath: str,
        thumb_media_id: Optional[str] = None,
        msgid: Optional[str] = None
    ) -> SendMessageResponse:
        """发送小程序消息"""
        request_data = SendMiniProgramRequest(
            touser=touser,
            open_kfid=open_kfid,
            msgid=msgid,
            msgtype="miniprogram",
            miniprogram=MiniProgramContent(
                title=title,
                appid=appid,
                pagepath=pagepath,
                thumb_media_id=thumb_media_id
            )
        )

        return self._client._request(
            "POST",
            "/kf/send_msg",
            response_model=SendMessageResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump(exclude_none=True)
        )

    def send_channels_shop_product(
        self,
        corp_id: str,
        touser: str,
        open_kfid: str,
        product_id: str,
        head_image: Optional[str] = None,
        title: Optional[str] = None,
        sales_price: Optional[str] = None,
        shop_nickname: Optional[str] = None,
        shop_head_image: Optional[str] = None,
        msgid: Optional[str] = None
    ) -> SendMessageResponse:
        """发送视频号商品消息"""
        request_data = SendChannelsShopProductRequest(
            touser=touser,
            open_kfid=open_kfid,
            msgid=msgid,
            msgtype="channels_shop_product",
            channels_shop_product=ChannelsShopProductContent(
                product_id=product_id,
                head_image=head_image,
                title=title,
                sales_price=sales_price,
                shop_nickname=shop_nickname,
                shop_head_image=shop_head_image
            )
        )

        return self._client._request(
            "POST",
            "/kf/send_msg",
            response_model=SendMessageResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump(exclude_none=True)
        )

    def send_channels_shop_order(
        self,
        corp_id: str,
        touser: str,
        open_kfid: str,
        order_id: str,
        product_titles: Optional[str] = None,
        price_wording: Optional[str] = None,
        state: Optional[str] = None,
        image_url: Optional[str] = None,
        shop_nickname: Optional[str] = None,
        msgid: Optional[str] = None
    ) -> SendMessageResponse:
        """发送视频号订单消息"""
        request_data = SendChannelsShopOrderRequest(
            touser=touser,
            open_kfid=open_kfid,
            msgid=msgid,
            msgtype="channels_shop_order",
            channels_shop_order=ChannelsShopOrderContent(
                order_id=order_id,
                product_titles=product_titles,
                price_wording=price_wording,
                state=state,
                image_url=image_url,
                shop_nickname=shop_nickname
            )
        )

        return self._client._request(
            "POST",
            "/kf/send_msg",
            response_model=SendMessageResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump(exclude_none=True)
        )

    def send_merged_msg(
        self,
        corp_id: str,
        touser: str,
        open_kfid: str,
        title: str,
        item: list,
        msgid: Optional[str] = None
    ) -> SendMessageResponse:
        """发送聊天记录消息"""
        request_data = SendMergedMsgRequest(
            touser=touser,
            open_kfid=open_kfid,
            msgid=msgid,
            msgtype="merged_msg",
            merged_msg=MergedMsgContent(
                title=title,
                item=item
            )
        )

        return self._client._request(
            "POST",
            "/kf/send_msg",
            response_model=SendMessageResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump(exclude_none=True)
        )

    def send_channels(
        self,
        corp_id: str,
        touser: str,
        open_kfid: str,
        sub_type: int,
        nickname: Optional[str] = None,
        title: Optional[str] = None,
        msgid: Optional[str] = None
    ) -> SendMessageResponse:
        """发送视频号消息"""
        request_data = SendChannelsRequest(
            touser=touser,
            open_kfid=open_kfid,
            msgid=msgid,
            msgtype="channels",
            channels=ChannelsContent(
                sub_type=sub_type,
                nickname=nickname,
                title=title
            )
        )

        return self._client._request(
            "POST",
            "/kf/send_msg",
            response_model=SendMessageResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump(exclude_none=True)
        )

    def send_note(
        self,
        corp_id: str,
        touser: str,
        open_kfid: str,
        msgid: Optional[str] = None
    ) -> SendMessageResponse:
        """发送笔记消息"""
        request_data = SendNoteRequest(
            touser=touser,
            open_kfid=open_kfid,
            msgid=msgid,
            msgtype="note"
        )

        return self._client._request(
            "POST",
            "/kf/send_msg",
            response_model=SendMessageResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump(exclude_none=True)
        )

    def sync_msg(
        self,
        corp_id: str,
        cursor: Optional[str] = None,
        token: Optional[str] = None,
        limit: int = 1000,
        voice_format: int = 0,
        open_kfid: Optional[str] = None
    ) -> SyncMsgResponse:
        """同步消息

        获取客户主动发送的消息、发送消息失败事件、客户点击菜单消息的回复消息等。

        Args:
            corp_id: 企业ID
            cursor: 上一次调用时返回的next_cursor,第一次拉取可以不填
            token: 回调事件返回的token字段,10分钟内有效
            limit: 期望请求的数据量,默认和最大值都为1000
            voice_format: 语音消息类型,0-Amr 1-Silk,默认0
            open_kfid: 指定拉取某个客服账号的消息

        Returns:
            SyncMsgResponse: 消息列表和分页信息

        Raises:
            WxKfApiError: API调用失败
        """
        request_data = SyncMsgRequest(
            cursor=cursor,
            token=token,
            limit=limit,
            voice_format=voice_format,
            open_kfid=open_kfid
        )

        return self._client._request(
            "POST",
            "/kf/sync_msg",
            response_model=SyncMsgResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump(exclude_none=True)
        )

    def send_welcome(
        self,
        corp_id: str,
        welcome_code: str,
        msgtype: str,
        content: str = None,
        media_id: str = None,
        title: str = None,
        appid: str = None,
        pagepath: str = None,
        thumb_media_id: str = None
    ) -> SendWelcomeResponse:
        """发送欢迎语

        当客户进入会话且满足条件时,通过welcome_code发送欢迎语。

        Args:
            corp_id: 企业ID
            welcome_code: 通过进入会话事件获取的welcome_code
            msgtype: 消息类型(text/image/miniprogram等)
            content: 文本内容(msgtype=text时必填)
            media_id: 媒体文件ID(msgtype=image等时必填)
            title: 标题(msgtype=miniprogram时必填)
            appid: 小程序appid(msgtype=miniprogram时必填)
            pagepath: 小程序页面路径(msgtype=miniprogram时必填)
            thumb_media_id: 小程序封面mediaid(msgtype=miniprogram时可选)

        Returns:
            SendWelcomeResponse: 发送结果
        """
        request_data = SendWelcomeRequest(
            welcome_code=welcome_code,
            msgtype=msgtype
        )

        if msgtype == "text" and content:
            request_data.text = TextContent(content=content)
        elif msgtype == "image" and media_id:
            request_data.image = ImageContent(media_id=media_id)
        elif msgtype == "miniprogram" and title and appid and pagepath:
            request_data.miniprogram = MiniProgramContent(
                title=title,
                appid=appid,
                pagepath=pagepath,
                thumb_media_id=thumb_media_id
            )

        return self._client._request(
            "POST",
            "/kf/send_msg_on_event",
            response_model=SendWelcomeResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump(exclude_none=True)
        )

    def recall(
        self,
        corp_id: str,
        msgid: str
    ) -> RecallMessageResponse:
        """撤回消息

        Args:
            corp_id: 企业ID
            msgid: 要撤回的消息ID

        Returns:
            RecallMessageResponse: 撤回结果
        """
        request_data = RecallMessageRequest(msgid=msgid)

        return self._client._request(
            "POST",
            "/kf/recall_msg",
            response_model=RecallMessageResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump()
        )