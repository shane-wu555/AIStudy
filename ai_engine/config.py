"""
AI引擎配置文件
"""
from pydantic_settings import BaseSettings
from typing import Optional


class AIEngineSettings(BaseSettings):
    """AI引擎配置"""
    
    # 服务配置
    AI_ENGINE_HOST: str = "0.0.0.0"
    AI_ENGINE_PORT: int = 8001
    
    # 模型配置
    DEFAULT_LLM: str = "openai"  # openai, wenxin, tongyi
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Vision模型
    VISION_MODEL: str = "gpt-4-vision-preview"
    
    # 向量数据库配置
    VECTOR_DB: str = "qdrant"  # qdrant, milvus, chromadb
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    
    # 推理配置
    MAX_CONTEXT_LENGTH: int = 10
    REASONING_TIMEOUT: int = 30
    
    # 知识库配置
    KB_EMBEDDING_DIM: int = 1536
    KB_TOP_K: int = 5
    
    class Config:
        env_file = ".env"


# 全局配置实例
ai_settings = AIEngineSettings()
