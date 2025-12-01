# -*- coding: utf-8 -*-
"""多租户Token管理器"""

import time
import json
from typing import Optional, Dict
from sqlalchemy.orm import Session
import httpx

from wxkf_saas.core.config import WxKfSaasConfig
from wxkf_saas.core.exceptions import (
    WxKfApiError,
    TenantNotFoundError,
    TenantNotAuthorizedError,
    TokenExpiredError
)
from wxkf_saas.models.tenant import Tenant, TenantToken


class TokenType:
    """Token类型枚举"""
    ACCESS_TOKEN = "access_token"
    SUITE_ACCESS_TOKEN = "suite_access_token"
    PROVIDER_ACCESS_TOKEN = "provider_access_token"


class MultiTenantTokenManager:
    """多租户Token管理器

    负责管理多个租户的各类Token,包括:
    1. 企业access_token
    2. 服务商suite_access_token
    3. 服务商provider_access_token
    """

    # 微信API基础URL
    BASE_URL = "https://qyapi.weixin.qq.com/cgi-bin"

    def __init__(self, config: WxKfSaasConfig, db_session: Session, redis_client=None):
        """初始化Token管理器

        Args:
            config: SaaS配置对象
            db_session: 数据库会话
            redis_client: Redis客户端(可选,用于缓存)
        """
        self.config = config
        self.db = db_session
        self.redis = redis_client
        self._http_client = httpx.Client()

        # Token提前刷新时间(秒)
        self.token_refresh_advance = 60

    def get_corp_access_token(self, corp_id: str) -> str:
        """获取企业的access_token

        Args:
            corp_id: 企业ID

        Returns:
            str: 有效的access_token

        Raises:
            TenantNotFoundError: 租户不存在
            TenantNotAuthorizedError: 租户未授权
            WxKfApiError: API调用失败
        """
        # 1. 检查租户是否存在
        tenant = self.db.query(Tenant).filter(Tenant.corp_id == corp_id).first()
        if not tenant:
            raise TenantNotFoundError(corp_id)

        if not tenant.is_authorized or not tenant.permanent_code:
            raise TenantNotAuthorizedError(corp_id)

        # 2. 尝试从缓存获取
        token = self._get_token_from_cache(corp_id, TokenType.ACCESS_TOKEN)
        if token:
            return token

        # 3. 尝试从数据库获取
        token = self._get_token_from_db(corp_id, TokenType.ACCESS_TOKEN)
        if token:
            # 保存到缓存
            self._save_token_to_cache(corp_id, TokenType.ACCESS_TOKEN, token)
            return token

        # 4. 从微信获取新token
        token = self._fetch_corp_access_token(corp_id, tenant.permanent_code)
        return token

    def get_suite_access_token(self) -> str:
        """获取服务商的suite_access_token

        Returns:
            str: 有效的suite_access_token

        Raises:
            WxKfApiError: API调用失败
        """
        # suite_access_token是服务商级别的,不区分租户
        corp_id = "_suite_"

        # 1. 尝试从缓存获取
        token = self._get_token_from_cache(corp_id, TokenType.SUITE_ACCESS_TOKEN)
        if token:
            return token

        # 2. 尝试从数据库获取
        token = self._get_token_from_db(corp_id, TokenType.SUITE_ACCESS_TOKEN)
        if token:
            self._save_token_to_cache(corp_id, TokenType.SUITE_ACCESS_TOKEN, token)
            return token

        # 3. 从微信获取新token (需要suite_ticket,通常通过回调获得)
        # 这里暂时抛出异常,实际应该实现suite_ticket的存储和获取
        raise WxKfApiError(-1, "suite_ticket not implemented yet")

    def get_provider_access_token(self) -> str:
        """获取服务商的provider_access_token

        Returns:
            str: 有效的provider_access_token

        Raises:
            WxKfApiError: API调用失败
        """
        corp_id = "_provider_"

        # 1. 尝试从缓存获取
        token = self._get_token_from_cache(corp_id, TokenType.PROVIDER_ACCESS_TOKEN)
        if token:
            return token

        # 2. 尝试从数据库获取
        token = self._get_token_from_db(corp_id, TokenType.PROVIDER_ACCESS_TOKEN)
        if token:
            self._save_token_to_cache(corp_id, TokenType.PROVIDER_ACCESS_TOKEN, token)
            return token

        # 3. 从微信获取新token
        token = self._fetch_provider_access_token()
        return token

    def _get_token_from_cache(self, corp_id: str, token_type: str) -> Optional[str]:
        """从缓存获取Token

        Args:
            corp_id: 企业ID
            token_type: Token类型

        Returns:
            Optional[str]: Token值,如果不存在或已过期返回None
        """
        if not self.redis:
            return None

        key = f"{self.config.redis_key_prefix}token:{corp_id}:{token_type}"
        token_data = self.redis.get(key)

        if not token_data:
            return None

        try:
            data = json.loads(token_data)
            expires_at = data.get("expires_at", 0)

            # 检查是否过期
            if expires_at < time.time():
                self.redis.delete(key)
                return None

            return data.get("token")
        except Exception:
            return None

    def _save_token_to_cache(self, corp_id: str, token_type: str, token: str, expires_in: int = 7200):
        """保存Token到缓存

        Args:
            corp_id: 企业ID
            token_type: Token类型
            token: Token值
            expires_in: 过期时间(秒)
        """
        if not self.redis:
            return

        key = f"{self.config.redis_key_prefix}token:{corp_id}:{token_type}"
        expires_at = int(time.time()) + expires_in - self.token_refresh_advance

        data = {
            "token": token,
            "expires_at": expires_at
        }

        # 设置缓存,TTL为expires_in
        self.redis.setex(key, expires_in, json.dumps(data))

    def _get_token_from_db(self, corp_id: str, token_type: str) -> Optional[str]:
        """从数据库获取Token

        Args:
            corp_id: 企业ID
            token_type: Token类型

        Returns:
            Optional[str]: Token值,如果不存在或已过期返回None
        """
        token_record = (
            self.db.query(TenantToken)
            .filter(
                TenantToken.corp_id == corp_id,
                TenantToken.token_type == token_type
            )
            .first()
        )

        if not token_record:
            return None

        # 检查是否过期
        if token_record.expires_at < time.time():
            # 删除过期token
            self.db.delete(token_record)
            self.db.commit()
            return None

        return token_record.token_value

    def _save_token_to_db(self, corp_id: str, token_type: str, token: str, expires_in: int):
        """保存Token到数据库

        Args:
            corp_id: 企业ID
            token_type: Token类型
            token: Token值
            expires_in: 过期时间(秒)
        """
        expires_at = int(time.time()) + expires_in - self.token_refresh_advance

        # 查找现有记录
        token_record = (
            self.db.query(TenantToken)
            .filter(
                TenantToken.corp_id == corp_id,
                TenantToken.token_type == token_type
            )
            .first()
        )

        if token_record:
            # 更新现有记录
            token_record.token_value = token
            token_record.expires_at = expires_at
        else:
            # 创建新记录
            token_record = TenantToken(
                corp_id=corp_id,
                token_type=token_type,
                token_value=token,
                expires_at=expires_at
            )
            self.db.add(token_record)

        self.db.commit()

    def _fetch_corp_access_token(self, corp_id: str, permanent_code: str) -> str:
        """从微信获取企业access_token

        Args:
            corp_id: 企业ID
            permanent_code: 永久授权码

        Returns:
            str: access_token

        Raises:
            WxKfApiError: API调用失败
        """
        # 首先需要获取suite_access_token
        suite_access_token = self.get_suite_access_token()

        url = f"{self.BASE_URL}/service/get_corp_token"
        params = {"suite_access_token": suite_access_token}
        data = {
            "auth_corpid": corp_id,
            "permanent_code": permanent_code
        }

        response = self._http_client.post(url, params=params, json=data)
        response.raise_for_status()
        result = response.json()

        if result.get("errcode", 0) != 0:
            raise WxKfApiError(
                result.get("errcode", -1),
                result.get("errmsg", "获取access_token失败")
            )

        token = result.get("access_token")
        expires_in = result.get("expires_in", 7200)

        # 保存到数据库和缓存
        self._save_token_to_db(corp_id, TokenType.ACCESS_TOKEN, token, expires_in)
        self._save_token_to_cache(corp_id, TokenType.ACCESS_TOKEN, token, expires_in)

        return token

    def _fetch_provider_access_token(self) -> str:
        """从微信获取provider_access_token

        Returns:
            str: provider_access_token

        Raises:
            WxKfApiError: API调用失败
        """
        url = f"{self.BASE_URL}/service/get_provider_token"
        data = {
            "corpid": self.config.suite_id,
            "provider_secret": self.config.provider_secret
        }

        response = self._http_client.post(url, json=data)
        response.raise_for_status()
        result = response.json()

        if result.get("errcode", 0) != 0:
            raise WxKfApiError(
                result.get("errcode", -1),
                result.get("errmsg", "获取provider_access_token失败")
            )

        token = result.get("provider_access_token")
        expires_in = result.get("expires_in", 7200)

        # 保存到数据库和缓存
        corp_id = "_provider_"
        self._save_token_to_db(corp_id, TokenType.PROVIDER_ACCESS_TOKEN, token, expires_in)
        self._save_token_to_cache(corp_id, TokenType.PROVIDER_ACCESS_TOKEN, token, expires_in)

        return token

    def close(self):
        """关闭HTTP客户端"""
        if self._http_client:
            self._http_client.close()
