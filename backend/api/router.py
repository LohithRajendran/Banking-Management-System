"""
Main API v1 Router Aggregator
"""

from fastapi import APIRouter
from api.v1.auth import router as auth_router
from api.v1.users import router as users_router
from api.v1.customers import router as customers_router
from api.v1.accounts import router as accounts_router
from api.v1.transactions import router as transactions_router

api_router = APIRouter(prefix="/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(customers_router)
api_router.include_router(accounts_router)
api_router.include_router(transactions_router)
