"""
FastAPI Dependency Injections
Provides reusable security and session dependencies for API endpoints.
"""

from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.redis_client import get_redis
from core.security import decode_token
from core.exceptions import credentials_exception

# OAuth2 token URL endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    redis = Depends(get_redis),
) -> int:
    """
    Validates bearer token and checks token blacklist in Redis.
    Returns user ID extracted from token payload.
    """
    # Check if token is blacklisted (logged out)
    is_blacklisted = await redis.get(f"blacklist:{token}")
    if is_blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been invalidated (logged out)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception()

    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception()

    return int(user_id)
