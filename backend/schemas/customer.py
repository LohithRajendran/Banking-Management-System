"""
Customer Pydantic Schemas
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CustomerCreate(BaseModel):
    full_name: str
    phone: str
    address: Optional[str] = None
    date_of_birth: Optional[date] = None


class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None


class CustomerResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    phone: str
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
