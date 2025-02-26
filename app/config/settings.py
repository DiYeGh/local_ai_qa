from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # 应用基本配置
    APP_NAME: str = "本地知识库AI问答系统"
    API_V1_STR: str = "/api/v1"
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 30 * 1024 * 1024  # 30MB
    ALLOWED_EXTENSIONS: List[str] = ["txt", "docx"]
    
    # Milvus配置
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    COLLECTION_NAME: str = "document_chunks"
    VECTOR_DIM: int = 1024  # bge-m3 向量维度
    
    # Ollama配置
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    EMBEDDING_MODEL: str = "bge-m3"
    RERANK_MODEL: str = "bge-reranker-v2-m3"
    LLM_MODEL: str = "deepseek-coder:7b"
    
    # 文本分块配置
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    # 检索配置
    TOP_K: int = 5
    VECTOR_SEARCH_WEIGHT: float = 0.7
    BM25_WEIGHT: float = 0.3
    FINAL_CHUNKS_COUNT: int = 3

    class Config:
        case_sensitive = True

# 创建全局设置实例
settings = Settings()

# 确保上传目录存在
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
