# -*- coding: utf-8 -*-
"""客户联系API模块"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from .base import BaseApi


# 请求和响应模型
class ContactAvatar(BaseModel):
    """客户头像信息"""
    media_id: str = Field(..., description="头像素材id")


class ContactProfile(BaseModel):
    """客户联系Profile配置"""
    avatar: Optional[ContactAvatar] = Field(None, description="客户头像")
    handle: Optional[str] = Field(None, max_length=12, description="客户名称，12个UTF-8字符，不能包含特殊字符")
    description: Optional[str] = Field(None, max_length=36, description="客户简介，不能包含特殊字符<>*&")
    image: Optional[str] = Field(None, description="客户企业主体Logo图片url")
    mobile: Optional[str] = Field(None, pattern=r'^[0-9]{6,20}$', description="客服电话，6-20位数字")
    email: Optional[str] = Field(None, description="客服邮箱")
    biz_url: Optional[str] = Field(None, description="客服页面跳转链接，仅支持小程序的scheme链接")


class SetContactProfileRequest(BaseModel):
    """设置客户Profile请求"""
    userid: str = Field(..., description="企业成员的userid")
    external_userid: str = Field(..., description="外部联系人userid")
    profile: ContactProfile = Field(..., description="Profile配置信息")


class SetContactProfileResponse(BaseModel):
    """设置客户Profile响应"""
    errcode: int
    errmsg: str


class ContactApi(BaseApi):
    """客户联系API类"""

    def set_contact_profile(self, corp_id: str, userid: str, external_userid: str,
                           avatar: Optional[str] = None, handle: Optional[str] = None,
                           description: Optional[str] = None, image: Optional[str] = None,
                           mobile: Optional[str] = None, email: Optional[str] = None,
                           biz_url: Optional[str] = None) -> SetContactProfileResponse:
        """
        配置客户联系Profile

        该接口用于配置指定成员添加外部联系人时，自动对外部联系人展示的Profile信息。
        如果未配置，则展示企业的Profile信息。

        Args:
            corp_id: 企业ID
            userid: 企业成员的userid
            external_userid: 外部联系人userid
            avatar: 头像素材id
            handle: 客户名称，12个UTF-8字符
            description: 客户简介，36个UTF-8字符
            image: 企业主体Logo图片url
            mobile: 客服电话，6-20位数字
            email: 客服邮箱
            biz_url: 客服页面跳转链接

        Returns:
            SetContactProfileResponse: 配置结果

        Raises:
            WxKfApiError: API调用失败

        Doc:
            https://developer.work.weixin.qq.com/document/31441
        """
        # 构建Profile数据
        profile_data: Dict[str, Any] = {}

        if avatar:
            profile_data["avatar"] = {"media_id": avatar}
        if handle is not None:
            profile_data["handle"] = handle
        if description is not None:
            profile_data["description"] = description
        if image is not None:
            profile_data["image"] = image
        if mobile is not None:
            profile_data["mobile"] = mobile
        if email is not None:
            profile_data["email"] = email
        if biz_url is not None:
            profile_data["biz_url"] = biz_url

        # 构建请求数据
        request_data = {
            "userid": userid,
            "external_userid": external_userid,
            "profile": profile_data
        }

        return self._client._request(
            "POST",
            "/cgi-bin/kf/setcontactprofile",
            json_data=request_data,
            corp_id=corp_id,
            response_model=SetContactProfileResponse
        )

    def get_contact_profile(self, corp_id: str, userid: str, external_userid: str):
        """
        获取客户联系Profile

        Args:
            corp_id: 企业ID
            userid: 企业成员的userid
            external_userid: 外部联系人userid

        Returns:
            Dict: Profile配置信息

        Raises:
            WxKfApiError: API调用失败
        """
        request_data = {
            "userid": userid,
            "external_userid": external_userid
        }

        return self._client._request(
            "POST",
            "/cgi-bin/kf/getcontactprofile",
            json_data=request_data,
            corp_id=corp_id
        )

    def batch_get_contact_profile(self, corp_id: str, userid: str,
                                 external_userid_list: List[str]) -> Dict[str, Any]:
        """
        批量获取客户联系Profile

        Args:
            corp_id: 企业ID
            userid: 企业成员的userid
            external_userid_list: 外部联系人userid列表，最多100个

        Returns:
            Dict: 批量查询结果

        Raises:
            WxKfApiError: API调用失败
        """
        request_data = {
            "userid": userid,
            "external_userid_list": external_userid_list
        }

        return self._client._request(
            "POST",
            "/cgi-bin/kf/batch/getcontactprofile",
            json_data=request_data,
            corp_id=corp_id
        )