# -*- coding: utf-8 -*-
"""素材管理相关数据模型"""

from pydantic import Field
from wxkf_saas.models.base import WxKfBaseModel, SuccessResponse


class UploadMediaResponse(SuccessResponse):
    """上传临时素材响应"""
    type: str = Field(..., description="素材类型,image/voice/video/file")
    media_id: str = Field(..., description="媒体文件ID")
    created_at: int = Field(..., description="媒体文件上传时间戳")


class GetMediaResponse(WxKfBaseModel):
    """获取临时素材响应(文件流)"""
    content: bytes = Field(..., description="文件内容")
    content_type: str = Field(..., description="文件类型")
    filename: str = Field(None, description="文件名")
