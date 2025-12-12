"""
Authentication utilities for Supabase JWT verification.
"""
from typing import Optional
from fastapi import HTTPException, Header, Depends
from jose import jwt, JWTError
import httpx
from functools import lru_cache
from app.config import settings

# Supabase JWT configuration
SUPABASE_JWT_SECRET_URL_TEMPLATE = "{url}/rest/v1/"
SUPABASE_JWKS_URL_TEMPLATE = "{url}/auth/v1/.well-known/jwks.json"


class User:
    """Represents an authenticated user."""
    def __init__(self, id: str, email: str, user_metadata: dict = None):
        self.id = id
        self.email = email
        self.user_metadata = user_metadata or {}


@lru_cache()
def get_supabase_jwt_secret() -> Optional[str]:
    """
    For Supabase, we can verify JWTs using the project's JWT secret.
    This is available in the Supabase dashboard under Project Settings > API.
    """
    # Supabase uses a consistent JWT secret per project
    # In production, you'd get this from SUPABASE_JWT_SECRET env var
    return None


async def verify_jwt_token(token: str) -> dict:
    """
    Verify a Supabase JWT token.
    
    Note: For production, you should:
    1. Use the SUPABASE_JWT_SECRET to verify locally, or
    2. Call Supabase's /auth/v1/user endpoint to validate
    """
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        # If Supabase is not configured, skip auth (development mode)
        return None
    
    try:
        # Call Supabase to verify the token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.SUPABASE_URL}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": settings.SUPABASE_SERVICE_KEY,
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
    except Exception as e:
        print(f"JWT verification failed: {e}")
        return None


async def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization")
) -> Optional[User]:
    """
    FastAPI dependency to get the current authenticated user.
    
    If Supabase is not configured, returns None (allowing unauthenticated access).
    This is useful for development/testing without auth.
    """
    # If no Supabase config, allow unauthenticated access
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        return None
    
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = parts[1]
    
    # Verify the token
    user_data = await verify_jwt_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return User(
        id=user_data.get("id"),
        email=user_data.get("email"),
        user_metadata=user_data.get("user_metadata", {})
    )


async def get_optional_user(
    authorization: Optional[str] = Header(None, alias="Authorization")
) -> Optional[User]:
    """
    FastAPI dependency to optionally get the current user.
    Returns None if not authenticated (doesn't raise an error).
    """
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization)
    except HTTPException:
        return None
