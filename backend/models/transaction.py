"""
Transaction History Model
"""

from enum import Enum
from typing import Optional, TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from models.account import Account


class TransactionType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    INTEREST = "interest"


class Transaction(Base, TimestampMixin):
    """Financial transaction ledger record."""
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    to_account_id: Mapped[Optional[int]] = mapped_column(ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    transaction_type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    note: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    account: Mapped["Account"] = relationship("Account", foreign_keys=[account_id], back_populates="transactions")
    to_account: Mapped[Optional["Account"]] = relationship("Account", foreign_keys=[to_account_id])
