from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application configuration settings.

    These default values are automatically overridden by environment variables
    in production. Environment variable names are uppercase with underscores
    (e.g., DATABASE_URL, SECRET_KEY, ENVIRONMENT) and are case-insensitive.

    Example production overrides:
    - DATABASE_URL="sqlite+aiosqlite:////tmp/test.db"  # For Leapcell
    - SECRET_KEY="your-secure-production-key"
    - ENVIRONMENT="production"
    - UPLOAD_DIR="/data/uploads"
    """
    database_url: str = "sqlite+aiosqlite:///./test.db"
    secret_key: str = "dev_secret_key_change_in_production"
    environment: str = "development"
    access_token_expire_minutes: int = 30
    upload_dir: str = "static/uploads"
    openrouter_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # S3/Object Storage settings (for LeapCell Object Storage)
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    s3_bucket: Optional[str] = None
    s3_endpoint_url: Optional[str] = None
    s3_region: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Dependency to get application settings"""
    return Settings()
