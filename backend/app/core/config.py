from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[".env", "../.env"], env_file_encoding="utf-8", extra="ignore")
    ENV: Literal["dev", "prod"] = "dev"
    JWT_SECRET_KEY: str = "your-secret-key"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL_NAME: str = "gpt-4"
    OPENAI_BASE_URL: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    LLAMA_CLOUD_API_KEY: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None
    QDRANT_URL: Optional[str] = None
    DATABASE_TYPE: Literal["sqlite", "postgres"] = "sqlite"
    POSTGRES_URL: Optional[str] = None
    STORAGE_TYPE: Literal["local"] = "local"
    FRONTEND_URL: str = "http://localhost:5173"


settings = Settings()
