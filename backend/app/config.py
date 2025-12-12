from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=[".env", "../.env"], env_file_encoding="utf-8", extra="ignore")

    # General
    ENV: Literal["dev", "prod"] = "dev"
    
    # API Keys (BYOK - users provide their own via Settings page)
    # These are now optional - only used as fallback for development
    OPENAI_API_KEY: Optional[str] = None
    LLAMA_CLOUD_API_KEY: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None
    QDRANT_URL: Optional[str] = None
    
    # Database
    DATABASE_TYPE: Literal["sqlite", "postgres"] = "sqlite"
    POSTGRES_URL: Optional[str] = None
    
    # Storage
    STORAGE_TYPE: Literal["local", "s3", "supabase"] = "local"
    S3_ENDPOINT_URL: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_BUCKET_NAME: Optional[str] = "rag-bucket"
    S3_REGION: Optional[str] = "us-east-1"
    
    # Supabase (required for production)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    
    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

settings = Settings()
