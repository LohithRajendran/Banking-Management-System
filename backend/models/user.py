"""
User Model — Authentication & User Account
"""

from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from models.customer import Customer


class User(Base, TimestampMixin):
    """User account entity for login and authorization."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 1-to-1 relationship with Customer profile
    customer: Mapped[Optional["Customer"]] = relationship(
        "Customer", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
