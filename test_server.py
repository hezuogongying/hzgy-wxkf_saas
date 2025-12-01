#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试服务器启动"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from wxkf_saas.core.config import WxKfSaasConfig

# 创建简单的FastAPI应用
app = FastAPI(
    title="微信客服SaaS服务 - 测试版",
    description="测试服务器，验证路由导入",
    version="1.0.0-test",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/", tags=["测试"])
def health_check():
    """健康检查"""
    try:
        # 测试配置加载
        config = WxKfSaasConfig()
        return {
            "status": "ok",
            "message": "路由导入成功，服务器运行正常",
            "config_loaded": True,
            "service": "微信客服SaaS服务-测试版"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"配置加载失败: {str(e)}",
            "config_loaded": False
        }

@app.get("/test-routes", tags=["测试"])
def test_routes():
    """测试路由导入"""
    results = {}

    # 测试各个路由模块导入
    routes_to_test = [
        ("kf_account", "客服账号路由"),
        ("message", "消息管理路由"),
        ("media", "素材管理路由"),
        ("callback", "回调路由")
    ]

    for route_name, route_desc in routes_to_test:
        try:
            if route_name == "kf_account":
                from routes.kf_account import router
            elif route_name == "message":
                from routes.message import router
            elif route_name == "media":
                from routes.media import router
            elif route_name == "callback":
                from routes.callback import router

            results[route_name] = {
                "status": "success",
                "description": route_desc,
                "message": "导入成功"
            }
        except Exception as e:
            results[route_name] = {
                "status": "error",
                "description": route_desc,
                "message": f"导入失败: {str(e)}"
            }

    return {
        "test_results": results,
        "total_routes": len(routes_to_test),
        "success_count": sum(1 for r in results.values() if r["status"] == "success")
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 启动测试服务器...")
    print("📖 访问地址: http://127.0.0.1:58084/docs")
    print("🧪 测试路由: http://127.0.0.1:58084/test-routes")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=58084,
        log_level="info"
    )