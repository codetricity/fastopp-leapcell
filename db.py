# db.py - Simple database setup for base_assets
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment (defaults to SQLite for development)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

# For PostgreSQL, add SSL and timeout parameters to the URL
if "postgresql" in DATABASE_URL and "?" not in DATABASE_URL:
    # Add SSL and timeout parameters to the connection URL
    DATABASE_URL += "?sslmode=require&connect_timeout=30&command_timeout=30"

# Debug: Print the database URL (without password for security)
print(f"🔍 Database URL: {DATABASE_URL}")
if "postgresql" in DATABASE_URL:
    # Mask password in URL for logging
    import re
    masked_url = re.sub(r':[^@]+@', ':***@', DATABASE_URL)
    print(f"🔍 Masked URL: {masked_url}")

# Create async engine with minimal configuration
connect_args = {}

async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # set to False in production
    future=True,
    connect_args=connect_args,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
    pool_size=1,  # Minimal pool size
    max_overflow=0  # No overflow
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Export async_engine for admin setup
async_engine = async_engine