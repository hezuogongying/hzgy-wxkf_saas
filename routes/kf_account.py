# -*- coding: utf-8 -*-
"""客服账号管理路由"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_async_db, get_db
from core.client import WxKfSaasClient
from core.config import WxKfSaasConfig
from api.kf_account import KfAccountApi
from models.kf_account import (
    AddKfAccountRequest,
    AddKfAccountResponse,
    UpdateKfAccountRequest,
    UpdateKfAccountResponse,
    DeleteKfAccountRequest,
    DeleteKfAccountResponse,
    GetKfAccountListRequest,
    GetKfAccountListResponse,
    GetAccountLinkRequest,
    GetAccountLinkResponse,
    GetCustomerInfoRequest,
    GetCustomerInfoResponse,
)

router = APIRouter(prefix="/api/kf-accounts", tags=["客服账号管理"])

# 请求模型
class AddKfAccountRequestModel(BaseModel):
    """添加客服账号请求模型"""
    corp_id: str
    name: str
    media_id: str

class UpdateKfAccountRequestModel(BaseModel):
    """修改客服账号请求模型"""
    corp_id: str
    open_kfid: str
    name: Optional[str] = None
    media_id: Optional[str] = None

class DeleteKfAccountRequestModel(BaseModel):
    """删除客服账号请求模型"""
    corp_id: str
    open_kfid: str

class GetKfAccountListRequestModel(BaseModel):
    """获取客服账号列表请求模型"""
    corp_id: str
    offset: Optional[int] = Query(0, ge=0, description="偏移量")
    limit: Optional[int] = Query(100, ge=1, le=1000, description="限制数量")

class GetAccountLinkRequestModel(BaseModel):
    """获取客服账号链接请求模型"""
    corp_id: str
    open_kfid: str
    scene: Optional[str] = Query(None, description="场景值")

class GetCustomerInfoRequestModel(BaseModel):
    """获取客户信息请求模型"""
    corp_id: str
    external_userid: str


# 响应模型
class APIResponse(BaseModel):
    """API通用响应模型"""
    code: int = 0
    message: str = "success"
    data: dict = {}


def get_db_session(db_gen=Depends(get_db)) -> Session:
    """从依赖注入的生成器中获取数据库会话"""
    return next(db_gen)


def get_client(db: Session = Depends(get_db_session)) -> WxKfSaasClient:
    """获取微信客服客户端实例"""
    config = WxKfSaasConfig()
    return WxKfSaasClient(config, db)


@router.post("/", response_model=AddKfAccountResponse, summary="添加客服账号")
async def add_kf_account(
    request_data: AddKfAccountRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """添加客服账号

    添加客服账号，并可设置客服名称和头像。目前一家企业最多可添加5000个客服账号。
    """
    try:
        kf_api = KfAccountApi(client)
        response = await kf_api.add(
            corp_id=request_data.corp_id,
            name=request_data.name,
            media_id=request_data.media_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{open_kfid}", response_model=UpdateKfAccountResponse, summary="修改客服账号")
async def update_kf_account(
    open_kfid: str,
    request_data: UpdateKfAccountRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """修改客服账号

    修改客服账号基本信息，包括客服名称和头像。
    """
    try:
        kf_api = KfAccountApi(client)
        response = await kf_api.update(
            corp_id=request_data.corp_id,
            open_kfid=open_kfid,
            name=request_data.name,
            media_id=request_data.media_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{open_kfid}", response_model=DeleteKfAccountResponse, summary="删除客服账号")
async def delete_kf_account(
    open_kfid: str,
    request_data: DeleteKfAccountRequestModel,
    client: WxKfSaasClient = Depends(get_client)
):
    """删除客服账号

    删除指定的客服账号，删除后客服将无法接收用户消息。
    """
    try:
        kf_api = KfAccountApi(client)
        response = await kf_api.delete(
            corp_id=request_data.corp_id,
            open_kfid=open_kfid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=GetKfAccountListResponse, summary="获取客服账号列表")
async def get_kf_account_list(
    corp_id: str = Query(..., description="企业ID"),
    offset: int = Query(0, ge=0, description="偏移量"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    client: WxKfSaasClient = Depends(get_client)
):
    """获取客服账号列表

    获取企业下所有客服账号列表，支持分页查询。
    """
    try:
        kf_api = KfAccountApi(client)
        response = await kf_api.get_list(
            corp_id=corp_id,
            offset=offset,
            limit=limit
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{open_kfid}/link", response_model=GetAccountLinkResponse, summary="获取客服账号链接")
async def get_account_link(
    open_kfid: str,
    corp_id: str = Query(..., description="企业ID"),
    scene: Optional[str] = Query(None, description="场景值"),
    client: WxKfSaasClient = Depends(get_client)
):
    """获取客服账号链接

    获取指定客服账号的联系方式链接，用户可通过链接直接联系客服。
    """
    try:
        kf_api = KfAccountApi(client)
        response = await kf_api.get_account_link(
            corp_id=corp_id,
            open_kfid=open_kfid,
            scene=scene
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/customer/{external_userid}", response_model=GetCustomerInfoResponse, summary="获取客户信息")
async def get_customer_info(
    external_userid: str,
    corp_id: str = Query(..., description="企业ID"),
    client: WxKfSaasClient = Depends(get_client)
):
    """获取客户信息

    根据用户的external_userid获取客户的基础信息，包括昵称、头像、性别等。
    """
    try:
        kf_api = KfAccountApi(client)
        response = await kf_api.get_customer_info(
            corp_id=corp_id,
            external_userid=external_userid
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))