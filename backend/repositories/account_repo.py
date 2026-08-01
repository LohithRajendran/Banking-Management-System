"""
Account Repository
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.account import Account
from repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account]):
    def __init__(self, session: AsyncSession):
        super().__init__(Account, session)

    async def get_by_account_number(self, account_number: str) -> Optional[Account]:
        result = await self.session.execute(
            select(Account).where(Account.account_number == account_number)
        )
        return result.scalars().first()

    async def get_by_customer_id(self, customer_id: int) -> List[Account]:
        result = await self.session.execute(
            select(Account).where(Account.customer_id == customer_id)
        )
        return list(result.scalars().all())
