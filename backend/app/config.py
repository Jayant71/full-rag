from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=[".env", "../.env"], env_file_encoding="utf-8", extra="ignore")

    # General
    ENV: Literal["dev", "prod"] = "dev"
    
    # API Keys
    OPENAI_API_KEY: str
    LLAMA_CLOUD_API_KEY: str
    COHERE_API_KEY: Optional[str] = None
    
    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    
    # Database
    DATABASE_TYPE: Literal["sqlite", "postgres"] = "sqlite"
    POSTGRES_URL: Optional[str] = None
    
    # Storage
    STORAGE_TYPE: Literal["local", "s3"] = "local"
    S3_ENDPOINT_URL: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_BUCKET_NAME: Optional[str] = "rag-bucket"
    S3_REGION: Optional[str] = "us-east-1"

settings = Settings()
