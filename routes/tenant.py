# -*- coding: utf-8 -*-
"""租户管理路由"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from wxkf_api.core.database import get_db
from wxkf_api.models.tenant import (
    Tenant,
    TenantCreate,
    TenantUpdate,
    TenantResponse,
    TenantListResponse,
)

router = APIRouter(prefix="/api/tenants", tags=["租户管理"])


@router.post("/", response_model=TenantResponse, summary="创建租户")
def create_tenant(
    tenant_data: TenantCreate,
    db: Session = Depends(get_db)
):
    """创建新租户

    Args:
        tenant_data: 租户信息
        db: 数据库会话

    Returns:
        TenantResponse: 创建的租户信息

    Raises:
        HTTPException: 租户已存在
    """
    # 检查租户是否已存在
    existing_tenant = db.query(Tenant).filter(Tenant.corp_id == tenant_data.corp_id).first()
    if existing_tenant:
        raise HTTPException(status_code=400, detail="Tenant already exists")

    # 创建租户
    tenant = Tenant(
        corp_id=tenant_data.corp_id,
        corp_name=tenant_data.corp_name,
        auth_code=tenant_data.auth_code,
        callback_url=tenant_data.callback_url,
        contact_name=tenant_data.contact_name,
        contact_phone=tenant_data.contact_phone,
        contact_email=tenant_data.contact_email,
        remark=tenant_data.remark,
        is_active=True,
        is_authorized=False  # 需要通过授权流程后才设置为True
    )

    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    return tenant


@router.get("/", response_model=TenantListResponse, summary="获取租户列表")
def list_tenants(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="每页记录数"),
    is_active: bool = Query(None, description="是否激活"),
    db: Session = Depends(get_db)
):
    """获取租户列表

    Args:
        skip: 跳过记录数
        limit: 每页记录数
        is_active: 是否激活(可选)
        db: 数据库会话

    Returns:
        TenantListResponse: 租户列表和总数
    """
    query = db.query(Tenant)

    if is_active is not None:
        query = query.filter(Tenant.is_active == is_active)

    total = query.count()
    tenants = query.offset(skip).limit(limit).all()

    return TenantListResponse(
        total=total,
        items=tenants
    )


@router.get("/{corp_id}", response_model=TenantResponse, summary="获取租户详情")
def get_tenant(
    corp_id: str,
    db: Session = Depends(get_db)
):
    """获取租户详情

    Args:
        corp_id: 企业ID
        db: 数据库会话

    Returns:
        TenantResponse: 租户信息

    Raises:
        HTTPException: 租户不存在
    """
    tenant = db.query(Tenant).filter(Tenant.corp_id == corp_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return tenant


@router.put("/{corp_id}", response_model=TenantResponse, summary="更新租户")
def update_tenant(
    corp_id: str,
    tenant_data: TenantUpdate,
    db: Session = Depends(get_db)
):
    """更新租户信息

    Args:
        corp_id: 企业ID
        tenant_data: 更新的租户信息
        db: 数据库会话

    Returns:
        TenantResponse: 更新后的租户信息

    Raises:
        HTTPException: 租户不存在
    """
    tenant = db.query(Tenant).filter(Tenant.corp_id == corp_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # 更新字段
    update_data = tenant_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)

    db.commit()
    db.refresh(tenant)

    return tenant


@router.delete("/{corp_id}", summary="删除租户")
def delete_tenant(
    corp_id: str,
    db: Session = Depends(get_db)
):
    """删除租户

    Args:
        corp_id: 企业ID
        db: 数据库会话

    Returns:
        dict: 删除结果

    Raises:
        HTTPException: 租户不存在
    """
    tenant = db.query(Tenant).filter(Tenant.corp_id == corp_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    db.delete(tenant)
    db.commit()

    return {"message": "Tenant deleted successfully"}
