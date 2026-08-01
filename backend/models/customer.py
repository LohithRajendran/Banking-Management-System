"""
Customer Profile Model
"""

from typing import List, TYPE_CHECKING, Optional
from datetime import date
from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from models.user import User
    from models.account import Account


class Customer(Base, TimestampMixin):
    """Customer profile linked to a User account."""
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="customer")
    accounts: Mapped[List["Account"]] = relationship("Account", back_populates="customer", cascade="all, delete-orphan")
