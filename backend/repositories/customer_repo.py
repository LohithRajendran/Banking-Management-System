"""
Customer Repository
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.customer import Customer
from repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, session: AsyncSession):
        super().__init__(Customer, session)

    async def get_by_user_id(self, user_id: int) -> Optional[Customer]:
        result = await self.session.execute(select(Customer).where(Customer.user_id == user_id))
        return result.scalars().first()
