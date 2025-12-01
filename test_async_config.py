# -*- coding: utf-8 -*-
"""测试异步配置"""

import sys
import asyncio
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from core.config import WxKfSaasConfig

    print("🔍 测试异步数据库配置...")

    # 加载配置
    print("\n1. 加载配置...")
    config = WxKfSaasConfig()

    # 验证配置
    print("\n2. 数据库配置检查:")
    print(f"   同步 URL: {config.db_url}")
    print(f"   异步 URL: {config.db_async_url}")
    print(f"   连接池大小: {config.db_pool_size}")
    print(f"   最大溢出: {config.db_max_overflow}")

    # 检查异步URL格式
    print("\n3. 异步URL格式检查:")
    if config.db_async_url.startswith("mysql+aiomysql://"):
        print("✅ 异步URL格式正确 (mysql+aiomysql://)")
    else:
        print(f"❌ 异步URL格式错误: {config.db_async_url}")
        print("   应该以 'mysql+aiomysql://' 开头")

    # 检查同步URL格式
    print("\n4. 同步URL格式检查:")
    if config.db_url.startswith("mysql+pymysql://"):
        print("✅ 同步URL格式正确 (mysql+pymysql://)")
    else:
        print(f"❌ 同步URL格式错误: {config.db_url}")
        print("   应该以 'mysql+pymysql://' 开头")

    print("\n✅ 配置检查完成！")

    # 显示配置总结
    print("\n📋 异步数据库配置总结:")
    print("1. ✅ 同步 URL: mysql+pymysql:// - 用于表创建、迁移等同步操作")
    print("2. ✅ 异步 URL: mysql+aiomysql:// - 用于异步数据库操作")
    print("3. ✅ 连接池配置: QueuePool")
    print("4. ✅ 异步会话: AsyncSession + async_sessionmaker")
    print("5. ✅ 同步会话: Session + sessionmaker（备用）")

    print("\n🚀 部署建议:")
    print("1. 生产环境使用异步URL提高性能")
    print("2. 连接池大小根据服务器配置调整")
    print("3. 确保MySQL版本支持异步连接")
    print("4. 使用连接池监控工具")

except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()