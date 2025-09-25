# =========================
# init_db.py - Database initialization script
# =========================
from sqlalchemy import create_engine
from db import DATABASE_URL
from sqlmodel import SQLModel


def init_db():
    """Initialize the database by creating all tables."""
    engine = create_engine(DATABASE_URL, echo=True)

    with engine.begin() as conn:
        # Create all tables
        SQLModel.metadata.create_all(conn)

    engine.dispose()
    print("✅ Database initialized successfully!")


if __name__ == "__main__":
    init_db()
