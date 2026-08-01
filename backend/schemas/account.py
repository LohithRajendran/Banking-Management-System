"""
Account Pydantic Schemas
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from models.account import AccountType


class AccountCreate(BaseModel):
    account_type: AccountType
    initial_deposit: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"))


class AccountResponse(BaseModel):
    id: int
    customer_id: int
    account_number: str
    account_type: AccountType
    balance: Decimal
    min_balance: Decimal
    overdraft_limit: Decimal
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
