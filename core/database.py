# -*- coding: utf-8 -*-
"""数据库管理模块 - 异步版本"""

from typing import Generator, AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from wxkf_saas.core.config import WxKfSaasConfig
from wxkf_saas.models.tenant import Base


class DatabaseManager:
    """异步数据库管理器"""

    def __init__(self, config: WxKfSaasConfig):
        """初始化数据库管理器

        Args:
            config: SaaS配置对象
        """
        self.config = config

        # 创建异步数据库引擎
        self.async_engine = create_async_engine(
            config.db_async_url,
            poolclass=QueuePool,
            pool_size=config.db_pool_size,
            max_overflow=config.db_max_overflow,
            pool_pre_ping=True,  # 检查连接健康状态
            echo=config.log_level == "DEBUG",  # DEBUG模式下打印SQL
        )

        # 创建同步数据库引擎（用于表创建等同步操作）
        self.sync_engine = create_engine(
            config.db_url,
            poolclass=QueuePool,
            pool_size=config.db_pool_size,
            max_overflow=config.db_max_overflow,
            pool_pre_ping=True,
            echo=config.log_level == "DEBUG",
        )

        # 创建异步会话工厂
        self.AsyncSessionLocal = async_sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        # 创建同步会话工厂（备用）
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.sync_engine
        )

    async def create_tables(self):
        """异步创建所有表"""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def create_tables_sync(self):
        """同步创建所有表（备用方法）"""
        Base.metadata.create_all(bind=self.sync_engine)

    async def drop_tables(self):
        """异步删除所有表(谨慎使用)"""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取异步数据库会话

        Yields:
            AsyncSession: 异步数据库会话
        """
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    def get_session(self) -> Generator[Session, None, None]:
        """获取同步数据库会话（备用）

        Yields:
            Session: 数据库会话
        """
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    async def close(self):
        """关闭数据库连接"""
        await self.async_engine.dispose()
        self.sync_engine.dispose()


# 全局数据库管理器实例
_db_manager: DatabaseManager = None


async def init_database(config: WxKfSaasConfig) -> DatabaseManager:
    """异步初始化数据库

    Args:
        config: SaaS配置对象

    Returns:
        DatabaseManager: 数据库管理器实例
    """
    global _db_manager
    _db_manager = DatabaseManager(config)
    await _db_manager.create_tables()
    return _db_manager


def init_database_sync(config: WxKfSaasConfig) -> DatabaseManager:
    """同步初始化数据库（备用方法）

    Args:
        config: SaaS配置对象

    Returns:
        DatabaseManager: 数据库管理器实例
    """
    global _db_manager
    _db_manager = DatabaseManager(config)
    _db_manager.create_tables_sync()
    return _db_manager


def get_db_manager() -> DatabaseManager:
    """获取全局数据库管理器实例

    Returns:
        DatabaseManager: 数据库管理器实例

    Raises:
        RuntimeError: 如果数据库未初始化
    """
    if _db_manager is None:
        raise RuntimeError("Database not initialized. Call init_database first.")
    return _db_manager


def get_db() -> Generator[Session, None, None]:
    """获取同步数据库会话(用于依赖注入，备用)

    Yields:
        Session: 数据库会话
    """
    return get_db_manager().get_session()


def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """获取异步数据库会话(用于依赖注入)

    Yields:
        AsyncSession: 异步数据库会话
    """
    return get_db_manager().get_async_session()
