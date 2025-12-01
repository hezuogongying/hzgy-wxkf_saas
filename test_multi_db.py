# -*- coding: utf-8 -*-
"""多数据库配置测试"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from core.config import WxKfSaasConfig


def test_database_configs():
    """测试不同数据库配置"""
    print("🗄️ 多数据库配置测试\n")

    # 1. MySQL配置测试
    print("1️⃣ MySQL 配置测试:")
    config_mysql = {
        'DB_TYPE': 'mysql',
        'DB_HOST': 'localhost',
        'DB_PORT': 3306,
        'DB_NAME': 'wxkf_saas',
        'DB_USER': 'user',
        'DB_PASSWORD': 'pass'
    }

    try:
        config = WxKfSaasConfig(**config_mysql)
        print(f"   ✅ 同步URL: {config.db_url}")
        print(f"   ✅ 异步URL: {config.db_async_url}")
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
        config = WxKfSaasConfig(**config_pg)
        print(f"   ✅ 同步URL: {config.db_url}")
        print(f"   ✅ 异步URL: {config.db_async_url}")
    except Exception as e:
        print(f"   ❌ PostgreSQL配置错误: {e}")

    print()

    # 3. SQLite配置测试
    print("3️⃣ SQLite 配置测试:")
    config_sqlite = {
        'DB_TYPE': 'sqlite',
        'DB_PATH': './data/app.db'
    }

    try:
        config = WxKfSaasConfig(**config_sqlite)
        print(f"   ✅ 同步URL: {config.db_url}")
        print(f"   ✅ 异步URL: {config.db_async_url}")
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
        config = WxKfSaasConfig(**config_direct)
        print(f"   ✅ 使用直接配置的同步URL: {config.db_url}")
        print(f"   ✅ 使用直接配置的异步URL: {config.db_async_url}")
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
        config = WxKfSaasConfig(**config_invalid)
        print(f"   ❌ 应该报错，但成功了: {config.db_url}")
    except Exception as e:
        print(f"   ✅ 正确报错: {e}")

    print()

    print("   b. SQLite缺少路径:")
    config_sqlite_invalid = {
        'DB_TYPE': 'sqlite'
        # 缺少 DB_PATH
    }

    try:
        config = WxKfSaasConfig(**config_sqlite_invalid)
        print(f"   ❌ 应该报错，但成功了: {config.db_url}")
    except Exception as e:
        print(f"   ✅ 正确报错: {e}")

    print()

    print("   c. 不支持的数据库类型:")
    config_unsupported = {
        'DB_TYPE': 'mongodb'
    }

    try:
        config = WxKfSaasConfig(**config_unsupported)
        print(f"   ❌ 应该报错，但成功了: {config.db_url}")
    except Exception as e:
        print(f"   ✅ 正确报错: {e}")


def show_database_recommendations():
    """显示数据库推荐配置"""
    print("\n📋 数据库配置建议:")

    print("\n1. 🔗 配置方式选择:")
    print("   方式1: 环境变量（推荐用于开发/生产）")
    print("     - 灵活，支持不同环境")
    print("     - 容器化部署友好")
    print("     - 示例: DB_HOST, DB_PORT, DB_NAME 等")

    print("\n   方式2: 直接URL（推荐用于特殊配置）")
    print("     - 完整控制连接字符串")
    print("     - 支持特殊参数和选项")
    print("     - 示例: DATABASE_URL=mysql+pymysql://user:pass@host/db")

    print("\n2. 🚀 数据库类型建议:")
    print("   MySQL:")
    print("     - 优点: 广泛使用，云服务成熟")
    print("     - 场景: 传统业务，云数据库")
    print("     - 异步驱动: aiomysql")

    print("\n   PostgreSQL:")
    print("     - 优点: 功能强大，性能优秀")
    print("     - 场景: 复杂查询，事务要求高")
    print("     - 异步驱动: asyncpg")

    print("\n   SQLite:")
    print("     - 优点: 零配置，轻量级")
    print("     - 场景: 开发测试，小型应用")
    print("     - 异步驱动: aiosqlite")

    print("\n3. ⚡ 性能优化建议:")
    print("   连接池配置:")
    print("     - 小型: 5-10 核心连接")
    print("     - 中型: 10-20 核心连接")
    print("     - 大型: 20-50 核心连接")
    print("     - DB_MAX_OVERFLOW = 核心连接 × 2")

    print("\n   异步vs同步:")
    print("     - 生产环境: 优先使用异步")
    print("     - 开发环境: 同步也可用")
    print("     - 同步引擎: 用于迁移、管理任务")

    print("\n4. 🔒 安全配置建议:")
    print("   环境变量:")
    print("     - 不要在代码中硬编码密码")
    print("     - 使用密钥管理系统")
    print("     - 定期轮换凭据")

    print("\n   连接安全:")
    print("     - 生产环境使用SSL/TLS")
    print("     - 限制数据库访问IP")
    print("     - 使用最小权限原则")

    print("\n5. 📦 部署建议:")
    print("   Docker:")
    print("     - 环境变量注入")
    print("     - 数据持久化卷")
    print("     - 健康检查配置")

    print("\n   云服务:")
    print("     - 内网连接地址")
    print("     - 连接池监控")
    print("     - 备份策略配置")


if __name__ == "__main__":
    test_database_configs()
    show_database_recommendations()