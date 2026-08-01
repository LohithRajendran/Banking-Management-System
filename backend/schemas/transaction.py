"""
Transaction Pydantic Schemas
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from models.transaction import TransactionType


class DepositRequest(BaseModel):
    account_number: str
    amount: Decimal = Field(gt=Decimal("0.00"))
    note: Optional[str] = None


class WithdrawRequest(BaseModel):
    account_number: str
    amount: Decimal = Field(gt=Decimal("0.00"))
    note: Optional[str] = None


class TransferRequest(BaseModel):
    from_account_number: str
    to_account_number: str
    amount: Decimal = Field(gt=Decimal("0.00"))
    note: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    account_id: int
    to_account_id: Optional[int] = None
    transaction_type: TransactionType
    amount: Decimal
    balance_after: Decimal
    note: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
