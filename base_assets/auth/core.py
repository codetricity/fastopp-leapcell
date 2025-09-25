"""
Authentication core functions for base_assets
Simple version without dependency injection
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Request, status
from fastapi_users.password import PasswordHelper
from sqlmodel import select
from db import AsyncSessionLocal
from models import User


def create_user_token(user: User) -> str:
    """Create a JWT token for the user"""
    # Simple token creation - in production, use proper JWT
    return f"token_{user.id}_{user.email}"


async def get_current_user_from_cookies(request: Request):
    """Get current authenticated user from cookies"""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Simple token validation - in production, use proper JWT
    if not token.startswith("token_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user ID from token (simple approach)
    try:
        parts = token.split("_")
        if len(parts) < 3:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_uuid = uuid.UUID(parts[1])
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_uuid))
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user


async def get_current_staff_or_admin_from_cookies(request: Request):
    """Get current authenticated user with staff or admin privileges"""
    user = await get_current_user_from_cookies(request)
    
    if not (user.is_staff or user.is_superuser):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff or admin privileges required",
        )
    
    return user
