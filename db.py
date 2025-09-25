# db.py - Simple database setup for base_assets
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment (defaults to SQLite for development)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

# Debug: Print the database URL (without password for security)
print(f"🔍 Database URL: {DATABASE_URL}")
if "postgresql" in DATABASE_URL:
    # Mask password in URL for logging
    import re
    masked_url = re.sub(r':[^@]+@', ':***@', DATABASE_URL)
    print(f"🔍 Masked URL: {masked_url}")

# Create async engine with SSL configuration
connect_args = {}
if "postgresql" in DATABASE_URL:
    # For PostgreSQL, handle SSL mode properly with aggressive timeout settings
    connect_args = {
        "sslmode": "require",
        "server_settings": {
            "application_name": "fastopp_leapcell",
            "statement_timeout": "30000",  # 30 seconds
            "idle_in_transaction_session_timeout": "30000",  # 30 seconds
            "tcp_keepalives_idle": "600",
            "tcp_keepalives_interval": "30",
            "tcp_keepalives_count": "3"
        }
    }

async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # set to False in production
    future=True,
    connect_args={**connect_args, "command_timeout": 30},
    pool_timeout=10,  # Reduced from 30
    pool_recycle=1800,  # Reduced from 3600 (30 minutes)
    pool_pre_ping=True,
    pool_size=5,  # Smaller pool size
    max_overflow=10  # Allow some overflow
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