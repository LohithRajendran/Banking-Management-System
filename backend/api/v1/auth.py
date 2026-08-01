"""
Auth Routes — Register, Login, Refresh, Logout
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.redis_client import get_redis
from core.dependencies import oauth2_scheme
from schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.register(req)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    return await auth_service.login(req)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(token: str = Depends(oauth2_scheme), redis=Depends(get_redis)):
    """Blacklists access token in Redis."""
    await redis.setex(f"blacklist:{token}", 900, "1")
    return {"detail": "Successfully logged out"}
