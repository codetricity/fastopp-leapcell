from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from .config import Settings, get_settings


def create_database_engine(settings: Settings = Depends(get_settings)):
    """Create database engine from settings"""
    return create_async_engine(
        settings.database_url,
        echo=settings.environment == "development",
        future=True
    )


def create_session_factory(engine = Depends(create_database_engine)):
    """Create session factory from engine"""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False
    )


async def get_db_session(
    session_factory: async_sessionmaker = Depends(create_session_factory)
) -> AsyncSession:
    """Dependency to get database session"""
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
