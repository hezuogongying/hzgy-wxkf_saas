# -*- coding: utf-8 -*-
"""客服账号相关数据模型"""

from typing import Optional, List
from pydantic import Field
from wxkf_api.models.base import WxKfBaseModel, SuccessResponse


# ===== 请求模型 =====

class AddKfAccountRequest(WxKfBaseModel):
    """添加客服账号请求"""
    name: str = Field(..., max_length=16, description="客服名称,不多于16个字符")
    media_id: str = Field(..., max_length=128, description="客服头像临时素材ID,不多于128个字节")


class UpdateKfAccountRequest(WxKfBaseModel):
    """修改客服账号请求"""
    open_kfid: str = Field(..., description="客服账号ID")
    name: Optional[str] = Field(None, max_length=16, description="客服名称")
    media_id: Optional[str] = Field(None, max_length=128, description="客服头像临时素材ID")


class DeleteKfAccountRequest(WxKfBaseModel):
    """删除客服账号请求"""
    open_kfid: str = Field(..., description="客服账号ID")


class GetAccountLinkRequest(WxKfBaseModel):
    """获取客服账号链接请求"""
    open_kfid: str = Field(..., description="客服账号ID")
    scene: Optional[str] = Field(None, max_length=32, description="场景值,不多于32字节")


# ===== 响应模型 =====

class AddKfAccountResponse(SuccessResponse):
    """添加客服账号响应"""
    open_kfid: str = Field(..., description="新创建的客服账号ID")


class UpdateKfAccountResponse(SuccessResponse):
    """修改客服账号响应"""
    pass


class DeleteKfAccountResponse(SuccessResponse):
    """删除客服账号响应"""
    pass


class KfAccount(WxKfBaseModel):
    """客服账号信息"""
    open_kfid: str = Field(..., description="客服账号ID")
    name: str = Field(..., description="客服账号名称")
    avatar: str = Field(..., description="客服账号头像URL")


class GetKfAccountListResponse(SuccessResponse):
    """获取客服账号列表响应"""
    account_list: List[KfAccount] = Field(default_factory=list, description="客服账号列表")


class GetAccountLinkResponse(SuccessResponse):
    """获取客服账号链接响应"""
    url: str = Field(..., description="客服链接")


# ===== 客户信息相关模型 =====

class CustomerEnterSessionContext(WxKfBaseModel):
    """客户进入会话上下文"""
    scene: Optional[str] = Field(None, description="场景值")
    scene_param: Optional[str] = Field(None, description="场景参数")


class CustomerInfo(WxKfBaseModel):
    """客户基础信息"""
    external_userid: str = Field(..., description="客户UserID")
    nickname: Optional[str] = Field(None, description="客户昵称")
    avatar: Optional[str] = Field(None, description="客户头像URL")
    gender: Optional[int] = Field(None, description="性别,0-未知 1-男 2-女")
    unionid: Optional[str] = Field(None, description="客户UnionID")
    enter_session_context: Optional[CustomerEnterSessionContext] = Field(
        None,
        description="客户48小时内最后一次进入会话的上下文信息"
    )


class GetCustomerInfoRequest(WxKfBaseModel):
    """获取客户基础信息请求"""
    external_userid_list: List[str] = Field(..., description="客户UserID列表")
    need_enter_session_context: int = Field(
        0,
        description="是否需要返回进入会话上下文,0-不返回 1-返回"
    )


class GetCustomerInfoResponse(SuccessResponse):
    """获取客户基础信息响应"""
    customer_list: List[CustomerInfo] = Field(default_factory=list, description="客户信息列表")
    invalid_external_userid: List[str] = Field(
        default_factory=list,
        description="无效的external_userid列表"
    )
