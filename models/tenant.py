# -*- coding: utf-8 -*-
"""租户数据模型"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field

Base = declarative_base()


class Tenant(Base):
    """租户表 - 存储授权企业的信息"""

    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 企业基本信息
    corp_id = Column(String(64), unique=True, nullable=False, index=True, comment="企业ID")
    corp_name = Column(String(128), comment="企业名称")

    # 授权信息
    permanent_code = Column(String(512), comment="永久授权码")
    auth_code = Column(String(512), comment="临时授权码")
    auth_time = Column(DateTime, comment="授权时间")

    # 状态
    is_active = Column(Boolean, default=True, comment="是否激活")
    is_authorized = Column(Boolean, default=False, comment="是否已授权")

    # 配置信息
    callback_url = Column(String(512), comment="回调URL")
    callback_token = Column(String(128), comment="回调Token")
    callback_aes_key = Column(String(128), comment="回调加密密钥")

    # 额外信息
    contact_name = Column(String(64), comment="联系人姓名")
    contact_phone = Column(String(32), comment="联系人电话")
    contact_email = Column(String(128), comment="联系人邮箱")

    # 备注
    remark = Column(Text, comment="备注")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def __repr__(self):
        return f"<Tenant(corp_id='{self.corp_id}', corp_name='{self.corp_name}')>"


class TenantToken(Base):
    """租户Token表 - 存储各类Token"""

    __tablename__ = "tenant_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 租户信息
    corp_id = Column(String(64), nullable=False, index=True, comment="企业ID")

    # Token信息
    token_type = Column(String(32), nullable=False, comment="Token类型: access_token, suite_access_token等")
    token_value = Column(String(512), nullable=False, comment="Token值")
    expires_at = Column(Integer, nullable=False, comment="过期时间戳")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def __repr__(self):
        return f"<TenantToken(corp_id='{self.corp_id}', token_type='{self.token_type}')>"


# Pydantic 模型用于API请求和响应

class TenantCreate(BaseModel):
    """创建租户请求"""
    corp_id: str = Field(..., description="企业ID")
    corp_name: Optional[str] = Field(None, description="企业名称")
    auth_code: Optional[str] = Field(None, description="临时授权码")
    callback_url: Optional[str] = Field(None, description="回调URL")
    contact_name: Optional[str] = Field(None, description="联系人姓名")
    contact_phone: Optional[str] = Field(None, description="联系人电话")
    contact_email: Optional[str] = Field(None, description="联系人邮箱")
    remark: Optional[str] = Field(None, description="备注")


class TenantUpdate(BaseModel):
    """更新租户请求"""
    corp_name: Optional[str] = Field(None, description="企业名称")
    callback_url: Optional[str] = Field(None, description="回调URL")
    callback_token: Optional[str] = Field(None, description="回调Token")
    callback_aes_key: Optional[str] = Field(None, description="回调加密密钥")
    contact_name: Optional[str] = Field(None, description="联系人姓名")
    contact_phone: Optional[str] = Field(None, description="联系人电话")
    contact_email: Optional[str] = Field(None, description="联系人邮箱")
    is_active: Optional[bool] = Field(None, description="是否激活")
    remark: Optional[str] = Field(None, description="备注")


class TenantResponse(BaseModel):
    """租户响应"""
    id: int
    corp_id: str
    corp_name: Optional[str]
    is_active: bool
    is_authorized: bool
    contact_name: Optional[str]
    contact_phone: Optional[str]
    contact_email: Optional[str]
    auth_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TenantListResponse(BaseModel):
    """租户列表响应"""
    total: int = Field(..., description="总数")
    items: list[TenantResponse] = Field(..., description="租户列表")
