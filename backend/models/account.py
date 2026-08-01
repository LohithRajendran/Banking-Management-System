"""
Bank Account Model — Savings & Current Accounts
"""

from enum import Enum
from typing import List, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import String, Numeric, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from models.customer import Customer
    from models.transaction import Transaction


class AccountType(str, Enum):
    SAVINGS = "savings"
    CURRENT = "current"


class Account(Base, TimestampMixin):
    """Bank account entity (Savings or Current)."""
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    account_number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    account_type: Mapped[AccountType] = mapped_column(SQLEnum(AccountType), nullable=False)
    balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    min_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("500.00"), nullable=False)
    overdraft_limit: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="accounts")
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction",
        foreign_keys="Transaction.account_id",
        back_populates="account",
        cascade="all, delete-orphan",
    )
