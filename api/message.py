# -*- coding: utf-8 -*-
"""消息管理API"""

from typing import TYPE_CHECKING, Optional

from wxkf_saas.models.message import (
    SendTextMessageRequest,
    SendImageMessageRequest,
    SendVoiceMessageRequest,
    SendVideoMessageRequest,
    SendFileMessageRequest,
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
)

if TYPE_CHECKING:
    from wxkf_saas.core.client import WxKfSaasClient


class MessageApi:
    """消息管理API

    提供消息收发、同步等功能
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
        """发送文本消息

        Args:
            corp_id: 企业ID
            touser: 接收消息的客户UserID
            open_kfid: 发送消息的客服账号ID
            content: 文本内容,最长不超过2048个字节
            msgid: 消息ID(可选),用于去重

        Returns:
            SendMessageResponse: 发送结果,包含消息ID

        Raises:
            WxKfApiError: API调用失败

        文档: https://developer.work.weixin.qq.com/document/path/94744
        """
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
        """发送图片消息

        Args:
            corp_id: 企业ID
            touser: 接收消息的客户UserID
            open_kfid: 发送消息的客服账号ID
            media_id: 图片媒体文件ID
            msgid: 消息ID(可选),用于去重

        Returns:
            SendMessageResponse: 发送结果

        Raises:
            WxKfApiError: API调用失败
        """
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
        """发送语音消息

        Args:
            corp_id: 企业ID
            touser: 接收消息的客户UserID
            open_kfid: 发送消息的客服账号ID
            media_id: 语音媒体文件ID
            msgid: 消息ID(可选)

        Returns:
            SendMessageResponse: 发送结果

        Raises:
            WxKfApiError: API调用失败
        """
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
        """发送视频消息

        Args:
            corp_id: 企业ID
            touser: 接收消息的客户UserID
            open_kfid: 发送消息的客服账号ID
            media_id: 视频媒体文件ID
            msgid: 消息ID(可选)

        Returns:
            SendMessageResponse: 发送结果

        Raises:
            WxKfApiError: API调用失败
        """
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
        """发送文件消息

        Args:
            corp_id: 企业ID
            touser: 接收消息的客户UserID
            open_kfid: 发送消息的客服账号ID
            media_id: 文件媒体文件ID
            msgid: 消息ID(可选)

        Returns:
            SendMessageResponse: 发送结果

        Raises:
            WxKfApiError: API调用失败
        """
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

        说明:
            1. 不支持获取通过接口发送的消息
            2. 可能会出现返回条数少于limit的情况,需结合has_more字段判断是否继续请求
            3. 强烈建议对next_cursor入库保存,避免因意外丢失导致必须从头拉取

        文档: https://developer.work.weixin.qq.com/document/path/94670
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
        media_id: str = None
    ) -> SendWelcomeResponse:
        """发送欢迎语

        当客户进入会话且满足条件时,通过welcome_code发送欢迎语。

        Args:
            corp_id: 企业ID
            welcome_code: 通过进入会话事件获取的welcome_code
            msgtype: 消息类型(text/image等)
            content: 文本内容(msgtype=text时必填)
            media_id: 媒体文件ID(msgtype=image等时必填)

        Returns:
            SendWelcomeResponse: 发送结果

        Raises:
            WxKfApiError: API调用失败

        说明:
            1. 满足条件:用户在过去48小时里未收过欢迎语,且未向客服发过消息
            2. welcome_code有效期48小时,过期后不可使用

        文档: https://developer.work.weixin.qq.com/document/path/95123
        """
        request_data = SendWelcomeRequest(
            welcome_code=welcome_code,
            msgtype=msgtype
        )

        if msgtype == "text" and content:
            request_data.text = TextContent(content=content)
        elif msgtype == "image" and media_id:
            request_data.image = ImageContent(media_id=media_id)

        return self._client._request(
            "POST",
            "/kf/send_msg_on_event",
            response_model=SendWelcomeResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump(exclude_none=True)
        )

    def recall(self, corp_id: str, msgid: str) -> RecallMessageResponse:
        """撤回消息

        Args:
            corp_id: 企业ID
            msgid: 要撤回的消息ID

        Returns:
            RecallMessageResponse: 撤回结果

        Raises:
            WxKfApiError: API调用失败

        说明:
            1. 只能撤回通过接口发送的消息
            2. 撤回消息后,客户会看到"对方撤回了一条消息"的提示

        文档: https://developer.work.weixin.qq.com/document/path/96020
        """
        request_data = RecallMessageRequest(msgid=msgid)

        return self._client._request(
            "POST",
            "/kf/recall_msg",
            response_model=RecallMessageResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump()
        )
