# -*- coding: utf-8 -*-
"""客户联系路由"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.database import get_db
from api.contact import ContactApi, SetContactProfileRequest, ContactProfile, ContactAvatar
from core.client import WxKfSaasClient
from models.tenant import Tenant

router = APIRouter(prefix="/api/contact", tags=["客户联系"])


def get_db_session(db_gen=Depends(get_db)) -> Session:
    """从依赖注入的生成器中获取数据库会话"""
    return next(db_gen)


def get_contact_api(db: Session = Depends(get_db_session)) -> ContactApi:
    """获取ContactApi实例"""
    from core.config import WxKfSaasConfig
    config = WxKfSaasConfig()
    client = WxKfSaasClient(config, db)
    return ContactApi(client)


@router.post("/set-profile/{corp_id}", summary="配置客户联系Profile")
def set_contact_profile(
    corp_id: str,
    request: SetContactProfileRequest,
    db: Session = Depends(get_db_session)
):
    """配置客户联系Profile

    该接口用于配置指定成员添加外部联系人时，自动对外部联系人展示的Profile信息。

    Args:
        corp_id: 企业ID
        request: 设置请求参数

    Returns:
        设置结果

    Raises:
        HTTPException: 租户不存在或API调用失败
    """
    # 验证租户是否存在
    tenant = db.query(Tenant).filter(Tenant.corp_id == corp_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if not tenant.is_authorized:
        raise HTTPException(status_code=400, detail="Tenant not authorized")

    # 获取API实例
    api = get_contact_api(db)

    # 调用API
    try:
        result = api.set_contact_profile(
            corp_id=corp_id,
            userid=request.userid,
            external_userid=request.external_userid,
            avatar=request.profile.avatar.media_id if request.profile.avatar else None,
            handle=request.profile.handle,
            description=request.profile.description,
            image=request.profile.image,
            mobile=request.profile.mobile,
            email=request.profile.email,
            biz_url=request.profile.biz_url
        )

        if result.errcode != 0:
            raise HTTPException(status_code=400, detail=result.errmsg)

        return {"errcode": result.errcode, "errmsg": result.errmsg}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-profile/{corp_id}", summary="获取客户联系Profile")
def get_contact_profile(
    corp_id: str,
    userid: str = Query(..., description="企业成员的userid"),
    external_userid: str = Query(..., description="外部联系人userid"),
    db: Session = Depends(get_db_session)
):
    """获取客户联系Profile

    Args:
        corp_id: 企业ID
        userid: 企业成员的userid
        external_userid: 外部联系人userid

    Returns:
        Profile配置信息

    Raises:
        HTTPException: 租户不存在或API调用失败
    """
    # 验证租户是否存在
    tenant = db.query(Tenant).filter(Tenant.corp_id == corp_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if not tenant.is_authorized:
        raise HTTPException(status_code=400, detail="Tenant not authorized")

    # 获取API实例
    api = get_contact_api(db)

    # 调用API
    try:
        result = api.get_contact_profile(
            corp_id=corp_id,
            userid=userid,
            external_userid=external_userid
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-get-profile/{corp_id}", summary="批量获取客户联系Profile")
def batch_get_contact_profile(
    corp_id: str,
    request: dict,
    db: Session = Depends(get_db_session)
):
    """批量获取客户联系Profile

    Args:
        corp_id: 企业ID
        request: 请求参数，包含userid和external_userid_list

    Returns:
        批量查询结果

    Raises:
        HTTPException: 租户不存在或API调用失败
    """
    # 验证租户是否存在
    tenant = db.query(Tenant).filter(Tenant.corp_id == corp_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if not tenant.is_authorized:
        raise HTTPException(status_code=400, detail="Tenant not authorized")

    # 获取请求参数
    userid = request.get("userid")
    external_userid_list = request.get("external_userid_list", [])

    if not userid:
        raise HTTPException(status_code=400, detail="userid is required")

    if not external_userid_list:
        raise HTTPException(status_code=400, detail="external_userid_list is required")

    if len(external_userid_list) > 100:
        raise HTTPException(status_code=400, detail="external_userid_list size cannot exceed 100")

    # 获取API实例
    api = get_contact_api(db)

    # 调用API
    try:
        result = api.batch_get_contact_profile(
            corp_id=corp_id,
            userid=userid,
            external_userid_list=external_userid_list
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))