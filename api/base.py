# -*- coding: utf-8 -*-
"""API基类模块"""

from typing import Optional, Dict, Any, Type, TypeVar
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.client import WxKfSaasClient

# 定义泛型类型变量
T = TypeVar("T", bound=BaseModel)


class BaseApi:
    """API基类

    所有API类的基类，提供基础的客户端访问功能
    """

    def __init__(self, client: WxKfSaasClient):
        """初始化API基类

        Args:
            client: 微信客服SaaS客户端实例
        """
        self._client = client
        self._http_client = client._http_client

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
        corp_id: Optional[str] = None,
        use_provider_token: bool = False,
        use_suite_token: bool = False
    ) -> Optional[T]:
        """发起HTTP请求的便捷方法

        Args:
            method: HTTP方法 (GET/POST)
            endpoint: API端点路径
            params: URL查询参数
            json_data: JSON请求数据
            files: 上传文件数据
            response_model: 响应模型类
            corp_id: 企业ID（多租户使用）
            use_provider_token: 是否使用服务商Token
            use_suite_token: 是否使用套件Token

        Returns:
            解析后的响应对象
        """
        return self._client._request(
            method=method,
            endpoint=endpoint,
            params=params,
            json_data=json_data,
            files=files,
            response_model=response_model,
            corp_id=corp_id,
            use_provider_token=use_provider_token,
            use_suite_token=use_suite_token
        )