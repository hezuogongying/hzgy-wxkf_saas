# -*- coding: utf-8 -*-
"""异常定义模块"""


class WxKfApiError(Exception):
    """微信客服API错误基类"""

    def __init__(self, errcode: int, errmsg: str):
        self.errcode = errcode
        self.errmsg = errmsg
        super().__init__(f"[{errcode}] {errmsg}")


class TenantNotFoundError(Exception):
    """租户不存在错误"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        super().__init__(f"Tenant not found: {tenant_id}")


class TenantNotAuthorizedError(Exception):
    """租户未授权错误"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        super().__init__(f"Tenant not authorized: {tenant_id}")


class TokenExpiredError(Exception):
    """Token过期错误"""

    def __init__(self, token_type: str):
        self.token_type = token_type
        super().__init__(f"Token expired: {token_type}")


class ConfigurationError(Exception):
    """配置错误"""
    pass
