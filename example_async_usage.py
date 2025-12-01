# -*- coding: utf-8 -*-
"""异步数据库使用示例"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.config import WxKfSaasConfig
from core.database import init_database_sync, get_db_manager, get_async_db
from models.tenant import Tenant, TenantToken


async def example_tenant_operations():
    """演示异步租户操作"""
    print("🔧 异步数据库操作示例:")

    # 获取数据库管理器
    db_manager = get_db_manager()

    async for session in get_async_db():
        try:
            # 1. 查询所有租户
            print("\n1. 查询租户列表...")
            stmt = select(Tenant)
            result = await session.execute(stmt)
            tenants = result.scalars().all()

            if tenants:
                print(f"   找到 {len(tenants)} 个租户:")
                for tenant in tenants[:3]:  # 只显示前3个
                    print(f"   - {tenant.name} ({tenant.corp_id})")
            else:
                print("   暂无租户数据")

            # 2. 创建新租户示例（注释掉，避免实际创建）
            # print("\n2. 创建新租户...")
            # new_tenant = Tenant(
            #     corp_id="example_corp_id",
            #     name="示例企业",
            #     is_authorized=True
            # )
            # session.add(new_tenant)
            # await session.commit()
            # print("   ✅ 租户创建成功")

            # 3. 查询Token信息
            print("\n3. 查询Token信息...")
            token_stmt = select(TenantToken).where(TenantToken.corp_id == "_provider_")
            token_result = await session.execute(token_stmt)
            provider_tokens = token_result.scalars().all()

            print(f"   Provider Token 数量: {len(provider_tokens)}")

            # 4. 批量查询
            print("\n4. 批量查询操作...")
            batch_stmt = select(Tenant).where(Tenant.is_authorized == True)
            batch_result = await session.execute(batch_stmt)
            authorized_tenants = batch_result.scalars().all()

            print(f"   已授权租户数量: {len(authorized_tenants)}")

        except Exception as e:
            print(f"   ❌ 操作失败: {e}")
            await session.rollback()
            raise

async def example_connection_info():
    """显示连接信息"""
    config = WxKfSaasConfig()

    print("\n📊 数据库连接信息:")
    print(f"   同步URL: {config.db_url}")
    print(f"   异步URL: {config.db_async_url}")
    print(f"   连接池大小: {config.db_pool_size}")
    print(f"   最大溢出: {config.db_max_overflow}")
    print(f"   预检查: True")
    print(f"   日志模式: {config.log_level}")


async def main():
    """主函数"""
    print("🚀 异步数据库使用演示\n")

    # 初始化数据库（同步方式创建表）
    print("1. 初始化数据库...")
    try:
        config = WxKfSaasConfig()
        db_manager = init_database_sync(config)  # 使用同步初始化创建表
        print("   ✅ 数据库初始化成功")
    except Exception as e:
        print(f"   ❌ 数据库初始化失败: {e}")
        print("   💡 请检查数据库连接配置")
        return

    # 显示连接信息
    await example_connection_info()

    # 演示异步操作
    await example_tenant_operations()

    print("\n✅ 异步数据库演示完成!")

    print("\n📝 使用要点:")
    print("1. 使用 AsyncSession 进行所有数据库操作")
    print("2. 使用 await session.execute() 执行查询")
    print("3. 使用 async for session in get_async_db(): 获取会话")
    print("4. 自动提交和异常回滚已处理")
    print("5. 连接池自动管理")


if __name__ == "__main__":
    # 运行异步示例
    asyncio.run(main())