"""
Account Routes — Create & View Bank Accounts
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.dependencies import get_current_user_id
from schemas.account import AccountCreate, AccountResponse
from services.account_service import AccountService

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    req: AccountCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = AccountService(db)
    return await service.create_account(user_id, req)


@router.get("/", response_model=List[AccountResponse])
async def get_my_accounts(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = AccountService(db)
    return await service.get_user_accounts(user_id)
