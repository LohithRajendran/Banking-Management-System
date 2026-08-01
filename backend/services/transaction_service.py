"""
Transaction Service — Atomic Financial Operations
Handles Deposit, Withdraw, Transfer with strict DB transaction isolation.
"""

from decimal import Decimal
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from models.transaction import Transaction, TransactionType
from models.account import AccountType
from repositories.account_repo import AccountRepository
from repositories.transaction_repo import TransactionRepository
from schemas.transaction import DepositRequest, WithdrawRequest, TransferRequest
from core.exceptions import bad_request_exception, not_found_exception, InsufficientFundsError


class TransactionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.account_repo = AccountRepository(session)
        self.transaction_repo = TransactionRepository(session)

    async def deposit(self, req: DepositRequest) -> Transaction:
        account = await self.account_repo.get_by_account_number(req.account_number)
        if not account or not account.is_active:
            raise not_found_exception("Active Account")

        account.balance += req.amount
        txn = Transaction(
            account_id=account.id,
            transaction_type=TransactionType.DEPOSIT,
            amount=req.amount,
            balance_after=account.balance,
            note=req.note or "Deposit",
        )
        return await self.transaction_repo.create(txn)

    async def withdraw(self, req: WithdrawRequest) -> Transaction:
        account = await self.account_repo.get_by_account_number(req.account_number)
        if not account or not account.is_active:
            raise not_found_exception("Active Account")

        available_funds = account.balance + account.overdraft_limit
        if account.account_type == AccountType.SAVINGS:
            available_funds = account.balance - account.min_balance

        if req.amount > available_funds:
            raise bad_request_exception("Insufficient funds for withdrawal")

        account.balance -= req.amount
        txn = Transaction(
            account_id=account.id,
            transaction_type=TransactionType.WITHDRAWAL,
            amount=req.amount,
            balance_after=account.balance,
            note=req.note or "Withdrawal",
        )
        return await self.transaction_repo.create(txn)

    async def transfer(self, req: TransferRequest) -> Transaction:
        if req.from_account_number == req.to_account_number:
            raise bad_request_exception("Cannot transfer to the same account")

        from_acc = await self.account_repo.get_by_account_number(req.from_account_number)
        to_acc = await self.account_repo.get_by_account_number(req.to_account_number)

        if not from_acc or not from_acc.is_active:
            raise not_found_exception("Sender Account")
        if not to_acc or not to_acc.is_active:
            raise not_found_exception("Recipient Account")

        available_funds = from_acc.balance + from_acc.overdraft_limit
        if from_acc.account_type == AccountType.SAVINGS:
            available_funds = from_acc.balance - from_acc.min_balance

        if req.amount > available_funds:
            raise bad_request_exception("Insufficient funds for transfer")

        # Atomic transfer execution
        from_acc.balance -= req.amount
        to_acc.balance += req.amount

        # Record sender transaction
        txn = Transaction(
            account_id=from_acc.id,
            to_account_id=to_acc.id,
            transaction_type=TransactionType.TRANSFER,
            amount=req.amount,
            balance_after=from_acc.balance,
            note=req.note or f"Transfer to {to_acc.account_number}",
        )
        return await self.transaction_repo.create(txn)
