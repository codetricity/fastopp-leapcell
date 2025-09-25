# db.py - Simple database setup for base_assets
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment (defaults to SQLite for development)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

# For PostgreSQL, convert asyncpg to psycopg2 (LeapCell recommended driver)
if "postgresql+asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql+psycopg2")
    # Add SSL mode as URL parameter (psycopg2 supports this)
    if "?" not in DATABASE_URL:
        DATABASE_URL += "?sslmode=require"

# Debug: Print the database URL (without password for security)
print(f"🔍 Database URL: {DATABASE_URL}")
if "postgresql" in DATABASE_URL:
    # Mask password in URL for logging
    import re
    masked_url = re.sub(r':[^@]+@', ':***@', DATABASE_URL)
    print(f"🔍 Masked URL: {masked_url}")

# Create synchronous engine (psycopg2 for PostgreSQL)
engine = create_engine(
    DATABASE_URL,
    echo=True,  # set to False in production
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Export engine for admin setup
async_engine = engine