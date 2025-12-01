# -*- coding: utf-8 -*-
"""素材管理路由"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from pydantic import BaseModel

from core.database import get_async_db
from core.client import WxKfSaasClient
from core.config import WxKfSaasConfig
from api.media import MediaApi
from models.media import UploadMediaResponse, GetMediaResponse

router = APIRouter(prefix="/api/media", tags=["素材管理"])


# 请求模型
class UploadMediaRequestModel(BaseModel):
    """上传素材请求模型"""
    corp_id: str
    media_type: str
    # 文件上传通过 form-data 处理，不在请求体中


# 响应模型
class APIResponse(BaseModel):
    """API通用响应模型"""
    code: int = 0
    message: str = "success"
    data: dict = {}


async def get_client() -> WxKfSaasClient:
    """获取微信客服客户端实例"""
    config = WxKfSaasConfig()
    return WxKfSaasClient(config)


@router.post("/upload", response_model=UploadMediaResponse, summary="上传临时素材")
async def upload_media(
    corp_id: str = Query(..., description="企业ID"),
    media_type: str = Query(..., description="媒体文件类型"),
    file: UploadFile = File(..., description="媒体文件"),
    client: WxKfSaasClient = Depends(get_client)
):
    """上传临时素材

    上传临时素材，支持图片、语音、视频、文件等类型。

    Args:
        corp_id: 企业ID
        media_type: 媒体文件类型(image/voice/video/file)
        file: 上传的媒体文件
        client: 微信客服客户端实例

    Returns:
        UploadMediaResponse: 上传结果，包含media_id

    Raises:
        HTTPException: API调用失败
    """
    try:
        media_api = MediaApi(client)

        # 检查文件类型是否匹配
        allowed_types = {
            "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
            "voice": [".amr", ".mp3", ".silk"],
            "video": [".mp4", ".mov"],
            "file": [".doc", ".docx", ".pdf", ".txt", ".zip", ".rar"]
        }

        file_ext = ""
        if hasattr(file, 'filename') and file.filename:
            file_ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""

        if media_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"不支持的媒体类型: {media_type}")

        if media_type not in allowed_types or file_ext not in allowed_types[media_type]:
            raise HTTPException(
                status_code=400,
                detail=f"文件扩展名 {file_ext} 不匹配媒体类型 {media_type}"
            )

        # 读取文件内容
        file_content = await file.read()

        response = await media_api.upload(
            corp_id=corp_id,
            media_type=media_type,
            file_obj=file_content,
            filename=file.filename if file.filename else "unknown"
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{media_id}", response_model=GetMediaResponse, summary="获取临时素材")
async def get_media(
    media_id: str,
    corp_id: str = Query(..., description="企业ID"),
    client: WxKfSaasClient = Depends(get_client)
):
    """获取临时素材

    获取临时素材内容，返回原始文件流。

    Args:
        media_id: 媒体文件ID
        corp_id: 企业ID
        client: 微信客服客户端实例

    Returns:
        媒体文件流

    Raises:
        HTTPException: API调用失败
    """
    try:
        media_api = MediaApi(client)
        response = await media_api.get(
            corp_id=corp_id,
            media_id=media_id,
            stream=True  # 返回原始响应
        )

        # 返回文件流
        if response.headers.get("content-type"):
            from fastapi.responses import StreamingResponse
            return StreamingResponse(
                content=response.iter_bytes(),
                media_type=response.headers["content-type"],
                headers={
                    "Content-Disposition": f'attachment; filename="{media_id}"'
                }
            )
        else:
            # 如果没有流式响应，返回JSON
            return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{media_id}", summary="下载临时素材")
async def download_media(
    media_id: str,
    corp_id: str = Query(..., description="企业ID"),
    filename: Optional[str] = Query(None, description="文件名"),
    client: WxKfSaasClient = Depends(get_client)
):
    """下载临时素材

    下载临时素材，提供文件下载功能。

    Args:
        media_id: 媒体文件ID
        corp_id: 企业ID
        filename: 自定义文件名（可选）
        client: 微信客服客户端实例

    Returns:
        文件下载响应

    Raises:
        HTTPException: API调用失败
    """
    try:
        media_api = MediaApi(client)
        response = await media_api.get(
            corp_id=corp_id,
            media_id=media_id,
            stream=True
        )

        from fastapi.responses import StreamingResponse

        # 确定文件名
        download_filename = filename if filename else media_id
        if response.headers.get("content-type"):
            content_type = response.headers["content-type"]
        else:
            # 根据media_id推断文件类型
            if media_id.startswith("image"):
                content_type = "image/jpeg"
            elif media_id.startswith("voice"):
                content_type = "audio/amr"
            elif media_id.startswith("video"):
                content_type = "video/mp4"
            else:
                content_type = "application/octet-stream"

        return StreamingResponse(
            content=response.iter_bytes(),
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{download_filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))