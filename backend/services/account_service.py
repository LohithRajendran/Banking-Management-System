"""
Account Service — Account Management Logic
"""

import random
from decimal import Decimal
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from models.account import Account, AccountType
from repositories.account_repo import AccountRepository
from repositories.customer_repo import CustomerRepository
from schemas.account import AccountCreate
from core.exceptions import bad_request_exception, not_found_exception


class AccountService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.account_repo = AccountRepository(session)
        self.customer_repo = CustomerRepository(session)

    def _generate_account_number(self) -> str:
        """Generate a random 10-digit account number starting with 10."""
        return f"10{''.join([str(random.randint(0, 9)) for _ in range(8)])}"

    async def create_account(self, user_id: int, req: AccountCreate) -> Account:
        customer = await self.customer_repo.get_by_user_id(user_id)
        if not customer:
            raise not_found_exception("Customer profile")

        # Set default rules based on type
        min_balance = Decimal("500.00") if req.account_type == AccountType.SAVINGS else Decimal("0.00")
        overdraft_limit = Decimal("1000.00") if req.account_type == AccountType.CURRENT else Decimal("0.00")

        if req.initial_deposit < min_balance:
            raise bad_request_exception(f"Minimum initial deposit for savings account is {min_balance}")

        account_number = self._generate_account_number()

        account = Account(
            customer_id=customer.id,
            account_number=account_number,
            account_type=req.account_type,
            balance=req.initial_deposit,
            min_balance=min_balance,
            overdraft_limit=overdraft_limit,
        )

        return await self.account_repo.create(account)

    async def get_user_accounts(self, user_id: int) -> List[Account]:
        customer = await self.customer_repo.get_by_user_id(user_id)
        if not customer:
            return []
        return await self.account_repo.get_by_customer_id(customer.id)
