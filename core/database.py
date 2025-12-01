# -*- coding: utf-8 -*-
"""数据库管理模块"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool

from wxkf_saas.core.config import WxKfSaasConfig
from wxkf_saas.models.tenant import Base


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, config: WxKfSaasConfig):
        """初始化数据库管理器

        Args:
            config: SaaS配置对象
        """
        self.config = config

        # 创建数据库引擎
        self.engine = create_engine(
            config.db_url,
            poolclass=QueuePool,
            pool_size=config.db_pool_size,
            max_overflow=config.db_max_overflow,
            pool_pre_ping=True,  # 检查连接健康状态
            echo=config.log_level == "DEBUG",  # DEBUG模式下打印SQL
        )

        # 创建会话工厂
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self):
        """创建所有表"""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """删除所有表(谨慎使用)"""
        Base.metadata.drop_all(bind=self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        """获取数据库会话

        Yields:
            Session: 数据库会话
        """
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def close(self):
        """关闭数据库连接"""
        self.engine.dispose()


# 全局数据库管理器实例
_db_manager: DatabaseManager = None


def init_database(config: WxKfSaasConfig) -> DatabaseManager:
    """初始化数据库

    Args:
        config: SaaS配置对象

    Returns:
        DatabaseManager: 数据库管理器实例
    """
    global _db_manager
    _db_manager = DatabaseManager(config)
    _db_manager.create_tables()
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
    """获取数据库会话(用于依赖注入)

    Yields:
        Session: 数据库会话
    """
    return get_db_manager().get_session()
