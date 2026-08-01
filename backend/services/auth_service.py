"""
Auth Service — Authentication Business Logic
"""

from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User
from models.customer import Customer
from repositories.user_repo import UserRepository
from repositories.customer_repo import CustomerRepository
from schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from core.security import hash_password, verify_password, create_access_token, create_refresh_token
from core.exceptions import bad_request_exception, credentials_exception


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.customer_repo = CustomerRepository(session)

    async def register(self, req: RegisterRequest) -> TokenResponse:
        existing_user = await self.user_repo.get_by_email(req.email)
        if existing_user:
            raise bad_request_exception("Email already registered")

        # Create user
        user = User(
            email=req.email,
            hashed_password=hash_password(req.password),
        )
        user = await self.user_repo.create(user)

        # Create customer profile linked to user
        customer = Customer(
            user_id=user.id,
            full_name=req.full_name,
            phone=req.phone,
        )
        await self.customer_repo.create(customer)

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def login(self, req: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(req.email)
        if not user or not verify_password(req.password, user.hashed_password):
            raise credentials_exception()

        if not user.is_active:
            raise bad_request_exception("Account is deactivated")

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
