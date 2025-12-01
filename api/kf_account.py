# -*- coding: utf-8 -*-
"""客服账号管理API"""

from typing import TYPE_CHECKING, List

from wxkf_api.models.kf_account import (
    AddKfAccountRequest,
    AddKfAccountResponse,
    UpdateKfAccountRequest,
    UpdateKfAccountResponse,
    DeleteKfAccountRequest,
    DeleteKfAccountResponse,
    GetKfAccountListResponse,
    GetAccountLinkRequest,
    GetAccountLinkResponse,
    GetCustomerInfoRequest,
    GetCustomerInfoResponse,
)

if TYPE_CHECKING:
    from wxkf_api.core.client import WxKfSaasClient


class KfAccountApi:
    """客服账号管理API

    提供客服账号的增删改查等功能
    """

    def __init__(self, client: "WxKfSaasClient"):
        """初始化客服账号API

        Args:
            client: WxKfSaasClient客户端实例
        """
        self._client = client

    def add(self, corp_id: str, name: str, media_id: str) -> AddKfAccountResponse:
        """添加客服账号

        添加客服账号,并可设置客服名称和头像。目前一家企业最多可添加5000个客服账号。

        Args:
            corp_id: 企业ID
            name: 客服账号名称,不多于16个字符
            media_id: 客服头像临时素材ID,可调用上传临时素材接口获取

        Returns:
            AddKfAccountResponse: 包含新创建的客服账号ID

        Raises:
            WxKfApiError: API调用失败

        文档: https://developer.work.weixin.qq.com/document/path/94747
        """
        request_data = AddKfAccountRequest(name=name, media_id=media_id)

        return self._client._request(
            "POST",
            "/kf/account/add",
            response_model=AddKfAccountResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump()
        )

    def update(
        self,
        corp_id: str,
        open_kfid: str,
        name: str = None,
        media_id: str = None
    ) -> UpdateKfAccountResponse:
        """修改客服账号

        Args:
            corp_id: 企业ID
            open_kfid: 客服账号ID
            name: 客服账号名称(可选)
            media_id: 客服头像临时素材ID(可选)

        Returns:
            UpdateKfAccountResponse: 修改结果

        Raises:
            WxKfApiError: API调用失败

        文档: https://developer.work.weixin.qq.com/document/path/94750
        """
        request_data = UpdateKfAccountRequest(
            open_kfid=open_kfid,
            name=name,
            media_id=media_id
        )

        return self._client._request(
            "POST",
            "/kf/account/update",
            response_model=UpdateKfAccountResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump(exclude_none=True)
        )

    def delete(self, corp_id: str, open_kfid: str) -> DeleteKfAccountResponse:
        """删除客服账号

        Args:
            corp_id: 企业ID
            open_kfid: 客服账号ID

        Returns:
            DeleteKfAccountResponse: 删除结果

        Raises:
            WxKfApiError: API调用失败

        文档: https://developer.work.weixin.qq.com/document/path/94749
        """
        request_data = DeleteKfAccountRequest(open_kfid=open_kfid)

        return self._client._request(
            "POST",
            "/kf/account/del",
            response_model=DeleteKfAccountResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump()
        )

    def list(self, corp_id: str) -> GetKfAccountListResponse:
        """获取客服账号列表

        Args:
            corp_id: 企业ID

        Returns:
            GetKfAccountListResponse: 客服账号列表

        Raises:
            WxKfApiError: API调用失败

        文档: https://developer.work.weixin.qq.com/document/path/94746
        """
        return self._client._request(
            "GET",
            "/kf/account/list",
            response_model=GetKfAccountListResponse,
            corp_id=corp_id
        )

    def get_account_link(
        self,
        corp_id: str,
        open_kfid: str,
        scene: str = None
    ) -> GetAccountLinkResponse:
        """获取客服账号链接

        企业可通过此接口获取带有不同参数的客服链接。

        Args:
            corp_id: 企业ID
            open_kfid: 客服账号ID
            scene: 场景值,由开发者自定义,不多于32字节

        Returns:
            GetAccountLinkResponse: 包含客服链接

        Raises:
            WxKfApiError: API调用失败

        说明:
            1. 若scene非空,返回的客服链接可拼接scene_param参数使用
            2. 用户进入会话事件会将scene_param原样返回
            3. 返回的客服链接不能修改或复制参数到其他链接使用

        文档: https://developer.work.weixin.qq.com/document/path/94751
        """
        request_data = GetAccountLinkRequest(open_kfid=open_kfid, scene=scene)

        return self._client._request(
            "POST",
            "/kf/add_contact_way",
            response_model=GetAccountLinkResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump(exclude_none=True)
        )

    def get_customer_info(
        self,
        corp_id: str,
        external_userid_list: List[str],
        need_enter_session_context: int = 0
    ) -> GetCustomerInfoResponse:
        """获取客户基础信息

        批量获取微信客户的基础信息,包括昵称、头像、unionid等。

        Args:
            corp_id: 企业ID
            external_userid_list: 客户UserID列表
            need_enter_session_context: 是否需要返回进入会话上下文,0-不返回 1-返回

        Returns:
            GetCustomerInfoResponse: 客户信息列表

        Raises:
            WxKfApiError: API调用失败

        说明:
            1. external_userid需为最近48小时内有触发进入会话事件或发过消息的客户
            2. 第三方不可获取头像和性别,头像为空,性别统一返回0
            3. unionid需要绑定微信开发者账号才能获取

        文档: https://developer.work.weixin.qq.com/document/path/95122
        """
        request_data = GetCustomerInfoRequest(
            external_userid_list=external_userid_list,
            need_enter_session_context=need_enter_session_context
        )

        return self._client._request(
            "POST",
            "/kf/customer/batchget",
            response_model=GetCustomerInfoResponse,
            corp_id=corp_id,
            json_data=request_data.model_dump()
        )
