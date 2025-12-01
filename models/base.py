# -*- coding: utf-8 -*-
"""基础数据模型"""

from typing import Optional
from pydantic import BaseModel, Field


class WxKfBaseModel(BaseModel):
    """微信客服基础模型"""

    class Config:
        # 支持从ORM读取
        from_attributes = True
        # 使用枚举值
        use_enum_values = True


class ErrorResponse(WxKfBaseModel):
    """微信API错误响应"""
    errcode: int = Field(..., description="错误码")
    errmsg: str = Field(..., description="错误信息")


class SuccessResponse(WxKfBaseModel):
    """成功响应"""
    errcode: int = Field(0, description="错误码,0表示成功")
    errmsg: str = Field("ok", description="错误信息")
