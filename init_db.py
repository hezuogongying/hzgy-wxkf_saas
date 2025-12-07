#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
用于创建所有必要的数据库表
"""

import asyncio
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def init_database():
    """初始化数据库"""
    try:
        # 导入必要的模块
        from core.config import WxKfSaasConfig
        from core.database import DatabaseManager

        # 加载配置
        config = WxKfSaasConfig()
        logger.info(f"数据库URL: {config.database_url}")

        # 创建数据库管理器
        db_manager = DatabaseManager(config)

        # 导入所有模型以确保它们被注册到Base.metadata
        from models.tenant import Tenant

        # 创建所有表
        logger.info("正在创建数据库表...")
        async with db_manager.engine.begin() as conn:
            await conn.run_sync(Tenant.metadata.create_all)

        logger.info("✅ 数据库表创建成功！")

        # 检查表是否创建成功
        async with db_manager.get_session() as session:
            # 检查tenants表
            result = await session.execute("SHOW TABLES LIKE 'tenants'")
            if result.fetchone():
                logger.info("✅ tenants表创建成功")

                # 插入测试数据（如果表为空）
                result = await session.execute("SELECT COUNT(*) FROM tenants")
                count = result.scalar()

                if count == 0:
                    logger.info("创建默认租户...")
                    test_tenant = Tenant(
                        corp_id="ww4c543662478cf668",
                        corp_name="测试企业",
                        contact_name="系统管理员",
                        contact_phone="400-123-4567",
                        contact_email="admin@example.com",
                        permanent_code="test_permanent_code",
                        is_authorized=False,
                        callback_url="https://wxkf.shoudu888.com/callback/customer-service",
                        callback_token="KLNsSkfx9",
                        callback_aes_key="wOoBhDpcsBEC1YlQrD768hPFufWAIkWXS7y1bsWAFtK"
                    )
                    session.add(test_tenant)
                    await session.commit()
                    logger.info("✅ 默认租户创建成功")
                else:
                    logger.info(f"tenants表已有 {count} 条记录")
            else:
                logger.error("❌ tenants表创建失败")

        await db_manager.engine.dispose()
        logger.info("数据库初始化完成！")

    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        raise

async def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("微信客服SaaS服务 - 数据库初始化")
    logger.info(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    await init_database()

    logger.info("=" * 60)
    logger.info("初始化完成！")
    logger.info("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())