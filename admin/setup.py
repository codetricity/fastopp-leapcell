# =========================
# admin/setup.py (Demo Assets - Full Features)
# =========================
import os
from sqladmin import Admin
from fastapi import FastAPI
from dependencies.database import create_database_engine
from dependencies.config import get_settings
from auth.admin import AdminAuth
from .views import UserAdmin, ProductAdmin, WebinarRegistrantsAdmin, AuditLogAdmin


def setup_admin(app: FastAPI, secret_key: str):
    """Setup and configure the admin interface for demo application (all features)"""
    # Get settings and create database engine using dependency injection
    settings = get_settings()
    engine = create_database_engine(settings)

    # Check if we're in production (HTTPS environment)
    is_production = (os.getenv("RAILWAY_ENVIRONMENT") or
                     os.getenv("PRODUCTION") or
                     os.getenv("FORCE_HTTPS") or
                     os.getenv("ENVIRONMENT") == "production")

    # Configure admin with HTTPS support for production
    if is_production:
        admin = Admin(
            app=app,
            engine=engine,
            authentication_backend=AdminAuth(secret_key=secret_key),
            base_url="/admin",
            title="FastOpp Admin",
            logo_url=None,  # Disable logo to avoid mixed content issues
            templates_dir="templates/admin",  # Use custom templates for font fixes
        )
    else:
        admin = Admin(
            app=app,
            engine=engine,
            authentication_backend=AdminAuth(secret_key=secret_key)
        )

    # Mount SQLAdmin static files to ensure fonts and assets load properly
    # This is especially important in production environments like LeapCell
    try:
        import sqladmin
        sqladmin_path = os.path.dirname(sqladmin.__file__)
        static_path = os.path.join(sqladmin_path, "statics")

        if os.path.exists(static_path):
            from fastapi.staticfiles import StaticFiles
            
            # Simple static file mount - let SQLAdmin handle its own assets
            static_files = StaticFiles(directory=static_path)
            app.mount("/admin/statics", static_files, name="admin_statics")
            print(f"✅ Mounted SQLAdmin static files from: {static_path}")
        else:
            print(f"❌ SQLAdmin static path not found: {static_path}")
    except Exception as e:
        print(f"❌ Could not mount SQLAdmin static files: {e}")

    # Register admin views (all features for demo application)
    admin.add_view(UserAdmin)
    admin.add_view(ProductAdmin)
    admin.add_view(WebinarRegistrantsAdmin)
    admin.add_view(AuditLogAdmin)
    return admin
