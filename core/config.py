# -*- coding: utf-8 -*-
"""微信客服API SaaS配置模块 - 支持多租户"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class WxKfSaasConfig(BaseSettings):
    """微信客服SaaS配置模型 - 多租户模式

    这个配置专门为SaaS模式设计,支持:
    1. 服务商模式(帮助多个企业管理微信客服)
    2. 多租户Token管理
    3. 数据库支持(必需,用于存储多租户配置)
    4. Redis支持(推荐,用于Token缓存)

    Attributes:
        # 服务商配置(必需)
        suite_id: 服务商套件ID
        suite_secret: 服务商套件Secret
        provider_secret: 服务商密钥
        provider_token: 服务商回调Token
        provider_encoding_aes_key: 服务商回调加密密钥

        # 服务器配置
        server_url: 服务器地址
        fastapi_host: FastAPI监听地址
        fastapi_port: FastAPI监听端口

        # 数据库配置(必需)
        db_host: 数据库主机
        db_port: 数据库端口
        db_name: 数据库名称
        db_user: 数据库用户
        db_password: 数据库密码

        # Redis配置(推荐)
        redis_host: Redis主机
        redis_port: Redis端口
        redis_db: Redis数据库编号
        redis_password: Redis密码

        # OpenAI配置(可选,用于AI客服)
        openai_api_key: OpenAI API密钥
        openai_base_url: OpenAI API基础URL
        openai_model_name: OpenAI模型名称
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # ===== 服务商模式配置(必需) =====
    suite_id: str
    suite_secret: str
    provider_secret: str
    provider_token: str
    provider_encoding_aes_key: str

    # ===== 服务器配置 =====
    server_url: Optional[str] = None
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8083

    # ===== 数据库配置(必需) =====
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str
    db_user: str
    db_password: str
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # ===== Redis配置(推荐) =====
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_key_prefix: str = "wxkf_saas:"

    # ===== OpenAI配置(可选) =====
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = "https://api.openai.com/v1"
    openai_model_name: Optional[str] = "gpt-3.5-turbo"
    openai_system_prompt: Optional[str] = None

    # ===== 日志配置 =====
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # ===== SaaS服务配置 =====
    enable_tenant_isolation: bool = True  # 启用租户隔离
    max_tenants: int = 1000  # 最大租户数
    token_cache_ttl: int = 7000  # Token缓存时间(秒)

    @property
    def redis_url(self) -> str:
        """构建Redis连接URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def db_url(self) -> str:
        """构建数据库连接URL"""
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
            f"?charset=utf8mb4"
        )

    @property
    def db_async_url(self) -> str:
        """构建异步数据库连接URL"""
        return (
            f"mysql+aiomysql://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
            f"?charset=utf8mb4"
        )

    def validate_config(self):
        """验证配置完整性"""
        required_fields = [
            ('suite_id', '服务商套件ID'),
            ('suite_secret', '服务商套件Secret'),
            ('provider_secret', '服务商密钥'),
            ('provider_token', '服务商回调Token'),
            ('provider_encoding_aes_key', '服务商回调加密密钥'),
            ('db_name', '数据库名称'),
            ('db_user', '数据库用户'),
            ('db_password', '数据库密码'),
        ]

        missing_fields = []
        for field_name, field_desc in required_fields:
            if not getattr(self, field_name, None):
                missing_fields.append(field_desc)

        if missing_fields:
            raise ValueError(
                f"SaaS模式缺少必需配置: {', '.join(missing_fields)}"
            )
