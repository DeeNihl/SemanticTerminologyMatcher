"""Configuration settings for Semantic Terminology Matcher."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Qdrant Configuration
    qdrant_host: str = Field(default="localhost", description="Qdrant server host")
    qdrant_port: int = Field(default=6333, description="Qdrant server port")
    qdrant_collection_name: str = Field(
        default="omop_concepts", description="Qdrant collection name"
    )
    qdrant_api_key: str = Field(default="", description="Qdrant API key (optional)")

    # Embedding Model
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2", description="Sentence transformer model name"
    )

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="FastAPI host")
    api_port: int = Field(default=8000, description="FastAPI port")

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
