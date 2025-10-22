"""
Configuration settings for Semantic Terminology Matcher
"""
from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Qdrant settings
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "terminology"
    qdrant_api_key: Optional[str] = None
    qdrant_use_memory: bool = False  # Use in-memory storage for testing
    
    # Embedding model settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384  # Dimension for all-MiniLM-L6-v2
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    class Config:
        env_file = ".env"
        env_prefix = "STM_"


settings = Settings()
