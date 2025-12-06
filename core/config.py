# -*- coding: utf-8 -*-
"""微信客服API SaaS配置模块 - 支持多租户"""

import os
from typing import Optional, List, Union
from pathlib import Path
from pydantic import field_validator, model_validator, Field
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
        env_file=[str(Path(__file__).parent.parent / ".env"), ".env"],  # 先查找项目根目录，再查找当前目录
        env_file_encoding="utf-8",
        extra="allow",  # 允许额外字段
        case_sensitive=False  # 环境变量不区分大小写
    )

    # ===== 运行模式 =====
    # 支持两种模式: single(单体模式) 和 provider(服务商模式)
    mode: str = "single"  # 默认为单体模式

    # ===== 单体模式配置(企业自用) =====
    corp_id: Optional[str] = None
    corp_secret: Optional[str] = None
    corp_callback_url: Optional[str] = None
    corp_callback_token: Optional[str] = None
    corp_callback_encoding_aes_key: Optional[str] = None

    # ===== 服务商模式配置(可选) =====
    suite_id: Optional[str] = None
    suite_secret: Optional[str] = None
    provider_secret: Optional[str] = None
    provider_token: Optional[str] = None
    provider_encoding_aes_key: Optional[str] = None

    # ===== 服务器配置 =====
    server_url: Optional[str] = None
    fastapi_host: str = Field(default="0.0.0.0", description="服务监听地址")
    fastapi_port: int = Field(default=58083, description="服务端口")

    # ===== 数据库配置(必需) =====
    # 推荐直接配置数据库URL，避免重复配置
    database_url: str  # 同步URL (必需)
    async_database_url: str  # 异步URL (必需)

    # 以下配置已弃用，由database_url提供
    # db_type: str = "mysql"
    # db_host: Optional[str] = "localhost"
    # db_port: Optional[int] = 3306
    # db_name: Optional[str] = None
    # db_user: Optional[str] = None
    # db_password: Optional[str] = None
    # db_path: Optional[str] = "./data/app.db"  # SQLite专用
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # ===== Redis配置(推荐) =====
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_key_prefix: str = "wxkf_saas:"

    # ===== OpenAI配置(可选) =====
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API密钥")
    openai_base_url: Optional[str] = Field(default="https://api.openai.com/v1", description="OpenAI API基础URL")
    openai_model_name: Optional[str] = Field(default="gpt-3.5-turbo", description="OpenAI模型名称")
    openai_system_prompt: Optional[str] = Field(default="你是一个专业的客服助手", description="系统提示词")

    # ===== 日志配置 =====
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # ===== SaaS服务配置 =====
    enable_tenant_isolation: bool = True  # 启用租户隔离
    max_tenants: int = 1000  # 最大租户数
    token_cache_ttl: int = 7000  # Token缓存时间(秒)

    # ===== 扩展配置 =====
    # CORS配置 - 支持逗号分隔的多个域名
    cors_origins: Union[List[str], str] = ["*"]

    # 限流配置
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    # SSL/TLS配置
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None

    # 文件上传配置
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB

    # 微信回调URL配置
    callback_url_provider: Optional[str] = None
    callback_url_suite: Optional[str] = None

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """解析CORS origins，支持逗号分隔的字符串或列表"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v if v else ["*"]

    @field_validator('log_level', mode='before')
    @classmethod
    def normalize_log_level(cls, v):
        """规范化日志级别"""
        if isinstance(v, str):
            return v.upper()
        return v

    @field_validator('fastapi_port', mode='before')
    @classmethod
    def validate_port(cls, v):
        """验证端口号"""
        try:
            port = int(v)
            if not 1 <= port <= 65535:
                raise ValueError("端口号必须在1-65535之间")
            return port
        except (ValueError, TypeError):
            raise ValueError("端口号必须是有效的整数")

    @model_validator(mode='after')
    def validate_environment(self):
        """环境配置验证"""
        # 验证SSL证书配置
        if self.ssl_cert_path and not self.ssl_key_path:
            raise ValueError("配置了SSL证书路径时，也必须配置SSL私钥路径")
        if self.ssl_key_path and not self.ssl_cert_path:
            raise ValueError("配置了SSL私钥路径时，也必须配置SSL证书路径")

        # 验证文件上传目录
        if self.upload_dir:
            upload_path = Path(self.upload_dir)
            try:
                upload_path.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                raise ValueError(f"无法创建上传目录: {self.upload_dir}")

        return self

    @property
    def redis_url(self) -> str:
        """构建Redis连接URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @model_validator(mode='after')
    def validate_database_config(self):
        """验证数据库配置"""
        # 如果直接提供了URL，使用URL
        if self.database_url or self.async_database_url:
            return self

        # 根据数据库类型验证必需参数
        if self.db_type == "sqlite":
            if not self.db_path:
                raise ValueError("SQLite需要配置db_path")
        else:
            # MySQL/PostgreSQL需要连接参数
            required_fields = ['db_host', 'db_port', 'db_name', 'db_user', 'db_password']
            missing = [field for field in required_fields if not getattr(self, field)]
            if missing:
                raise ValueError(f"{self.db_type}需要配置: {', '.join(missing)}")

        return self

    def _build_url(self, driver: str, is_async: bool = False) -> str:
        """构建数据库URL的通用方法

        Args:
            driver: 数据库驱动名称 (pymysql, aiomysql, asyncpg, aiosqlite等)
            is_async: 是否为异步驱动

        Returns:
            str: 完整的数据库连接URL
        """
        db_type = self.db_type
        db_path = self.db_path
        db_user = self.db_user
        db_password = self.db_password
        db_host = self.db_host
        db_port = self.db_port
        db_name = self.db_name

        if db_type == "sqlite":
            if is_async:
                return f"sqlite+{driver}:///{db_path}"
            else:
                return f"sqlite+{driver}:///{db_path}"

        # MySQL/PostgreSQL
        from urllib.parse import quote_plus

        # URL编码用户名和密码
        username = quote_plus(db_user or "")
        password = quote_plus(db_password or "")

        # 构建基础URL
        base_url = f"{db_type}+{driver}://{username}:{password}@{db_host}:{db_port}/{db_name}"

        # 添加额外参数
        params = []

        if db_type == "mysql":
            params.append("charset=utf8mb4")
        elif db_type == "postgresql":
            # PostgreSQL参数
            pass

        if params:
            base_url += "?" + "&".join(params)

        return base_url

    @property
    def db_url(self) -> str:
        """构建同步数据库连接URL"""
        # 如果直接配置了URL，直接返回
        if self.database_url:
            return self.database_url

        # 根据数据库类型选择驱动
        if self.db_type == "mysql":
            return self._build_url("pymysql")
        elif self.db_type == "postgresql":
            return self._build_url("psycopg2")
        elif self.db_type == "sqlite":
            return self._build_url("sqlite")
        else:
            raise ValueError(f"不支持的数据库类型: {self.db_type}")

    @property
    def db_async_url(self) -> str:
        """构建异步数据库连接URL"""
        # 如果直接配置了URL，直接返回
        if self.async_database_url:
            return self.async_database_url

        # 根据数据库类型选择异步驱动
        if self.db_type == "mysql":
            return self._build_url("aiomysql", is_async=True)
        elif self.db_type == "postgresql":
            return self._build_url("asyncpg", is_async=True)
        elif self.db_type == "sqlite":
            return self._build_url("aiosqlite", is_async=True)
        else:
            raise ValueError(f"不支持的数据库类型: {self.db_type}")

    @property
    def server_full_url(self) -> Optional[str]:
        """获取完整的服务器URL"""
        if not self.server_url:
            return None

        # 确保URL以/结尾
        if not self.server_url.endswith('/'):
            return f"{self.server_url}/"
        return self.server_url

    @property
    def provider_callback_url(self) -> Optional[str]:
        """获取服务商回调URL"""
        if self.callback_url_provider:
            return self.callback_url_provider
        if self.server_full_url:
            return f"{self.server_full_url}callback/provider"
        return None

    @property
    def suite_callback_url(self) -> Optional[str]:
        """获取套件回调URL"""
        if self.callback_url_suite:
            return self.callback_url_suite
        if self.server_full_url:
            return f"{self.server_full_url}callback/suite"
        return None

    def get_upload_path(self, filename: str = None) -> Path:
        """获取上传文件路径"""
        upload_path = Path(self.upload_dir)
        if filename:
            return upload_path / filename
        return upload_path

    def validate_config(self):
        """验证配置完整性"""
        # 验证数据库URL配置
        if not self.database_url:
            raise ValueError("缺少必需的 DATABASE_URL 配置")

        if not self.async_database_url:
            raise ValueError("缺少必需的 ASYNC_DATABASE_URL 配置")

        # 从URL中提取信息用于显示
        try:
            import urllib.parse
            parsed = urllib.parse.urlparse(self.database_url)
            db_info = f"{parsed.hostname}:{parsed.port}/{parsed.path.lstrip('/')}"
            print(f"   数据库: {db_info}")
        except:
            print(f"   数据库: {self.database_url}")

        # 根据模式验证不同配置
        missing_fields = []

        if self.mode == "single":
            # 单体模式验证
            single_required_fields = [
                ('corp_id', '企业ID'),
                ('corp_secret', '企业Secret'),
            ]

            for field_name, field_desc in single_required_fields:
                if not getattr(self, field_name, None):
                    missing_fields.append(field_desc)

            if missing_fields:
                raise ValueError(
                    f"单体模式缺少必需配置: {', '.join(missing_fields)}"
                )

            print("✅ 使用单体模式（企业自用）")
            print(f"   企业ID: {self.corp_id}")

        elif self.mode == "provider":
            # 服务商模式验证
            provider_required_fields = [
                ('suite_id', '服务商套件ID'),
                ('suite_secret', '服务商套件Secret'),
                ('provider_secret', '服务商密钥'),
                ('provider_token', '服务商回调Token'),
                ('provider_encoding_aes_key', '服务商回调加密密钥'),
            ]

            for field_name, field_desc in provider_required_fields:
                if not getattr(self, field_name, None):
                    missing_fields.append(field_desc)

            if missing_fields:
                raise ValueError(
                    f"服务商模式缺少必需配置: {', '.join(missing_fields)}"
                )

            print("✅ 使用服务商模式（SaaS）")

        # 验证回调URL配置（用于生产环境）
        if not self.server_url:
            print("⚠️ 警告: 未配置SERVER_URL，生产环境需要配置以支持微信回调")

        if self.mode == "single" and not self.corp_callback_url:
            print("⚠️ 警告: 企业回调URL未配置，无法接收客户消息")

        if self.mode == "provider":
            if not self.provider_callback_url:
                print("⚠️ 警告: 服务商回调URL未配置，无法接收授权事件")

            if not self.suite_callback_url:
                print("⚠️ 警告: 套件回调URL未配置，无法接收企业授权事件")

    def print_config_summary(self):
        """打印配置摘要（隐藏敏感信息）"""
        print("\n📋 配置摘要:")
        print(f"   服务商: {self.suite_id[:8]}...")
        print(f"   数据库: {self.db_host}:{self.db_port}/{self.db_name}")
        print(f"   Redis: {self.redis_host}:{self.redis_port}/{self.redis_db}")
        print(f"   服务端口: {self.fastapi_port}")
        print(f"   服务器URL: {self.server_url or '未配置'}")
        print(f"   租户隔离: {'启用' if self.enable_tenant_isolation else '禁用'}")
        print(f"   最大租户数: {self.max_tenants}")
        print(f"   日志级别: {self.log_level}")

        if self.server_url:
            print(f"\n📞 回调URL:")
            print(f"   服务商回调: {self.provider_callback_url}")
            print(f"   套件回调: {self.suite_callback_url}")

        if self.openai_api_key:
            print(f"\n🤖 AI客服: 已配置")

        print("\n✅ 配置验证通过\n")
