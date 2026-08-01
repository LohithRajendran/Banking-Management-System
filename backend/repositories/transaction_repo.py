"""
Transaction Repository
"""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.transaction import Transaction
from repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: AsyncSession):
        super().__init__(Transaction, session)

    async def get_by_account_id(self, account_id: int, skip: int = 0, limit: int = 50) -> List[Transaction]:
        result = await self.session.execute(
            select(Transaction)
            .where(Transaction.account_id == account_id)
            .order_by(Transaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
