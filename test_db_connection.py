#!/usr/bin/env python3
"""
Simple database connection test for LeapCell PostgreSQL
"""
import asyncio
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import text

async def test_connection():
    """Test database connection with detailed output"""
    print("🔍 Testing PostgreSQL connection...")
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        print("💡 To test locally, set DATABASE_URL environment variable")
        print("💡 Or run this on LeapCell where DATABASE_URL is automatically set")
        return False
    
    # Mask password for logging
    import re
    masked_url = re.sub(r':[^@]+@', ':***@', database_url)
    print(f"🔗 Connecting to: {masked_url}")
    
    try:
        # Create engine with same settings as db.py
        connect_args = {}
        if "postgresql" in database_url:
            connect_args = {
                "server_settings": {
                    "application_name": "fastopp_connection_test",
                    "statement_timeout": "30000",
                    "idle_in_transaction_session_timeout": "30000",
                }
            }
        
        engine = create_async_engine(
            database_url,
            echo=False,
            connect_args=connect_args,
            pool_timeout=10,
            pool_recycle=1800,
            pool_pre_ping=True,
            pool_size=2,
            max_overflow=5
        )
        
        print("🔄 Testing basic connection...")
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1 as test, NOW() as current_time"))
            row = result.fetchone()
            print(f"✅ Connection successful!")
            print(f"   Test value: {row[0]}")
            print(f"   Server time: {row[1]}")
        
        print("🔄 Testing connection pool...")
        pool = engine.pool
        print(f"   Pool size: {pool.size()}")
        print(f"   Checked in: {pool.checkedin()}")
        print(f"   Checked out: {pool.checkedout()}")
        
        print("🔄 Testing schema access...")
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT current_schema()"))
            schema = result.scalar()
            print(f"   Current schema: {schema}")
        
        print("✅ All connection tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False
    
    finally:
        try:
            await engine.dispose()
        except:
            pass

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
