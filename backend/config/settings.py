from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # 应用配置
    app_name: str = "ShadowForge API"
    app_version: str = "1.0.0"
    debug: bool = False

    # 安全配置
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # 数据库配置
    database_url: str = "sqlite:///./shadowforge.db"

    # 文件存储配置
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"

    # LLM配置
    llm_api_key: Optional[str] = None
    llm_base_url: Optional[str] = None
    llm_model: str = "qwen3.5-plus"

    # Redis配置（用于Celery）
    redis_url: str = "redis://localhost:6379/0"

    # CORS配置 - 使用字符串，在main.py中解析
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    class Config:
        env_file = ".env"
        case_sensitive = False  # 允许大小写不敏感
        env_prefix = ""  # 不使用前缀


# 创建设置实例
settings = Settings()