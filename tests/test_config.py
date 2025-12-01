# -*- coding: utf-8 -*-
"""配置模块单元测试"""

import pytest
from pydantic import ValidationError


@pytest.mark.unit
def test_config_validation(configure_test_logging):
    """测试配置验证"""
    test_logger = configure_test_logging
    test_logger.info("🔧 开始配置验证测试")

    from wxkf_saas.core.config import WxKfSaasConfig
    test_logger.debug("导入WxKfSaasConfig成功")

    # 测试从环境变量加载的配置
    config = WxKfSaasConfig()
    test_logger.debug(f"配置对象创建: {type(config)}")
    test_logger.debug(f"配置suite_id: {getattr(config, 'suite_id', 'N/A')}")

    # 验证配置对象创建成功
    test_logger.debug("验证配置对象属性...")
    assert config is not None
    test_logger.debug("✅ 配置对象不为None")

    assert hasattr(config, 'suite_id')
    test_logger.debug("✅ suite_id属性存在")

    assert hasattr(config, 'db_type')
    test_logger.debug("✅ db_type属性存在")

    assert hasattr(config, 'db_port')
    test_logger.debug("✅ db_port属性存在")

    # 验证基本属性类型
    test_logger.debug("验证属性类型...")
    assert isinstance(config.suite_id, str)
    test_logger.debug(f"✅ suite_id类型正确: {type(config.suite_id)}")

    assert isinstance(config.db_type, str)
    test_logger.debug(f"✅ db_type类型正确: {type(config.db_type)}")

    assert isinstance(config.db_port, int)
    test_logger.debug(f"✅ db_port类型正确: {type(config.db_port)}")

    test_logger.info("🎯 配置验证测试通过")


def test_config_validation_missing_fields():
    """测试缺少必需字段的配置"""
    from wxkf_saas.core.config import WxKfSaasConfig

    # 缺少必需字段
    with pytest.raises(ValidationError) as exc_info:
        WxKfSaasConfig(
            SUITE_ID="test_suite",
            # 缺少其他必需字段
        )

    assert "suite_secret" in str(exc_info.value)


def test_multi_database_config():
    """测试多数据库配置"""
    from wxkf_saas.core.config import WxKfSaasConfig

    # 测试MySQL配置
    mysql_config = WxKfSaasConfig(
        DB_TYPE="mysql",
        DB_HOST="localhost",
        DB_PORT=3306,
        DB_NAME="test_db",
        DB_USER="test_user",
        DB_PASSWORD="test_pass"
    )

    assert "mysql+pymysql://" in mysql_config.db_url
    assert "mysql+aiomysql://" in mysql_config.db_async_url

    # 测试PostgreSQL配置
    pg_config = WxKfSaasConfig(
        DB_TYPE="postgresql",
        DB_HOST="localhost",
        DB_PORT=5432,
        DB_NAME="test_db",
        DB_USER="postgres",
        DB_PASSWORD="postgres"
    )

    assert "postgresql+psycopg2://" in pg_config.db_url
    assert "postgresql+asyncpg://" in pg_config.db_async_url

    # 测试SQLite配置
    sqlite_config = WxKfSaasConfig(
        DB_TYPE="sqlite",
        DB_PATH="./test.db"
    )

    assert "sqlite+sqlite://" in sqlite_config.db_url
    assert "sqlite+aiosqlite://" in sqlite_config.db_async_url


def test_direct_url_config():
    """测试直接URL配置"""
    from wxkf_saas.core.config import WxKfSaasConfig

    config = WxKfSaasConfig(
        DATABASE_URL="mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4",
        ASYNC_DATABASE_URL="mysql+aiomysql://user:pass@host:3306/db?charset=utf8mb4"
    )

    assert config.db_url == "mysql+pymysql://user:pass@host:3306/db?charset=utf8mb4"
    assert config.db_async_url == "mysql+aiomysql://user:pass@host:3306/db?charset=utf8mb4"


def test_config_properties():
    """测试配置属性"""
    from wxkf_saas.core.config import WxKfSaasConfig

    config = WxKfSaasConfig(
        DB_TYPE="mysql",
        DB_HOST="localhost",
        DB_PORT=3306,
        DB_NAME="test_db",
        DB_USER="test_user",
        DB_PASSWORD="test_pass",
        DB_POOL_SIZE=5,
        DB_MAX_OVERFLOW=10
    )

    # 测试数据库URL生成
    assert config.db_url.startswith("mysql+pymysql://")
    assert config.db_async_url.startswith("mysql+aiomysql://")

    # 测试Redis URL生成
    assert "redis://" in config.redis_url

    # 测试回调URL生成
    config_with_server = WxKfSaasConfig(
        DB_TYPE="mysql",
        DB_HOST="localhost",
        DB_PORT=3306,
        DB_NAME="test_db",
        DB_USER="test_user",
        DB_PASSWORD="test_pass",
        SERVER_URL="https://test.domain.com"
    )

    assert "callback/provider" in config_with_server.provider_callback_url
    assert "callback/suite" in config_with_server.suite_callback_url

    # 测试上传路径
    upload_path = config_with_server.get_upload_path("test.txt")
    assert upload_path.name == "test.txt"
    assert str(upload_path).endswith("test.txt")


def test_invalid_database_type():
    """测试无效的数据库类型"""
    from wxkf_saas.core.config import WxKfSaasConfig

    with pytest.raises(ValueError) as exc_info:
        WxKfSaasConfig(DB_TYPE="invalid_db")


def test_sqlite_missing_path():
    """测试SQLite缺少路径"""
    from wxkf_saas.core.config import WxKfSaasConfig

    with pytest.raises(ValueError) as exc_info:
        WxKfSaasConfig(DB_TYPE="sqlite", DB_PATH=None)