# -*- coding: utf-8 -*-
"""配置模块单元测试"""

import pytest
from pydantic import ValidationError


def test_config_validation():
    """测试配置验证"""
    from wxkf_saas.core.config import WxKfSaasConfig

    # 测试MySQL完整配置
    config = WxKfSaasConfig(
        SUITE_ID="test_suite",
        SUITE_SECRET="test_secret",
        PROVIDER_SECRET="test_provider",
        PROVIDER_TOKEN="test_token",
        PROVIDER_ENCODING_AES_KEY="test_key",
        DB_TYPE="mysql",
        DB_HOST="localhost",
        DB_PORT=3306,
        DB_NAME="test_db",
        DB_USER="test_user",
        DB_PASSWORD="test_pass"
    )

    assert config.suite_id == "test_suite"
    assert config.db_type == "mysql"
    assert config.db_port == 3306


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