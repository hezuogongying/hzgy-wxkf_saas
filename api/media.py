# -*- coding: utf-8 -*-
"""素材管理API"""

from typing import TYPE_CHECKING, BinaryIO
from pathlib import Path

from models.media import UploadMediaResponse, GetMediaResponse

if TYPE_CHECKING:
    from core.client import WxKfSaasClient


class MediaApi:
    """素材管理API

    提供临时素材的上传和下载功能
    """

    def __init__(self, client: "WxKfSaasClient"):
        """初始化素材API

        Args:
            client: WxKfSaasClient客户端实例
        """
        self._client = client

    def upload(
        self,
        corp_id: str,
        media_type: str,
        file_path: str = None,
        file_obj: BinaryIO = None,
        filename: str = None
    ) -> UploadMediaResponse:
        """上传临时素材

        用于上传图片、语音、视频、文件等媒体文件,获取media_id用于发送消息。

        Args:
            corp_id: 企业ID
            media_type: 媒体文件类型,分别有image/voice/video/file
            file_path: 文件路径(二选一)
            file_obj: 文件对象(二选一)
            filename: 文件名(当使用file_obj时需要提供)

        Returns:
            UploadMediaResponse: 上传结果,包含media_id

        Raises:
            WxKfApiError: API调用失败
            ValueError: 参数错误

        说明:
            1. 图片(image):2MB,支持JPG/PNG格式
            2. 语音(voice):2MB,播放长度不超过60s,支持AMR/SILK格式
            3. 视频(video):10MB,支持MP4格式
            4. 文件(file):20MB
            5. media_id在上传后3天内有效

        文档: https://developer.work.weixin.qq.com/document/path/93349
        """
        if file_path:
            # 从文件路径读取
            path = Path(file_path)
            if not path.exists():
                raise ValueError(f"File not found: {file_path}")

            with open(file_path, 'rb') as f:
                files = {
                    'media': (path.name, f, self._get_content_type(path.suffix))
                }
                return self._upload(corp_id, media_type, files)

        elif file_obj and filename:
            # 从文件对象读取
            files = {
                'media': (filename, file_obj, self._get_content_type(Path(filename).suffix))
            }
            return self._upload(corp_id, media_type, files)

        else:
            raise ValueError("Either file_path or (file_obj and filename) must be provided")

    def _upload(self, corp_id: str, media_type: str, files: dict) -> UploadMediaResponse:
        """执行上传操作

        Args:
            corp_id: 企业ID
            media_type: 媒体文件类型
            files: 文件数据

        Returns:
            UploadMediaResponse: 上传结果
        """
        return self._client._request(
            "POST",
            "/cgi-bin/media/upload",
            response_model=UploadMediaResponse,
            corp_id=corp_id,
            params={"type": media_type},
            files=files
        )

    def download(
        self,
        corp_id: str,
        media_id: str,
        save_path: str = None
    ) -> GetMediaResponse:
        """获取临时素材

        下载之前上传的临时素材。

        Args:
            corp_id: 企业ID
            media_id: 媒体文件ID
            save_path: 保存路径(可选),如果提供则保存到文件

        Returns:
            GetMediaResponse: 媒体文件内容

        Raises:
            WxKfApiError: API调用失败

        文档: https://developer.work.weixin.qq.com/document/path/93349
        """
        response = self._client._request(
            "GET",
            "/cgi-bin/media/get",
            response_model=None,  # 返回的是文件流,不解析为JSON
            corp_id=corp_id,
            params={"media_id": media_id},
            stream=True
        )

        content = response.content
        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        filename = self._extract_filename(response.headers.get('Content-Disposition', ''))

        # 如果提供了保存路径,则保存文件
        if save_path:
            path = Path(save_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'wb') as f:
                f.write(content)

        return GetMediaResponse(
            content=content,
            content_type=content_type,
            filename=filename
        )

    def _get_content_type(self, suffix: str) -> str:
        """根据文件后缀获取Content-Type

        Args:
            suffix: 文件后缀(如.jpg)

        Returns:
            str: Content-Type
        """
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.mp4': 'video/mp4',
            '.amr': 'audio/amr',
            '.silk': 'audio/silk',
            '.mp3': 'audio/mp3',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        }
        return content_types.get(suffix.lower(), 'application/octet-stream')

    def _extract_filename(self, content_disposition: str) -> str:
        """从Content-Disposition头中提取文件名

        Args:
            content_disposition: Content-Disposition头的值

        Returns:
            str: 文件名
        """
        if not content_disposition:
            return None

        # Content-Disposition: attachment; filename="example.jpg"
        parts = content_disposition.split(';')
        for part in parts:
            part = part.strip()
            if part.startswith('filename='):
                filename = part[9:].strip('"')
                return filename

        return None
