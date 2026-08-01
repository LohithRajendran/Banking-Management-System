"""
Customer Profile Routes
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.dependencies import get_current_user_id
from repositories.customer_repo import CustomerRepository
from schemas.customer import CustomerResponse, CustomerUpdate
from core.exceptions import not_found_exception

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/me", response_model=CustomerResponse)
async def get_my_customer_profile(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = CustomerRepository(db)
    customer = await repo.get_by_user_id(user_id)
    if not customer:
        raise not_found_exception("Customer profile")
    return customer


@router.put("/me", response_model=CustomerResponse)
async def update_customer_profile(
    req: CustomerUpdate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = CustomerRepository(db)
    customer = await repo.get_by_user_id(user_id)
    if not customer:
        raise not_found_exception("Customer profile")

    if req.full_name is not None:
        customer.full_name = req.full_name
    if req.phone is not None:
        customer.phone = req.phone
    if req.address is not None:
        customer.address = req.address
    if req.date_of_birth is not None:
        customer.date_of_birth = req.date_of_birth

    await db.flush()
    return customer
