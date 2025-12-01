# -*- coding: utf-8 -*-
"""微信客服SaaS API核心客户端"""

import httpx
from typing import Type, TypeVar, Optional, Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session

from wxkf_api.core.config import WxKfSaasConfig
from wxkf_api.core.token_manager import MultiTenantTokenManager, TokenType
from wxkf_api.core.exceptions import WxKfApiError
from wxkf_api.models.base import ErrorResponse

# 定义泛型类型变量
T = TypeVar("T", bound=BaseModel)


class WxKfSaasClient:
    """微信客服SaaS API客户端

    负责发起HTTP请求并处理响应,支持多租户
    """

    BASE_URL = "https://qyapi.weixin.qq.com/cgi-bin"

    def __init__(
        self,
        config: WxKfSaasConfig,
        db_session: Session,
        redis_client=None
    ):
        """初始化客户端

        Args:
            config: SaaS配置对象
            db_session: 数据库会话
            redis_client: Redis客户端(可选)
        """
        self.config = config
        self.db = db_session
        self._http_client = httpx.Client(timeout=30.0)

        # 初始化Token管理器
        self.token_manager = MultiTenantTokenManager(
            config=config,
            db_session=db_session,
            redis_client=redis_client
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        response_model: Type[T],
        corp_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        use_suite_token: bool = False,
        use_provider_token: bool = False,
        **kwargs
    ) -> T:
        """发起API请求

        Args:
            method: HTTP方法 ('GET', 'POST'等)
            endpoint: API端点路径 (如 '/kf/account/list')
            response_model: 期望的Pydantic响应模型
            corp_id: 企业ID (单体模式不需要)
            params: 查询参数
            json_data: POST请求的JSON body
            files: 文件上传数据
            use_suite_token: 是否使用suite_access_token
            use_provider_token: 是否使用provider_access_token
            **kwargs: 其他请求参数

        Returns:
            解析后的Pydantic模型实例

        Raises:
            WxKfApiError: API返回错误
        """
        url = f"{self.BASE_URL}{endpoint}"

        # 获取Token
        if use_provider_token:
            token = self.token_manager.get_provider_access_token()
            token_param = "provider_access_token"
        elif use_suite_token:
            token = self.token_manager.get_suite_access_token()
            token_param = "suite_access_token"
        else:
            if not corp_id:
                raise ValueError("corp_id is required for corp access token")
            token = self.token_manager.get_corp_access_token(corp_id)
            token_param = "access_token"

        # 构建请求参数
        request_params = params or {}
        request_params[token_param] = token

        request_kwargs = {
            "method": method,
            "url": url,
            "params": request_params,
            **kwargs
        }

        # 处理文件上传
        if files:
            request_kwargs["files"] = files
        elif json_data is not None:
            request_kwargs["json"] = json_data

        # 发送请求
        response = self._http_client.request(**request_kwargs)
        response.raise_for_status()

        # 对于文件下载请求,直接返回响应对象
        if kwargs.get("stream", False):
            return response

        # 解析JSON响应
        data = response.json()

        # 检查微信API返回的业务错误码
        if data.get("errcode", 0) != 0:
            error = ErrorResponse.model_validate(data)
            raise WxKfApiError(error.errcode, error.errmsg)

        # 解析为指定的Pydantic模型
        return response_model.model_validate(data)

    async def _request_async(
        self,
        method: str,
        endpoint: str,
        response_model: Type[T],
        corp_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        use_suite_token: bool = False,
        use_provider_token: bool = False,
        **kwargs
    ) -> T:
        """发起异步API请求

        Args:
            (参数同_request方法)

        Returns:
            解析后的Pydantic模型实例

        Raises:
            WxKfApiError: API返回错误
        """
        url = f"{self.BASE_URL}{endpoint}"

        # 获取Token
        if use_provider_token:
            token = self.token_manager.get_provider_access_token()
            token_param = "provider_access_token"
        elif use_suite_token:
            token = self.token_manager.get_suite_access_token()
            token_param = "suite_access_token"
        else:
            if not corp_id:
                raise ValueError("corp_id is required for corp access token")
            token = self.token_manager.get_corp_access_token(corp_id)
            token_param = "access_token"

        # 构建请求参数
        request_params = params or {}
        request_params[token_param] = token

        request_kwargs = {
            "method": method,
            "url": url,
            "params": request_params,
            **kwargs
        }

        # 处理文件上传
        if files:
            request_kwargs["files"] = files
        elif json_data is not None:
            request_kwargs["json"] = json_data

        # 发送异步请求
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(**request_kwargs)
            response.raise_for_status()

            # 对于文件下载请求,直接返回响应对象
            if kwargs.get("stream", False):
                return response

            # 解析JSON响应
            data = response.json()

            # 检查微信API返回的业务错误码
            if data.get("errcode", 0) != 0:
                error = ErrorResponse.model_validate(data)
                raise WxKfApiError(error.errcode, error.errmsg)

            # 解析为指定的Pydantic模型
            return response_model.model_validate(data)

    def close(self):
        """关闭客户端,释放资源"""
        if self._http_client:
            self._http_client.close()
        if self.token_manager:
            self.token_manager.close()

    async def aclose(self):
        """异步关闭客户端"""
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()
