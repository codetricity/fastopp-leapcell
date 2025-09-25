"""
FastAPI Users setup for base_assets
Simple version without dependency injection
"""
import uuid
from fastapi import HTTPException
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieAuthentication
from fastapi_users.password import PasswordHelper
from sqlmodel import select
from db import AsyncSessionLocal
from models import User

# Simple cookie authentication
cookie_authentication = CookieAuthentication(
    secret="dev_secret_key_change_in_production",
    lifetime_seconds=1800,  # 30 minutes
    cookie_name="access_token",
    cookie_secure=False,  # Set to True in production with HTTPS
)

# FastAPI Users setup
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [cookie_authentication]
)

# User manager
class UserManager:
    def __init__(self):
        self.password_helper = PasswordHelper()

    async def get(self, user_id: uuid.UUID) -> User:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user

    async def get_by_email(self, email: str) -> User:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user

    async def create(self, user_create: dict) -> User:
        # Simple user creation - in production, use proper validation
        user = User(
            email=user_create["email"],
            hashed_password=self.password_helper.hash(user_create["password"]),
            is_active=True,
            is_superuser=False,
            is_staff=False
        )
        async with AsyncSessionLocal() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

def get_user_manager():
    return UserManager()
