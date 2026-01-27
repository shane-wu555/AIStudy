"""
后端服务配置文件
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "NumbersFallIntoPlace Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务器配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "numbersfall"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    
    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # AI引擎配置
    AI_ENGINE_URL: str = "http://localhost:8001"
    
    # AI模型配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    WENXIN_API_KEY: Optional[str] = None
    WENXIN_SECRET_KEY: Optional[str] = None
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # CORS配置
    CORS_ORIGINS: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()
