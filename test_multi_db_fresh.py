# -*- coding: utf-8 -*-
"""多数据库配置测试（不使用.env）"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from core.config import WxKfSaasConfig


def test_database_configs():
    """测试不同数据库配置"""
    print("🗄️ 多数据库配置测试（不使用.env）\n")

    # 1. MySQL配置测试
    print("1️⃣ MySQL 配置测试:")
    config_mysql = {
        'DB_TYPE': 'mysql',
        'DB_HOST': 'localhost',
        'DB_PORT': 3306,
        'DB_NAME': 'wxkf_saas',
        'DB_USER': 'testuser',
        'DB_PASSWORD': 'testpass'
    }

    try:
        # 创建临时配置类来测试
        test_config = WxKfSaasConfig(**config_mysql)
        print(f"   ✅ 同步URL: {test_config.db_url}")
        print(f"   ✅ 异步URL: {test_config.db_async_url}")
    except Exception as e:
        print(f"   ❌ MySQL配置错误: {e}")

    print()

    # 2. PostgreSQL配置测试
    print("2️⃣ PostgreSQL 配置测试:")
    config_pg = {
        'DB_TYPE': 'postgresql',
        'DB_HOST': 'localhost',
        'DB_PORT': 5432,
        'DB_NAME': 'wxkf_saas',
        'DB_USER': 'postgres',
        'DB_PASSWORD': 'postgres'
    }

    try:
        test_config = WxKfSaasConfig(**config_pg)
        print(f"   ✅ 同步URL: {test_config.db_url}")
        print(f"   ✅ 异步URL: {test_config.db_async_url}")
    except Exception as e:
        print(f"   ❌ PostgreSQL配置错误: {e}")

    print()

    # 3. SQLite配置测试
    print("3️⃣ SQLite 配置测试:")
    config_sqlite = {
        'DB_TYPE': 'sqlite',
        'DB_PATH': './data/test.db'
    }

    try:
        test_config = WxKfSaasConfig(**config_sqlite)
        print(f"   ✅ 同步URL: {test_config.db_url}")
        print(f"   ✅ 异步URL: {test_config.db_async_url}")
    except Exception as e:
        print(f"   ❌ SQLite配置错误: {e}")

    print()

    # 4. 直接URL配置测试
    print("4️⃣ 直接URL配置测试:")
    config_direct = {
        'DB_TYPE': 'mysql',
        'DATABASE_URL': 'mysql+pymysql://direct@localhost:3306/test',
        'ASYNC_DATABASE_URL': 'mysql+aiomysql://direct@localhost:3306/test'
    }

    try:
        test_config = WxKfSaasConfig(**config_direct)
        print(f"   ✅ 使用直接配置的同步URL: {test_config.db_url}")
        print(f"   ✅ 使用直接配置的异步URL: {test_config.db_async_url}")
    except Exception as e:
        print(f"   ❌ 直接URL配置错误: {e}")

    print()

    # 5. 错误配置测试
    print("5️⃣ 错误配置测试:")

    print("   a. 缺少必要参数:")
    config_invalid = {
        'DB_TYPE': 'mysql',
        'DB_HOST': 'localhost',
        # 缺少 DB_NAME, DB_USER, DB_PASSWORD
    }

    try:
        test_config = WxKfSaasConfig(**config_invalid)
        print(f"   ❌ 应该报错，但成功了: {test_config.db_url}")
    except Exception as e:
        print(f"   ✅ 正确报错: {e}")

    print()

    print("   b. SQLite缺少路径:")
    config_sqlite_invalid = {
        'DB_TYPE': 'sqlite'
        # 缺少 DB_PATH
    }

    try:
        test_config = WxKfSaasConfig(**config_sqlite_invalid)
        print(f"   ❌ 应该报错，但成功了: {test_config.db_url}")
    except Exception as e:
        print(f"   ✅ 正确报错: {e}")

    print()

    print("   c. 不支持的数据库类型:")
    config_unsupported = {
        'DB_TYPE': 'mongodb'
    }

    try:
        test_config = WxKfSaasConfig(**config_unsupported)
        print(f"   ❌ 应该报错，但成功了: {test_config.db_url}")
    except Exception as e:
        print(f"   ✅ 正确报错: {e}")


def show_configuration_examples():
    """显示配置示例"""
    print("\n📋 数据库配置示例:")

    examples = {
        "MySQL开发": {
            "DB_TYPE": "mysql",
            "DB_HOST": "localhost",
            "DB_PORT": 3306,
            "DB_NAME": "wxkf_saas_dev",
            "DB_USER": "dev_user",
            "DB_PASSWORD": "dev_password",
            "DB_POOL_SIZE": 5,
            "DB_MAX_OVERFLOW": 10
        },
        "MySQL生产": {
            "DB_TYPE": "mysql",
            "DATABASE_URL": "mysql+pymysql://user:pass@prod-db.internal:3306/wxkf_saas_prod?charset=utf8mb4",
            "ASYNC_DATABASE_URL": "mysql+aiomysql://user:pass@prod-db.internal:3306/wxkf_saas_prod?charset=utf8mb4",
            "DB_POOL_SIZE": 20,
            "DB_MAX_OVERFLOW": 40
        },
        "PostgreSQL": {
            "DB_TYPE": "postgresql",
            "DB_HOST": "localhost",
            "DB_PORT": 5432,
            "DB_NAME": "wxkf_saas",
            "DB_USER": "postgres",
            "DB_PASSWORD": "postgres",
            "DB_POOL_SIZE": 10,
            "DB_MAX_OVERFLOW": 20
        },
        "SQLite": {
            "DB_TYPE": "sqlite",
            "DB_PATH": "./data/app.db",
            "DB_POOL_SIZE": 1,
            "DB_MAX_OVERFLOW": 5
        }
    }

    for name, config in examples.items():
        print(f"\n📁 {name}:")
        for key, value in config.items():
            print(f"   {key}={value}")


if __name__ == "__main__":
    # 清除环境变量以避免干扰
    env_vars_to_clear = [
        'DB_TYPE', 'DB_HOST', 'DB_PORT', 'DB_NAME',
        'DB_USER', 'DB_PASSWORD', 'DB_PATH',
        'DATABASE_URL', 'ASYNC_DATABASE_URL'
    ]

    for var in env_vars_to_clear:
        if var in os.environ:
            del os.environ[var]

    test_database_configs()
    show_configuration_examples()