# -*- coding: utf-8 -*-
"""
Alembic环境配置
用于数据库迁移管理
"""

from logging.config import fileConfig
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 导入应用的配置和模型
from core.config import WxKfSaasConfig
from models.tenant import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# 使用应用的数据库配置
app_config = WxKfSaasConfig()
config.set_main_option('sqlalchemy.url', app_config.database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 添加模型的元数据对象，用于'autogenerate'支持
# 导入所有模型以确保它们被注册
target_metadata = Base.metadata

# 其他配置值可以从config中获取
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """在'离线'模式下运行迁移。

    这仅使用URL配置上下文，不需要Engine。
    通过跳过Engine创建，我们甚至不需要DBAPI可用。

    这里的context.execute()调用会将给定的字符串发出到脚本输出。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # 比较类型时忽略默认值
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在'在线'模式下运行迁移。

    在这种情况下，我们需要创建一个Engine
    并将连接与上下文关联。
    """
    # 使用应用的数据库配置创建引擎
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # 比较类型时忽略默认值
            compare_type=True,
            compare_server_default=True,
            # 自动生成时包含的对象类型
            include_object=include_object,
            # 自定义渲染函数
            render_item=render_item,
        )

        with context.begin_transaction():
            context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    """决定是否在自动生成时包含特定对象"""
    # 跳过alembic版本表
    if type_ == "table" and name == "alembic_version":
        return False
    # 包含其他所有对象
    return True


def render_item(type_, obj, autogen_context):
    """自定义渲染项"""
    # 这里可以添加自定义渲染逻辑
    # 例如处理枚举类型、特殊约束等
    return False


# 根据模式选择运行方式
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()