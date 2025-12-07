# -*- coding: utf-8 -*-
"""应用启动测试脚本"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_config_loading():
    """测试配置加载"""
    print("[1/4] 测试配置加载...")
    try:
        from core.config import WxKfSaasConfig
        config = WxKfSaasConfig()
        config.validate_config()
        print("✅ 配置加载成功")
        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return False


def test_database_connection():
    """测试数据库连接"""
    print("[2/4] 测试数据库连接...")
    try:
        from core.database import DatabaseManager
        from core.config import WxKfSaasConfig

        # 加载配置
        config = WxKfSaasConfig()

        # 创建数据库管理器并初始化
        db_manager = DatabaseManager()
        db_manager.init_sync()

        # 测试连接
        engine = db_manager.sync_engine
        with engine.connect() as conn:
            result = conn.execute("SELECT 1 as test")
            assert result.fetchone()[0] == 1
        print("✅ 数据库连接成功")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def test_redis_connection():
    """测试 Redis 连接"""
    print("[3/4] 测试 Redis 连接...")
    try:
        from core.config import WxKfSaasConfig
        config = WxKfSaasConfig()

        import redis
        r = redis.from_url(config.redis_url)
        r.ping()
        print("✅ Redis 连接成功")
        return True
    except Exception as e:
        print(f"⚠️ Redis 连接失败（可能未配置）: {e}")
        return True  # Redis 不是必需的


def test_fastapi_app():
    """测试 FastAPI 应用创建"""
    print("[4/4] 测试 FastAPI 应用...")
    try:
        from main import app
        # 测试应用是否可以创建
        assert hasattr(app, 'title')
        print(f"✅ FastAPI 应用创建成功: {app.title}")
        return True
    except Exception as e:
        print(f"❌ FastAPI 应用创建失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("应用启动测试")
    print("="*60)

    # 设置测试环境变量
    os.environ.setdefault('PYTHONPATH', str(project_root))

    # 运行测试
    tests = [
        test_config_loading,
        test_database_connection,
        test_redis_connection,
        test_fastapi_app
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "-"*60)
    print(f"测试结果: {passed}/{total} 通过")

    if passed == total:
        print("✅ 所有测试通过！应用可以正常启动")
    else:
        print("⚠️ 部分测试失败，请检查配置")
        sys.exit(1)

    print("="*60)


if __name__ == "__main__":
    main()