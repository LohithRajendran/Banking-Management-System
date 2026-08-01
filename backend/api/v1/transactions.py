"""
Transaction Routes — Deposit, Withdraw, Transfer & History
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.dependencies import get_current_user_id
from repositories.account_repo import AccountRepository
from repositories.transaction_repo import TransactionRepository
from schemas.transaction import DepositRequest, WithdrawRequest, TransferRequest, TransactionResponse
from services.transaction_service import TransactionService
from core.exceptions import not_found_exception, forbidden_exception

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/deposit", response_model=TransactionResponse)
async def deposit(
    req: DepositRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = TransactionService(db)
    return await service.deposit(req)


@router.post("/withdraw", response_model=TransactionResponse)
async def withdraw(
    req: WithdrawRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = TransactionService(db)
    return await service.withdraw(req)


@router.post("/transfer", response_model=TransactionResponse)
async def transfer(
    req: TransferRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    service = TransactionService(db)
    return await service.transfer(req)


@router.get("/account/{account_number}", response_model=List[TransactionResponse])
async def get_transaction_history(
    account_number: str,
    skip: int = 0,
    limit: int = 50,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    acc_repo = AccountRepository(db)
    account = await acc_repo.get_by_account_number(account_number)
    if not account:
        raise not_found_exception("Account")

    txn_repo = TransactionRepository(db)
    return await txn_repo.get_by_account_id(account.id, skip=skip, limit=limit)
