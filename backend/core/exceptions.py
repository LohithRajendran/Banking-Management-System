"""
Custom Application Exceptions
Defines standard domain exceptions for financial operations & security.
"""

from fastapi import HTTPException, status


class BankingException(Exception):
    """Base class for all domain business errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class InsufficientFundsError(BankingException):
    """Raised when an account does not have enough balance for a transaction."""
    pass


class InactiveAccountError(BankingException):
    """Raised when operating on a frozen/inactive account."""
    pass


class DuplicateAccountError(BankingException):
    """Raised when creating an account number that already exists."""
    pass


class InvalidTransactionError(BankingException):
    """Raised for illegal operations like negative deposit or self-transfer."""
    pass


# HTTP Exception Helpers for FastAPI routes
def credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden_exception(detail: str = "Permission denied") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
    )


def not_found_exception(item_name: str = "Resource") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{item_name} not found",
    )


def bad_request_exception(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail,
    )
