# -*- coding: utf-8 -*-
"""数据库模块单元测试"""

import pytest
import asyncio
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.unit
async def test_database_connection(test_config):
    """测试数据库连接"""
    from wxkf_saas.core.database import DatabaseManager

    db_manager = DatabaseManager(test_config)

    # 测试异步引擎
    try:
        # 测试连接
        async with db_manager.async_engine.begin() as conn:
            result = await conn.execute("SELECT 1 as test")
            assert result.scalar() == 1
    except Exception as e:
        pytest.fail(f"异步数据库连接失败: {e}")

    # 测试同步引擎
    try:
        with db_manager.sync_engine.connect() as conn:
            result = conn.execute("SELECT 1 as test")
            assert result.scalar() == 1
    except Exception as e:
        pytest.fail(f"同步数据库连接失败: {e}")


async def test_database_session_creation(test_database):
    """测试数据库会话创建"""
    async with test_database['async_session']() as session:
        assert isinstance(session, AsyncSession)
        assert session.is_active


async def test_database_transaction(test_database):
    """测试数据库事务"""
    from wxkf_saas.models.tenant import Tenant

    async with test_database['async_session']() as session:
        # 测试事务提交
        tenant = Tenant(
            corp_id="test_corp",
            corp_name="测试企业"
        )
        session.add(tenant)
        await session.commit()

        # 验证数据已保存
        result = await session.execute(
            "SELECT corp_id FROM tenants WHERE corp_id = :corp_id",
            {"corp_id": "test_corp"}
        )
        assert result.scalar() == "test_corp"

        # 测试事务回滚
        tenant2 = Tenant(corp_id="test_corp2", corp_name="测试企业2")
        session.add(tenant2)

        try:
            await session.commit()
            # 故意引发异常
            raise Exception("测试回滚")
        except Exception:
            await session.rollback()

        # 验证回滚成功
        result = await session.execute(
            "SELECT COUNT(*) FROM tenants WHERE corp_id = :corp_id",
            {"corp_id": "test_corp2"}
        )
        assert result.scalar() == 1


def test_database_connection_pool(test_database):
    """测试连接池配置"""
    from wxkf_saas.core.database import get_db_manager

    db_manager = get_db_manager()

    assert db_manager.config.db_pool_size == 1
    assert db_manager.config.db_max_overflow == 2


def test_database_url_generation():
    """测试URL生成"""
    from wxkf_saas.core.config import WxKfSaasConfig

    # 测试MySQL URL生成
    config = WxKfSaasConfig(
        DB_TYPE="mysql",
        DB_HOST="test-host",
        DB_PORT=3306,
        DB_NAME="test_db",
        DB_USER="test-user",
        DB_PASSWORD="test-pass"
    )

    expected_sync = "mysql+pymysql://test-user:test-pass@test-host:3306/test_db?charset=utf8mb4"
    expected_async = "mysql+aiomysql://test-user:test-pass@test-host:3306/test_db?charset=utf8mb4"

    assert config.db_url == expected_sync
    assert config.db_async_url == expected_async

    # 测试PostgreSQL URL生成
    pg_config = WxKfSaasConfig(
        DB_TYPE="postgresql",
        DB_HOST="test-host",
        DB_PORT=5432,
        DB_NAME="test_db",
        DB_USER="postgres",
        DB_PASSWORD="postgres"
    )

    assert "postgresql+psycopg2://" in pg_config.db_url
    assert "postgresql+asyncpg://" in pg_config.db_async_url

    # 测试SQLite URL生成
    sqlite_config = WxKfSaasConfig(
        DB_TYPE="sqlite",
        DB_PATH="./test.db"
    )

    assert "sqlite+sqlite://" in sqlite_config.db_url
    assert "sqlite+aiosqlite://" in sqlite_config.db_async_url


async def test_database_operations(test_database):
    """测试数据库基本操作"""
    from wxkf_saas.models.tenant import Tenant

    async with test_database['async_session']() as session:
        # 测试INSERT
        tenant = Tenant(
            corp_id="test_corp_1",
            corp_name="测试企业1",
            is_active=True,
            is_authorized=True
        )
        session.add(tenant)
        await session.commit()

        # 测试SELECT
        result = await session.execute(
            "SELECT * FROM tenants WHERE corp_id = :corp_id",
            {"corp_id": "test_corp_1"}
        )
        tenants = result.scalars().all()
        assert len(tenants) == 1
        assert tenants[0].corp_id == "test_corp_1"

        # 测试UPDATE
        tenants[0].corp_name = "测试企业1_更新"
        await session.commit()

        result = await session.execute(
            "SELECT corp_name FROM tenants WHERE corp_id = :corp_id",
            {"corp_id": "test_corp_1"}
        )
        assert result.scalar() == "测试企业1_更新"

        # 测试DELETE
        await session.delete(tenants[0])
        await session.commit()

        result = await session.execute(
            "SELECT COUNT(*) FROM tenants WHERE corp_id = :corp_id",
            {"corp_id": "test_corp_1"}
        )
        assert result.scalar() == 0


def test_database_error_handling(test_database):
    """测试数据库错误处理"""
    from wxkf_saas.core.database import DatabaseManager

    # 创建无效配置的管理器
    invalid_config = test_database['config']._replace(
        DB_TYPE="mysql",
        DB_HOST="invalid-host-does-not-exist"
    )

    with pytest.raises(Exception):
        DatabaseManager(invalid_config)


@pytest.mark.asyncio
async def test_database_async_operations(test_database):
    """测试异步数据库操作"""
    from wxkf_saas.models.tenant import Tenant
    from wxkf_saas.core.token_manager import MultiTenantTokenManager

    async with test_database['async_session']() as session:
        token_manager = MultiTenantTokenManager()

        # 测试批量操作
        tenants = [
            Tenant(corp_id=f"test_corp_{i}", corp_name=f"测试企业{i}")
            for i in range(5)
        ]

        session.add_all(tenants)
        await session.commit()

        # 验证批量插入
        result = await session.execute("SELECT COUNT(*) FROM tenants")
        assert result.scalar() == 5

        # 测试复杂查询
        complex_result = await session.execute("""
            SELECT corp_id, corp_name, COUNT(*) as message_count
            FROM tenants
            WHERE corp_name LIKE '测试企业%'
            GROUP BY corp_id, corp_name
            ORDER BY message_count DESC
        """)

        rows = complex_result.fetchall()
        assert len(rows) > 0