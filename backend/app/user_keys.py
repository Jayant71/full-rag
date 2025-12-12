"""
User API Keys & Configuration Service - Fetches per-user settings from Supabase.

For public deployments: Users MUST provide their own API keys and infrastructure URLs.
No fallback to environment variables.
"""
from typing import Optional
from dataclasses import dataclass
from fastapi import HTTPException
import httpx
from app.config import settings


@dataclass
class UserAPIKeys:
    """Container for user's API keys and configuration."""
    openai_api_key: Optional[str] = None
    llama_cloud_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    qdrant_url: Optional[str] = None
    
    def get_openai_key(self) -> str:
        """Get OpenAI key. Raises error if not configured."""
        if not self.openai_api_key:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not configured. Please add your API key in Settings."
            )
        return self.openai_api_key
    
    def get_llama_cloud_key(self) -> str:
        """Get LlamaCloud key. Raises error if not configured."""
        if not self.llama_cloud_api_key:
            raise HTTPException(
                status_code=400,
                detail="LlamaCloud API key not configured. Please add your API key in Settings."
            )
        return self.llama_cloud_api_key
    
    def get_cohere_key(self) -> Optional[str]:
        """Get Cohere key (optional - returns None if not set)."""
        return self.cohere_api_key
    
    def get_qdrant_url(self) -> str:
        """Get Qdrant URL. Raises error if not configured."""
        if not self.qdrant_url:
            raise HTTPException(
                status_code=400,
                detail="Qdrant URL not configured. Please add your Qdrant instance URL in Settings."
            )
        return self.qdrant_url
    
    def has_required_keys(self) -> bool:
        """Check if user has configured required API keys and URLs."""
        return bool(self.openai_api_key and self.llama_cloud_api_key and self.qdrant_url)
    
    def validate_for_ingestion(self):
        """Validate that all keys required for ingestion are present."""
        missing = []
        if not self.openai_api_key:
            missing.append("OpenAI API Key")
        if not self.llama_cloud_api_key:
            missing.append("LlamaCloud API Key")
        if not self.qdrant_url:
            missing.append("Qdrant URL")
        
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required configuration: {', '.join(missing)}. Please configure them in Settings before uploading documents."
            )
    
    def validate_for_chat(self):
        """Validate that all keys required for chat are present."""
        missing = []
        if not self.openai_api_key:
            missing.append("OpenAI API Key")
        if not self.qdrant_url:
            missing.append("Qdrant URL")
        
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required configuration: {', '.join(missing)}. Please configure them in Settings before using chat."
            )


async def get_user_api_keys(user_id: str) -> UserAPIKeys:
    """
    Fetch user's API keys and configuration from Supabase.
    Returns UserAPIKeys (may have None values if not configured).
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        # Supabase not configured - return empty keys (will fail validation)
        return UserAPIKeys()
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SUPABASE_URL}/rest/v1/user_configs",
                params={"user_id": f"eq.{user_id}", "select": "*"},
                headers={
                    "apikey": settings.SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    config = data[0]
                    return UserAPIKeys(
                        openai_api_key=config.get("openai_api_key"),
                        llama_cloud_api_key=config.get("llama_cloud_api_key"),
                        cohere_api_key=config.get("cohere_api_key"),
                        qdrant_url=config.get("qdrant_url"),
                    )
    except Exception as e:
        print(f"Failed to fetch user API keys: {e}")
    
    return UserAPIKeys()
