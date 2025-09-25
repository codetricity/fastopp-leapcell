from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from .config import Settings, get_settings


def create_database_engine(settings: Settings = Depends(get_settings)):
    """Create database engine from settings"""
    # Apply URL conversion for PostgreSQL (asyncpg -> psycopg2)
    database_url = settings.database_url
    if "postgresql+asyncpg" in database_url:
        database_url = database_url.replace("postgresql+asyncpg", "postgresql+psycopg2")
        # Add SSL mode as URL parameter (psycopg2 supports this)
        if "?" not in database_url:
            database_url += "?sslmode=require"
    
    return create_engine(
        database_url,
        echo=settings.environment == "development",
        future=True
    )


def create_session_factory(engine = Depends(create_database_engine)):
    """Create session factory from engine"""
    return sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False
    )


def get_db_session(
    session_factory: sessionmaker = Depends(create_session_factory)
) -> Session:
    """Dependency to get database session"""
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
