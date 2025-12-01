# -*- coding: utf-8 -*-
"""pytest配置文件"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from wxkf_saas.core.config import WxKfSaasConfig
from wxkf_saas.core.database import DatabaseManager
from wxkf_saas.core.client import WxKfSaasClient
from wxkf_saas.models.tenant import Tenant, TenantToken


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_config():
    """测试配置"""
    return WxKfSaasConfig(
        DB_TYPE="sqlite",  # 使用SQLite进行测试
        DB_PATH=":memory:",
        DB_NAME="test_db",
        DB_USER="test",
        DB_PASSWORD="test",
        DB_POOL_SIZE=1,
        DB_MAX_OVERFLOW=2,
        SUITE_ID="test_suite_id",
        SUITE_SECRET="test_suite_secret",
        PROVIDER_SECRET="test_provider_secret",
        PROVIDER_TOKEN="test_provider_token",
        PROVIDER_ENCODING_AES_KEY="test_provider_encoding_aes_key",
        REDIS_HOST="localhost",
        REDIS_PORT=6379,
        REDIS_DB=1,
        REDIS_KEY_PREFIX="test:",
        LOG_LEVEL="DEBUG"
    )


@pytest.fixture(scope="session")
async def test_database(test_config):
    """测试数据库"""
    # 创建内存数据库
    db_manager = DatabaseManager(test_config)

    # 测试同步数据库
    sync_engine = create_async_engine(
        test_config.db_url,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
            "echo": False,
        },
    )

    # 测试异步数据库
    async_engine = create_async_engine(
        test_config.db_async_url,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
            "echo": False,
        },
    )

    TestingAsyncSession = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    TestingSyncSession = sessionmaker(
        bind=sync_engine,
        autocommit=False,
        autoflush=False
    )

    yield {
        'db_manager': db_manager,
        'async_session': TestingAsyncSession,
        'sync_session': TestingSyncSession,
        'config': test_config
    }


@pytest.fixture(scope="session")
async def mock_client(test_config):
    """模拟微信API客户端"""
    client = WxKfSaasClient(test_config)

    # Mock HTTP客户端
    mock_http_client = AsyncMock()
    client._http_client = mock_http_client

    return client


@pytest.fixture(scope="session")
def mock_redis():
    """模拟Redis客户端"""
    mock_redis = MagicMock()
    return mock_redis


# 测试数据工厂
@pytest.fixture
def sample_tenant():
    """示例租户数据"""
    return Tenant(
        corp_id="test_corp_123",
        corp_name="测试企业",
        permanent_code="test_permanent_code",
        contact_name="张三",
        contact_phone="13800138000",
        contact_email="test@example.com",
        is_active=True,
        is_authorized=True
    )


@pytest.fixture
def sample_tenant_token():
    """示例Token数据"""
    return TenantToken(
        corp_id="_provider_",
        token_type="provider_access_token",
        token_value="test_provider_token_value",
        expires_at=9999999999
    )


# 测试数据清理
@pytest.fixture(autouse=True)
async def cleanup_test_data():
    """自动清理测试数据"""
    yield
    # 在测试后清理任何需要清理的数据
    pass


# 覆盖率配置
pytest_plugins = [
    "pytest-cov",
    "pytest-asyncio",
    "pytest-mock"
]

# 覆盖率配置
[tool:pytest]
coverage_run = {
    "source": ["wxkf_saas"],
    "omit": [
        "*/test_scripts/*",
        "*/venv/*",
        "*/tests/*",
    ]
}
coverage_report = {
    "show_missing": True,
    "precision": 2,
    "fail_under": 80,
    "skip_covered": False,
}
coverage_html = {
    "directory": "htmlcov",
}