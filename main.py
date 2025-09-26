# =========================
# main.py
# =========================
import os
from pathlib import Path
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to prevent false positive security warnings"""
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy
        # Note: CDN usage is for educational purposes - in production, bundle these assets locally
        csp = (
            "default-src 'self'; "
            "img-src 'self' data: https:; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://unpkg.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://cdn.jsdelivr.net; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv
from admin.setup import setup_admin
from routes.chat import router as chat_router
from routes.api import router as api_router
try:
    from routes.auth import router as auth_router
except Exception:
    auth_router = None  # Optional during partial restores
from routes.pages import router as pages_router
try:
    from routes.webinar import router as webinar_router
except Exception:
    webinar_router = None  # Optional during partial restores

# Import dependency injection modules
from dependencies.database import create_database_engine, create_session_factory, get_db_session
from dependencies.config import get_settings

# Load environment variables
load_dotenv()

# Get settings using dependency injection
settings = get_settings()

# Create upload directories
UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(exist_ok=True)
PHOTOS_DIR = UPLOAD_DIR / "photos"
PHOTOS_DIR.mkdir(exist_ok=True)

# from users import fastapi_users, auth_backend  # type: ignore

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.add_middleware(SecurityHeadersMiddleware)

# Add proxy headers middleware for production deployments
@app.middleware("http")
async def proxy_headers_middleware(request: Request, call_next):
    """Middleware to handle proxy headers for production deployments"""
    # Check if we're behind a proxy (Railway, Fly, etc.)
    if request.headers.get("x-forwarded-proto") == "https":
        request.scope["scheme"] = "https"
    
    # Don't modify scope["type"] - it should remain "http" for HTTP requests
    
    response = await call_next(request)
    return response

# Setup dependencies
def setup_dependencies(app: FastAPI):
    """Setup application dependencies"""
    # Create database engine and session factory
    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)
    
    # Store in app state for dependency injection
    app.state.db_engine = engine
    app.state.session_factory = session_factory
    app.state.settings = settings
    
    print(f"✅ Dependencies setup complete - session_factory: {session_factory}")
    print(f"✅ App state after setup: {list(app.state.__dict__.keys())}")

# Setup dependencies immediately
setup_dependencies(app)

# Mount static files first (for general static assets)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount uploads directory for production
if settings.upload_dir != "static/uploads":
    print(f"🔧 Production mode: Mounting /static/uploads to {UPLOAD_DIR}")
    app.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
else:
    print(f"🔧 Development mode: Using default static/uploads")

templates = Jinja2Templates(directory="templates")
security = HTTPBasic()


# Setup admin interface
setup_admin(app, settings.secret_key)

# Include routers
app.include_router(chat_router, prefix="/api")
app.include_router(api_router, prefix="/api")
if auth_router:
    app.include_router(auth_router)
app.include_router(pages_router)
if webinar_router:
    app.include_router(webinar_router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "FastOpp Demo app is running"}


@app.get("/kaithheathcheck")
async def leapcell_health_check():
    """LeapCell health check endpoint"""
    return {"status": "healthy", "message": "FastOpp Demo app is running"}

@app.get("/robots.txt")
async def robots_txt():
    """Provide robots.txt to help with SEO and security"""
    content = """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /debug/
Disallow: /api/
"""
    return HTMLResponse(content=content, media_type="text/plain")


@app.get("/debug/current-user")
async def debug_current_user(request: Request):
    """Debug endpoint to check current user authentication"""
    token = request.cookies.get("access_token")
    if not token:
        return HTMLResponse("No access token found")
    
    try:
        # Manual authentication check without dependency injection
        from dependencies.auth import verify_token
        from dependencies.config import get_settings
        from models import User
        from sqlmodel import select
        from db import SessionLocal
        import uuid
        
        settings = get_settings()
        payload = verify_token(token, settings)
        if not payload:
            return HTMLResponse("Invalid token")
        
        user_id = payload.get("sub")
        if not user_id:
            return HTMLResponse("No user ID in token")
        
        user_uuid = uuid.UUID(user_id)
        
        with SessionLocal() as session:
            result = session.execute(select(User).where(User.id == user_uuid))
            current_user = result.scalar_one_or_none()
            
            if not current_user:
                return HTMLResponse("User not found")
            
            return HTMLResponse(f"""
            <h1>Current User Debug</h1>
            <p><strong>Email:</strong> {current_user.email}</p>
            <p><strong>ID:</strong> {current_user.id}</p>
            <p><strong>is_staff:</strong> {current_user.is_staff}</p>
            <p><strong>is_superuser:</strong> {current_user.is_superuser}</p>
            <p><strong>is_active:</strong> {current_user.is_active}</p>
            <p><strong>Token:</strong> {token[:20]}...</p>
            """)
    except Exception as e:
        return HTMLResponse(f"Error: {str(e)}")


@app.get("/change-password")
async def change_password_form(request: Request):
    """Display password change form (protected)"""
    # Debug: Check if we have an access token
    token = request.cookies.get("access_token")
    if not token:
        return HTMLResponse(
            '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">'
            'No access token found. Please log in first.</div>'
        )
    
    # Manual authentication check without dependency injection
    try:
        from dependencies.auth import verify_token
        from dependencies.config import get_settings
        from models import User
        from sqlmodel import select
        from db import SessionLocal
        import uuid
        
        settings = get_settings()
        payload = verify_token(token, settings)
        if not payload:
            return HTMLResponse(
                '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">'
                'Invalid token. Please log in again.</div>'
            )
        
        user_id = payload.get("sub")
        if not user_id:
            return HTMLResponse(
                '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">'
                'No user ID in token.</div>'
            )
        
        user_uuid = uuid.UUID(user_id)
        
        with SessionLocal() as session:
            result = session.execute(select(User).where(User.id == user_uuid))
            current_user = result.scalar_one_or_none()
            
            if not current_user:
                return HTMLResponse(
                    '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">'
                    'User not found.</div>'
                )
            
            print(f"DEBUG: Checking privileges - is_staff: {current_user.is_staff}, is_superuser: {current_user.is_superuser}")
            print(f"DEBUG: OR condition result: {current_user.is_staff or current_user.is_superuser}")
            print(f"DEBUG: NOT condition result: {not (current_user.is_staff or current_user.is_superuser)}")
            
            if not (current_user.is_staff or current_user.is_superuser):
                return HTMLResponse(
                    '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">'
                    f'Access denied. User {current_user.email} is not staff or admin. is_staff: {current_user.is_staff}, is_superuser: {current_user.is_superuser}</div>'
                )
            
            print("DEBUG: Access granted, showing form")
    except Exception as e:
        print(f"DEBUG: Authentication error: {e}")
        return HTMLResponse(
            '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">'
            f'Authentication error: {str(e)}</div>'
        )
    
    form_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Change Password - FastOpp</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 min-h-screen flex items-center justify-center">
        <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
            <h1 class="text-2xl font-bold text-gray-900 mb-6">Change User Password</h1>
            
            <form hx-post="/change-password" hx-target="#result" class="space-y-4">
                <div>
                    <label for="email" class="block text-sm font-medium text-gray-700">User Email</label>
                    <input type="email" id="email" name="email" required
                           class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                           placeholder="user@example.com">
                </div>
                
                <div>
                    <label for="new_password" class="block text-sm font-medium text-gray-700">New Password</label>
                    <input type="password" id="new_password" name="new_password" required minlength="6"
                           class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                           placeholder="Enter new password">
                </div>
                
                <div>
                    <label for="confirm_password" class="block text-sm font-medium text-gray-700">Confirm Password</label>
                    <input type="password" id="confirm_password" name="confirm_password" required minlength="6"
                           class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                           placeholder="Confirm new password">
                </div>
                
                <button type="submit" 
                        class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                    Change Password
                </button>
            </form>
            
            <div id="result" class="mt-4"></div>
            
            <div class="mt-6 text-sm text-gray-600">
                <p><strong>Security Notes:</strong></p>
                <ul class="list-disc list-inside mt-2">
                    <li>Only staff and admin users can change passwords</li>
                    <li>Passwords must be at least 6 characters long</li>
                    <li>All password changes are logged</li>
                </ul>
            </div>
        </div>
        
        <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    </body>
    </html>
    """
    
    return HTMLResponse(form_html)


@app.post("/change-password")
async def change_password_submit(request: Request):
    """Handle password change submission (protected)"""
    # Manual authentication check without dependency injection
    token = request.cookies.get("access_token")
    if not token:
        return HTMLResponse(
            '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">'
            'No access token found. Please log in first.</div>'
        )
    
    try:
        from dependencies.auth import verify_token
        from dependencies.config import get_settings
        from models import User
        from sqlmodel import select
        from db import SessionLocal
        import uuid
        
        settings = get_settings()
        payload = verify_token(token, settings)
        if not payload:
            return HTMLResponse(
                '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">'
                'Invalid token. Please log in again.</div>'
            )
        
        user_id = payload.get("sub")
        if not user_id:
            return HTMLResponse(
                '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">'
                'No user ID in token.</div>'
            )
        
        user_uuid = uuid.UUID(user_id)
        
        with SessionLocal() as session:
            result = session.execute(select(User).where(User.id == user_uuid))
            current_user = result.scalar_one_or_none()
            
            if not current_user:
                return HTMLResponse(
                    '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">'
                    'User not found.</div>'
                )
            
            if not (current_user.is_staff or current_user.is_superuser):
                return HTMLResponse(
                    '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">'
                    'Access denied. Please log in as staff or admin.</div>'
                )
    except Exception as e:
        return HTMLResponse(
            '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">'
            f'Authentication error: {str(e)}</div>'
        )
    
    try:
        form = await request.form()
        email = form.get("email", "").strip()
        new_password = form.get("new_password", "").strip()
        confirm_password = form.get("confirm_password", "").strip()
        
        # Validation
        if not email or not new_password or not confirm_password:
            return HTMLResponse(
                '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">'
                'All fields are required.</div>'
            )
        
        if new_password != confirm_password:
            return HTMLResponse(
                '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">'
                'Passwords do not match.</div>'
            )
        
        if len(new_password) < 6:
            return HTMLResponse(
                '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">'
                'Password must be at least 6 characters long.</div>'
            )
        
        # Change password using the same logic as the CLI tool
        from sqlmodel import select
        from models import User
        from fastapi_users.password import PasswordHelper
        
        with SessionLocal() as session:
            # Find the user by email
            result = session.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            
            if not user:
                return HTMLResponse(
                    '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">'
                    f'User not found: {email}</div>'
                )
            
            if not user.is_active:
                return HTMLResponse(
                    '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">'
                    f'User is inactive: {email}</div>'
                )
            
            # Hash the new password
            password_helper = PasswordHelper()
            hashed_password = password_helper.hash(new_password)
            
            # Update the user's password
            user.hashed_password = hashed_password
            session.commit()
            
            return HTMLResponse(
                '<div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">'
                f'✅ Password changed successfully for user: {email}</div>'
            )
            
    except Exception as e:
        return HTMLResponse(
            '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">'
            f'Error changing password: {str(e)}</div>'
        )


@app.post("/async/init-demo")
def init_demo_async():
    """Initialize demo data using CDN-based images (no file storage issues)"""
    try:
        import uuid
        from datetime import datetime, timezone
        from models import WebinarRegistrants
        from sqlmodel import select, delete
        
        print("🚀 Starting demo initialization with CDN images...")

        # Get the session factory from app state
        session_factory = app.state.session_factory
        
        # Sample registrants data with CDN URLs
        sample_registrants = [
            {
                "name": "Sarah Johnson",
                "email": "sarah.johnson@techcorp.com",
                "company": "TechCorp Solutions",
                "webinar_title": "AI in Business: Practical Applications",
                "webinar_date": datetime(2024, 3, 15, 14, 0, tzinfo=timezone.utc),
                "status": "confirmed",
                "notes": "Interested in AI implementation strategies",
                "photo_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face"
            },
            {
                "name": "Michael Chen",
                "email": "michael.chen@innovate.com",
                "company": "Innovate Labs",
                "webinar_title": "AI in Business: Practical Applications", 
                "webinar_date": datetime(2024, 3, 15, 14, 0, tzinfo=timezone.utc),
                "status": "confirmed",
                "notes": "Looking for AI tools for data analysis",
                "photo_url": "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=200&h=200&fit=crop&crop=face"
            },
            {
                "name": "Emily Rodriguez",
                "email": "emily.rodriguez@startup.io",
                "company": "StartupIO",
                "webinar_title": "AI in Business: Practical Applications",
                "webinar_date": datetime(2024, 3, 15, 14, 0, tzinfo=timezone.utc),
                "status": "confirmed", 
                "notes": "Want to learn about AI automation",
                "photo_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop&crop=face"
            },
            {
                "name": "David Kim",
                "email": "david.kim@enterprise.com",
                "company": "Enterprise Systems",
                "webinar_title": "AI in Business: Practical Applications",
                "webinar_date": datetime(2024, 3, 15, 14, 0, tzinfo=timezone.utc),
                "status": "confirmed",
                "notes": "Exploring AI for customer service",
                "photo_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&h=200&fit=crop&crop=face"
            }
        ]
        
        created_count = 0
        
        with session_factory() as session:
            # Clear existing registrants
            session.execute(delete(WebinarRegistrants))
            session.commit()
            
            for registrant_data in sample_registrants:
                # Create new registrant with CDN URL
                registrant = WebinarRegistrants(
                    id=uuid.uuid4(),
                    name=registrant_data['name'],
                    email=registrant_data['email'],
                    company=registrant_data['company'],
                    webinar_title=registrant_data['webinar_title'],
                    webinar_date=registrant_data['webinar_date'],
                    status=registrant_data['status'],
                    notes=registrant_data['notes'],
                    photo_url=registrant_data['photo_url']  # Direct CDN URL
                )
                
                session.add(registrant)
                created_count += 1
            
            session.commit()

        print("✅ Demo initialization complete!")
        return {
            "status": "success",
            "message": "Demo initialization completed successfully with CDN images",
            "details": {
                "registrants_created": created_count,
                "image_source": "CDN (no file storage issues)",
                "persistent": True
            }
        }
    except Exception as e:
        print(f"❌ Demo initialization failed: {e}")
        return {
            "status": "error",
            "message": f"Demo initialization failed: {str(e)}",
            "error_type": type(e).__name__
        }


@app.get("/debug/database")
async def debug_database():
    """Debug database configuration and permissions"""
    from pathlib import Path
    
    # Get current database configuration
    settings = get_settings()
    db_path = settings.database_url.replace("sqlite+aiosqlite:///", "").replace("sqlite+aiosqlite:////", "/")
    
    # Check if database file exists and is writable
    db_file = Path(db_path)
    db_exists = db_file.exists()
    db_writable = False
    db_size = 0
    
    if db_exists:
        try:
            db_size = db_file.stat().st_size
            # Try to open in append mode to test write permissions
            with open(db_file, "a"):
                db_writable = True
        except Exception:
            db_writable = False
    
    # Check directory permissions
    db_dir = db_file.parent
    dir_writable = False
    try:
        test_file = db_dir / "test_write.tmp"
        test_file.write_text("test")
        test_file.unlink()
        dir_writable = True
    except Exception:
        dir_writable = False
    
    return {
        "database_url": settings.database_url,
        "database_path": str(db_path),
        "database_exists": db_exists,
        "database_writable": db_writable,
        "database_size_bytes": db_size,
        "directory_writable": dir_writable,
        "environment": settings.environment,
        "upload_dir": settings.upload_dir,
        "suggestions": {
            "use_tmp": not db_writable and not dir_writable,
            "leapcell_recommended": "/tmp/test.db",
            "alternative_paths": [
                "/tmp/test.db",
                "/data/test.db",
                "./test.db"
            ]
        }
    }


@app.get("/debug/database-data")
def debug_database_data(session: Session = Depends(get_db_session)):
    """Debug database data - check if tables exist and have data"""
    try:
        from sqlmodel import text
        
        # Check if tables exist
        tables_result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
        tables = [row[0] for row in tables_result.fetchall()]

        # Count records in each table
        table_counts = {}
        for table in tables:
            try:
                count_result = session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = count_result.scalar()
                table_counts[table] = count
            except Exception as e:
                table_counts[table] = f"Error: {str(e)}"

        # Check users specifically
        users_data = []
        if "users" in tables:
            try:
                users_result = session.execute(text("SELECT email, is_active, is_staff FROM users LIMIT 5"))
                users_data = [dict(row) for row in users_result.fetchall()]
            except Exception as e:
                users_data = f"Error: {str(e)}"
        
        return {
            "tables_found": tables,
            "table_counts": table_counts,
            "sample_users": users_data,
            "total_tables": len(tables)
        }
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__
        }


@app.get("/debug/simple")
async def debug_simple():
    """Simple debug endpoint to test if the app is working"""
    return {
        "status": "working",
        "message": "Debug endpoint is accessible",
        "timestamp": "2024-01-01T00:00:00Z"
    }


@app.get("/debug/settings")
async def debug_settings():
    """Debug endpoint to check current settings and upload directory configuration"""
    from pathlib import Path
    
    # Check if upload directory exists
    upload_dir = Path(settings.upload_dir)
    upload_dir_exists = upload_dir.exists()
    photos_dir_exists = (upload_dir / "photos").exists()
    sample_photos_dir_exists = (upload_dir / "sample_photos").exists()
    
    # Count files in photos directory
    photo_count = 0
    if photos_dir_exists:
        try:
            photo_count = len(list((upload_dir / "photos").glob("*")))
        except Exception:
            photo_count = "error"
    
    # Count files in sample_photos directory
    sample_photo_count = 0
    if sample_photos_dir_exists:
        try:
            sample_photo_count = len(list((upload_dir / "sample_photos").glob("*")))
        except Exception:
            sample_photo_count = "error"
    
    # List some sample files
    sample_files = []
    if photos_dir_exists:
        try:
            sample_files = [f.name for f in (upload_dir / "photos").glob("*")[:5]]
        except Exception:
            sample_files = ["error_reading_files"]
    
    # List sample photos
    sample_photos_files = []
    if sample_photos_dir_exists:
        try:
            sample_photos_files = [f.name for f in (upload_dir / "sample_photos").glob("*")[:5]]
        except Exception:
            sample_photos_files = ["error_reading_sample_photos"]
    
    return {
        "upload_dir": settings.upload_dir,
        "upload_dir_exists": upload_dir_exists,
        "photos_dir_exists": photos_dir_exists,
        "sample_photos_dir_exists": sample_photos_dir_exists,
        "photo_count": photo_count,
        "sample_photo_count": sample_photo_count,
        "sample_files": sample_files,
        "sample_photos_files": sample_photos_files,
        "environment": settings.environment,
        "static_mounts": {
            "general_static": "/static",
            "uploads_mounted_separately": settings.upload_dir != "static/uploads"
        },
        "expected_photo_urls": "/static/uploads/photos/",
        "actual_photo_path": str(upload_dir / "photos") if upload_dir_exists else "not_found",
        "sample_photos_path": str(upload_dir / "sample_photos") if upload_dir_exists else "not_found",
        "test_urls": [
            f"/static/uploads/photos/{f}" for f in sample_files[:3]
        ]
    }


@app.get("/debug/list-files")
async def debug_list_files():
    """List all files in the upload directory"""
    from pathlib import Path
    
    upload_dir = Path(settings.upload_dir)
    files_info = {}
    
    # Check photos directory
    photos_dir = upload_dir / "photos"
    if photos_dir.exists():
        try:
            photos_files = list(photos_dir.glob("*"))
            files_info["photos"] = {
                "exists": True,
                "count": len(photos_files),
                "files": [f.name for f in photos_files[:10]]  # First 10 files
            }
        except Exception as e:
            files_info["photos"] = {"exists": True, "error": str(e)}
    else:
        files_info["photos"] = {"exists": False}
    
    # Check sample_photos directory
    sample_photos_dir = upload_dir / "sample_photos"
    if sample_photos_dir.exists():
        try:
            sample_files = list(sample_photos_dir.glob("*"))
            files_info["sample_photos"] = {
                "exists": True,
                "count": len(sample_files),
                "files": [f.name for f in sample_files[:10]]
            }
        except Exception as e:
            files_info["sample_photos"] = {"exists": True, "error": str(e)}
    else:
        files_info["sample_photos"] = {"exists": False}
    
    return {
        "upload_dir": str(upload_dir),
        "files_info": files_info
    }


@app.get("/debug/test-image/{filename}")
async def debug_test_image(filename: str):
    """Test if a specific image file can be served"""
    from pathlib import Path
    from fastapi.responses import FileResponse
    
    upload_dir = Path(settings.upload_dir)
    photo_path = upload_dir / "photos" / filename
    
    if photo_path.exists():
        return FileResponse(photo_path)
    else:
        return {
            "error": "File not found",
            "expected_path": str(photo_path),
            "upload_dir": str(upload_dir),
            "filename": filename
        }


# Removed conflicting custom photo serving endpoint
# Photos should be served via static file mounting


@app.get("/debug/connection")
def debug_connection():
    """Test database connection with detailed diagnostics"""
    try:
        from db import engine
        from sqlmodel import text
        
        # Test basic connection
        with engine.begin() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            
        # Test connection pool status
        pool = engine.pool
        pool_status = {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "pool_type": type(pool).__name__
        }
        
        return {
            "status": "success",
            "connection_test": test_value,
            "pool_status": pool_status,
            "database_url": str(engine.url)[:50] + "...",
            "message": "Database connection successful"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__,
            "database_url": str(engine.url)[:50] + "..." if 'engine' in locals() else "not_available",
            "message": "Database connection failed"
        }


@app.post("/api/backup-files")
async def backup_files():
    """Backup uploaded files to LeapCell Object Storage"""
    try:
        import boto3
        from pathlib import Path
        
        # Check if S3 credentials are configured
        s3_access_key = os.getenv("S3_ACCESS_KEY")
        s3_secret_key = os.getenv("S3_SECRET_KEY")
        s3_bucket = os.getenv("S3_BUCKET")
        
        if not s3_access_key or not s3_secret_key:
            return {
                "status": "error", 
                "message": "S3 credentials not configured. Set S3_ACCESS_KEY and S3_SECRET_KEY environment variables."
            }
        
        if not s3_bucket:
            return {
                "status": "error",
                "message": "S3 bucket not configured. Set S3_BUCKET environment variable."
            }
        
        # Get upload directory
        settings = get_settings()
        upload_dir = Path(settings.upload_dir)
        
        if not upload_dir.exists():
            return {"status": "error", "message": "Upload directory does not exist"}
        
        # Initialize S3 client
        s3 = boto3.client(
            "s3",
            region_name=os.getenv("S3_REGION", "us-east-1"),
            endpoint_url=os.getenv("S3_ENDPOINT_URL", "https://objstorage.leapcell.io"),
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key
        )
        
        files_backed_up = 0
        
        # Backup all files in upload directory
        for file_path in upload_dir.rglob("*"):
            if file_path.is_file():
                # Create S3 key (relative path from upload_dir)
                relative_path = file_path.relative_to(upload_dir)
                s3_key = f"uploads/{relative_path}"
                
                # Upload file to Object Storage
                with open(file_path, "rb") as f:
                    s3.put_object(
                        Bucket=s3_bucket,
                        Key=str(s3_key),
                        Body=f
                    )
                files_backed_up += 1
        
        return {
            "status": "success",
            "message": f"Backed up {files_backed_up} files to Object Storage",
            "bucket": s3_bucket,
            "files_count": files_backed_up
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Backup failed: {str(e)}",
            "error_type": type(e).__name__
        }


@app.post("/api/create-registrants-with-cdn")
async def create_registrants_with_cdn():
    """Create registrants with CDN URLs directly - no file copying needed"""
    try:
        import uuid
        from datetime import datetime, timezone
        from models import WebinarRegistrants
        from sqlmodel import select, delete
        
        # Get the session factory from app state
        session_factory = app.state.session_factory
        
        # Sample registrants data with CDN URLs
        sample_registrants = [
            {
                "name": "Sarah Johnson",
                "email": "sarah.johnson@techcorp.com",
                "company": "TechCorp Solutions",
                "webinar_title": "AI in Business: Practical Applications",
                "webinar_date": datetime(2024, 3, 15, 14, 0, tzinfo=timezone.utc),
                "status": "confirmed",
                "notes": "Interested in AI implementation strategies",
                "photo_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face"
            },
            {
                "name": "Michael Chen",
                "email": "michael.chen@innovate.com",
                "company": "Innovate Labs",
                "webinar_title": "AI in Business: Practical Applications", 
                "webinar_date": datetime(2024, 3, 15, 14, 0, tzinfo=timezone.utc),
                "status": "confirmed",
                "notes": "Looking for AI tools for data analysis",
                "photo_url": "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=200&h=200&fit=crop&crop=face"
            },
            {
                "name": "Emily Rodriguez",
                "email": "emily.rodriguez@startup.io",
                "company": "StartupIO",
                "webinar_title": "AI in Business: Practical Applications",
                "webinar_date": datetime(2024, 3, 15, 14, 0, tzinfo=timezone.utc),
                "status": "confirmed", 
                "notes": "Want to learn about AI automation",
                "photo_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop&crop=face"
            },
            {
                "name": "David Kim",
                "email": "david.kim@enterprise.com",
                "company": "Enterprise Systems",
                "webinar_title": "AI in Business: Practical Applications",
                "webinar_date": datetime(2024, 3, 15, 14, 0, tzinfo=timezone.utc),
                "status": "confirmed",
                "notes": "Exploring AI for customer service",
                "photo_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&h=200&fit=crop&crop=face"
            }
        ]
        
        created_count = 0
        
        with session_factory() as session:
            # Clear existing registrants
            session.execute(delete(WebinarRegistrants))
            session.commit()
            
            for registrant_data in sample_registrants:
                # Create new registrant with CDN URL
                registrant = WebinarRegistrants(
                    id=uuid.uuid4(),
                    name=registrant_data['name'],
                    email=registrant_data['email'],
                    company=registrant_data['company'],
                    webinar_title=registrant_data['webinar_title'],
                    webinar_date=registrant_data['webinar_date'],
                    status=registrant_data['status'],
                    notes=registrant_data['notes'],
                    photo_url=registrant_data['photo_url']  # Direct CDN URL
                )
                
                session.add(registrant)
                created_count += 1
            
            session.commit()
        
        return {
            "status": "success",
            "message": f"Created {created_count} registrants with CDN photo URLs",
            "created_count": created_count
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create registrants: {str(e)}",
            "error_type": type(e).__name__
        }


@app.post("/api/download-from-cdn")
async def download_from_cdn():
    """Download sample photos directly from CDN instead of S3 API"""
    try:
        import requests
        from pathlib import Path
        
        # Get upload directory
        settings = get_settings()
        upload_dir = Path(settings.upload_dir)
        sample_photos_dir = upload_dir / "sample_photos"
        sample_photos_dir.mkdir(parents=True, exist_ok=True)
        
        # Generic CDN URLs for sample photos (works for any LeapCell account)
        cdn_urls = [
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face",
            "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=200&h=200&fit=crop&crop=face", 
            "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop&crop=face",
            "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&h=200&fit=crop&crop=face"
        ]
        
        downloaded_count = 0
        errors = []
        
        for i, url in enumerate(cdn_urls, 1):
            try:
                # Download from CDN
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                # Save to local directory
                filename = f"sample_photo_{i}.jpg"
                local_path = sample_photos_dir / filename
                
                with open(local_path, "wb") as f:
                    f.write(response.content)
                
                downloaded_count += 1
                print(f"Downloaded {filename} from CDN")
                
            except Exception as e:
                error_msg = f"Failed to download sample_photo_{i}.jpg: {e}"
                print(error_msg)
                errors.append(error_msg)
        
        return {
            "status": "success",
            "message": f"Downloaded {downloaded_count} sample photos from CDN",
            "downloaded_count": downloaded_count,
            "errors": errors,
            "local_path": str(sample_photos_dir)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to download from CDN: {str(e)}",
            "error_type": type(e).__name__
        }


@app.get("/api/debug-bucket-mismatch")
async def debug_bucket_mismatch():
    """Debug if there's a bucket mismatch between upload and download"""
    try:
        import boto3
        
        # Get settings
        settings = get_settings()
        
        # Initialize S3 client
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            endpoint_url=settings.s3_endpoint_url,
            region_name=settings.s3_region
        )
        
        # Check what bucket we're using
        bucket_name = settings.s3_bucket
        
        # Try to list objects in this bucket
        try:
            response = s3.list_objects_v2(Bucket=bucket_name)
            objects = response.get('Contents', [])
            
            return {
                "status": "success",
                "bucket_name": bucket_name,
                "object_count": len(objects),
                "objects": [obj['Key'] for obj in objects],
                "message": "Bucket access successful"
            }
        except Exception as e:
            return {
                "status": "error",
                "bucket_name": bucket_name,
                "error": str(e),
                "message": "Bucket access failed"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to debug bucket: {str(e)}",
            "error_type": type(e).__name__
        }


@app.get("/api/debug-exact-s3-keys")
async def debug_exact_s3_keys():
    """Debug the exact S3 keys and try to download them"""
    try:
        import boto3
        from pathlib import Path
        
        # Get upload directory
        settings = get_settings()
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize S3 client
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            endpoint_url=settings.s3_endpoint_url,
            region_name=settings.s3_region
        )
        
        # List all objects
        response = s3.list_objects_v2(Bucket=settings.s3_bucket)
        objects = response.get('Contents', [])
        
        results = []
        for obj in objects:
            s3_key = obj["Key"]
            try:
                # Try to download this specific object
                file_response = s3.get_object(Bucket=settings.s3_bucket, Key=s3_key)
                results.append({
                    "key": s3_key,
                    "size": obj["Size"],
                    "download_status": "success",
                    "content_length": file_response['ContentLength']
                })
            except Exception as e:
                results.append({
                    "key": s3_key,
                    "size": obj["Size"],
                    "download_status": "failed",
                    "error": str(e)
                })
        
        return {
            "status": "success",
            "bucket": settings.s3_bucket,
            "object_count": len(objects),
            "results": results
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to debug S3 keys: {str(e)}",
            "error_type": type(e).__name__
        }


@app.get("/api/test-restore-single")
async def test_restore_single():
    """Test restoring a single file to debug the issue"""
    try:
        import boto3
        from pathlib import Path
        
        # Get upload directory
        settings = get_settings()
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize S3 client
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            endpoint_url=settings.s3_endpoint_url,
            region_name=settings.s3_region
        )
        
        # Try to download the first sample photo
        s3_key = "sample_photos%2Fsample_photo_1.jpg"
        
        try:
            # Download file from Object Storage
            file_response = s3.get_object(Bucket=settings.s3_bucket, Key=s3_key)
            
            # Create local file path
            relative_path = s3_key.replace("sample_photos%2F", "sample_photos/")
            local_file_path = upload_dir / relative_path
            local_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save file locally
            with open(local_file_path, "wb") as f:
                f.write(file_response["Body"].read())
            
            return {
                "status": "success",
                "message": f"Successfully downloaded {s3_key}",
                "local_path": str(local_file_path),
                "file_size": local_file_path.stat().st_size
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to download {s3_key}: {str(e)}",
                "error_type": type(e).__name__
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to test restore: {str(e)}",
            "error_type": type(e).__name__
        }


@app.get("/api/debug-s3-download/{key}")
async def debug_s3_download(key: str):
    """Debug downloading a specific S3 object"""
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            endpoint_url=settings.s3_endpoint_url,
            region_name=settings.s3_region
        )
        
        try:
            # Try to get the object
            response = s3_client.get_object(Bucket=settings.s3_bucket, Key=key)
            return {
                "status": "success",
                "key": key,
                "size": response['ContentLength'],
                "content_type": response.get('ContentType', 'unknown')
            }
        except ClientError as e:
            return {
                "status": "error",
                "key": key,
                "error": str(e),
                "error_code": e.response.get('Error', {}).get('Code', 'Unknown')
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to debug S3 download: {str(e)}",
            "error_type": type(e).__name__
        }


@app.get("/api/debug-s3-objects")
async def debug_s3_objects():
    """Debug what objects are in the S3 bucket"""
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            endpoint_url=settings.s3_endpoint_url,
            region_name=settings.s3_region
        )
        
        # List all objects in the bucket
        try:
            response = s3_client.list_objects_v2(Bucket=settings.s3_bucket)
            objects = response.get('Contents', [])
            
            return {
                "status": "success",
                "bucket": settings.s3_bucket,
                "object_count": len(objects),
                "objects": [
                    {
                        "key": obj['Key'],
                        "size": obj['Size'],
                        "last_modified": obj['LastModified'].isoformat()
                    }
                    for obj in objects
                ]
            }
        except ClientError as e:
            return {
                "status": "error",
                "message": f"Failed to list objects: {str(e)}",
                "error_code": e.response.get('Error', {}).get('Code', 'Unknown')
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to debug S3 objects: {str(e)}",
            "error_type": type(e).__name__
        }


@app.get("/api/debug-s3-connection")
async def debug_s3_connection():
    """Debug S3 connection and credentials"""
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        # Check S3 credentials
        if not all([settings.s3_access_key, settings.s3_secret_key, settings.s3_bucket]):
            return {
                "status": "error",
                "message": "S3 credentials not configured",
                "s3_access_key": bool(settings.s3_access_key),
                "s3_secret_key": bool(settings.s3_secret_key),
                "s3_bucket": bool(settings.s3_bucket)
            }

        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            endpoint_url=settings.s3_endpoint_url,
            region_name=settings.s3_region
        )
        
        # Test S3 connection
        try:
            response = s3_client.list_objects_v2(Bucket=settings.s3_bucket, MaxKeys=1)
            return {
                "status": "success",
                "message": "S3 connection successful",
                "bucket": settings.s3_bucket,
                "endpoint": settings.s3_endpoint_url,
                "region": settings.s3_region,
                "object_count": response.get('KeyCount', 0)
            }
        except ClientError as e:
            return {
                "status": "error",
                "message": f"S3 connection failed: {str(e)}",
                "error_code": e.response.get('Error', {}).get('Code', 'Unknown')
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to test S3 connection: {str(e)}",
            "error_type": type(e).__name__
        }


@app.post("/api/download-sample-photos-to-s3")
async def download_sample_photos_to_s3():
    """Download sample photos directly to Object Storage"""
    try:
        import requests
        from pathlib import Path
        import boto3
        from botocore.exceptions import ClientError

        # Check S3 credentials
        if not all([settings.s3_access_key, settings.s3_secret_key, settings.s3_bucket]):
            return {
                "status": "error",
                "message": "S3 credentials not configured. Set S3_ACCESS_KEY, S3_SECRET_KEY, and S3_BUCKET environment variables."
            }

        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            endpoint_url=settings.s3_endpoint_url,
            region_name=settings.s3_region
        )

        # Sample photos from Unsplash
        sample_photos = [
            {
                "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face",
                "filename": "sample_photo_1.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=400&h=400&fit=crop&crop=face",
                "filename": "sample_photo_2.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop&crop=face",
                "filename": "sample_photo_3.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop&crop=face",
                "filename": "sample_photo_4.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&crop=face",
                "filename": "sample_photo_5.jpg"
            }
        ]

        uploaded_count = 0
        errors = []

        for photo in sample_photos:
            try:
                # Download the image
                print(f"Downloading {photo['url']}")
                response = requests.get(photo["url"], timeout=10)
                response.raise_for_status()
                print(f"Downloaded {photo['filename']}, size: {len(response.content)} bytes")
                
                # Upload directly to S3
                s3_key = f"sample_photos/{photo['filename']}"
                s3_client.put_object(
                    Bucket=settings.s3_bucket,
                    Key=s3_key,
                    Body=response.content,
                    ContentType='image/jpeg'
                )
                
                uploaded_count += 1
                print(f"Uploaded {photo['filename']} to S3")

            except Exception as e:
                error_msg = f"Failed to upload {photo['filename']}: {e}"
                print(error_msg)
                errors.append(error_msg)

        return {
            "status": "success",
            "message": f"Uploaded {uploaded_count} sample photos to Object Storage",
            "uploaded_count": uploaded_count,
            "errors": errors
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to upload sample photos to S3: {str(e)}",
            "error_type": type(e).__name__
        }


@app.post("/api/download-sample-photos")
async def download_sample_photos():
    """Download sample photos from Unsplash"""
    try:
        import requests
        from pathlib import Path
        
        # Sample photos from Unsplash
        sample_photos = [
            {
                "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face",
                "filename": "john_smith.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&h=200&fit=crop&crop=face",
                "filename": "sarah_johnson.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop&crop=face",
                "filename": "michael_chen.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&h=200&fit=crop&crop=face",
                "filename": "emily_davis.jpg"
            },
            {
                "url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=200&h=200&fit=crop&crop=face",
                "filename": "david_wilson.jpg"
            }
        ]
        
        # Setup directories
        upload_dir = Path(settings.upload_dir)
        sample_photos_dir = upload_dir / "sample_photos"
        sample_photos_dir.mkdir(parents=True, exist_ok=True)
        
        downloaded_count = 0
        
        for photo in sample_photos:
            filename = sample_photos_dir / photo["filename"]
            
            if filename.exists():
                continue
                
            try:
                response = requests.get(photo["url"], timeout=10)
                response.raise_for_status()
                
                with open(filename, "wb") as f:
                    f.write(response.content)
                
                downloaded_count += 1
                
            except Exception as e:
                print(f"Failed to download {photo['filename']}: {e}")
        
        return {
            "status": "success",
            "message": f"Downloaded {downloaded_count} sample photos",
            "downloaded_count": downloaded_count,
            "sample_photos_dir": str(sample_photos_dir)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to download sample photos: {str(e)}",
            "error_type": type(e).__name__
        }


@app.post("/api/test-write-tmp")
async def test_write_tmp():
    """Test if we can write to /tmp/ and if files persist"""
    from pathlib import Path
    import time
    
    # Test writing to /tmp/
    test_file = Path("/tmp/test_write.txt")
    test_content = f"Test write at {time.time()}\n"
    
    try:
        # Write test file
        test_file.write_text(test_content)
        
        # Check if it exists immediately
        exists_immediately = test_file.exists()
        
        # Try to read it back
        if exists_immediately:
            content = test_file.read_text()
        else:
            content = "File not found immediately after write"
        
        return {
            "status": "success",
            "test_file": str(test_file),
            "exists_immediately": exists_immediately,
            "content": content,
            "file_size": test_file.stat().st_size if exists_immediately else 0
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }


@app.get("/api/check-test-file")
async def check_test_file():
    """Check if our test file still exists"""
    from pathlib import Path
    
    test_file = Path("/tmp/test_write.txt")
    
    try:
        if test_file.exists():
            content = test_file.read_text()
            stat = test_file.stat()
            return {
                "status": "success",
                "exists": True,
                "content": content,
                "file_size": stat.st_size,
                "modified_time": stat.st_mtime
            }
        else:
            return {
                "status": "success",
                "exists": False,
                "message": "Test file not found"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }


@app.get("/api/debug-upload-dir")
async def debug_upload_dir():
    """Debug what's actually in the upload directory"""
    from pathlib import Path
    
    upload_dir = Path(settings.upload_dir)
    result = {
        "upload_dir": str(upload_dir),
        "upload_dir_exists": upload_dir.exists(),
        "directories": {},
        "all_files": []
    }
    
    if upload_dir.exists():
        # List all directories
        for item in upload_dir.iterdir():
            if item.is_dir():
                try:
                    files = list(item.glob("*"))
                    result["directories"][item.name] = {
                        "exists": True,
                        "count": len(files),
                        "files": [f.name for f in files[:10]]
                    }
                except Exception as e:
                    result["directories"][item.name] = {
                        "exists": True,
                        "error": str(e)
                    }
        
        # List all files in root
        try:
            all_files = list(upload_dir.glob("*"))
            result["all_files"] = [f.name for f in all_files if f.is_file()]
        except Exception as e:
            result["all_files"] = f"Error: {e}"
    
    return result


@app.post("/api/copy-sample-photos")
async def copy_sample_photos():
    """Copy sample photos from sample_photos to photos directory"""
    try:
        import shutil
        import uuid
        from pathlib import Path
        
        upload_dir = Path(settings.upload_dir)
        sample_photos_dir = upload_dir / "sample_photos"
        photos_dir = upload_dir / "photos"
        photos_dir.mkdir(parents=True, exist_ok=True)
        
        copied_count = 0
        
        if sample_photos_dir.exists():
            for sample_file in sample_photos_dir.glob("*.jpg"):
                # Generate unique filename
                unique_filename = f"{uuid.uuid4()}_{sample_file.name}"
                dest_path = photos_dir / unique_filename
                
                # Copy the file
                shutil.copy2(sample_file, dest_path)
                copied_count += 1
                
                print(f"Copied {sample_file.name} to {unique_filename}")
        
        return {
            "status": "success",
            "message": f"Copied {copied_count} photos from sample_photos to photos",
            "copied_count": copied_count
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to copy photos: {str(e)}",
            "error_type": type(e).__name__
        }


@app.post("/api/clear-and-create-registrants")
async def clear_and_create_registrants():
    """Clear existing registrants and create fresh ones with photos"""
    try:
        import uuid
        import shutil
        from pathlib import Path
        from datetime import datetime, timezone
        from models import WebinarRegistrants
        from sqlmodel import select, delete
        
        # Get the session factory from app state
        session_factory = app.state.session_factory
        
        # Sample registrants data
        sample_registrants = [
            {
                "name": "John Smith",
                "email": "john.smith@example.com",
                "company": "Tech Corp",
                "webinar_title": "Advanced FastAPI Development",
                "webinar_date": datetime(2024, 2, 15, 14, 0, tzinfo=timezone.utc),
                "status": "registered",
                "photo_filename": "john_smith.jpg",
                "notes": ("Interested in implementing authentication systems. "
                          "Has experience with Django and wants to migrate to FastAPI.")
            },
            {
                "name": "Sarah Johnson",
                "email": "sarah.johnson@startup.io",
                "company": "Startup Inc",
                "webinar_title": "Building Scalable APIs",
                "webinar_date": datetime(2024, 2, 20, 10, 0, tzinfo=timezone.utc),
                "status": "attended",
                "photo_filename": "sarah_johnson.jpg",
                "notes": ("Startup founder looking to scale their API from 100 to 10,000 users. "
                          "Currently using Express.js and considering FastAPI for better performance.")
            },
            {
                "name": "Michael Chen",
                "email": "michael.chen@enterprise.com",
                "company": "Enterprise Solutions",
                "webinar_title": "Database Design Best Practices",
                "webinar_date": datetime(2024, 2, 25, 16, 0, tzinfo=timezone.utc),
                "status": "registered",
                "photo_filename": "michael_chen.jpg",
                "notes": ("Senior architect evaluating database solutions for a new microservices project. "
                          "Interested in PostgreSQL and Redis integration patterns.")
            },
            {
                "name": "Emily Davis",
                "email": "emily.davis@freelance.dev",
                "company": "Freelance Developer",
                "webinar_title": "Modern Web Development",
                "webinar_date": datetime(2024, 3, 1, 13, 0, tzinfo=timezone.utc),
                "status": "registered",
                "photo_filename": "emily_davis.jpg",
                "notes": ("Full-stack developer specializing in React and Node.js. "
                          "Looking to expand skillset to include Python and FastAPI for backend development.")
            },
            {
                "name": "David Wilson",
                "email": "david.wilson@consulting.co",
                "company": "Tech Consulting",
                "webinar_title": "API Security Fundamentals",
                "webinar_date": datetime(2024, 3, 5, 15, 0, tzinfo=timezone.utc),
                "status": "registered",
                "photo_filename": "david_wilson.jpg",
                "notes": ("Security consultant working with financial services clients. "
                          "Needs to implement OAuth2 and JWT token validation for compliance requirements.")
            }
        ]
        
        # Setup photo directories
        upload_dir = Path(settings.upload_dir)
        sample_photos_dir = upload_dir / "sample_photos"
        photos_dir = upload_dir / "photos"
        photos_dir.mkdir(parents=True, exist_ok=True)
        
        created_count = 0
        
        with session_factory() as session:
            # Clear existing registrants
            session.execute(delete(WebinarRegistrants))
            session.commit()
            
            for registrant_data in sample_registrants:
                # Copy sample photo if it exists
                photo_url = None
                photo_filename = registrant_data.pop('photo_filename')
                sample_photo_path = sample_photos_dir / photo_filename
                
                if sample_photo_path.exists():
                    # Generate unique filename for the photo
                    unique_filename = f"{uuid.uuid4()}_{photo_filename}"
                    photo_dest_path = photos_dir / unique_filename
                    
                    # Copy the sample photo
                    shutil.copy2(sample_photo_path, photo_dest_path)
                    photo_url = f"/static/uploads/photos/{unique_filename}"
                
                # Create new registrant
                registrant = WebinarRegistrants(
                    id=uuid.uuid4(),
                    name=registrant_data['name'],
                    email=registrant_data['email'],
                    company=registrant_data['company'],
                    webinar_title=registrant_data['webinar_title'],
                    webinar_date=registrant_data['webinar_date'],
                    status=registrant_data['status'],
                    notes=registrant_data['notes'],
                    photo_url=photo_url
                )
                
                session.add(registrant)
                created_count += 1
            
            session.commit()
        
        return {
            "status": "success",
            "message": f"Cleared existing registrants and created {created_count} new ones with photos",
            "created_count": created_count
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to clear and create registrants: {str(e)}",
            "error_type": type(e).__name__
        }


@app.post("/api/create-sample-registrants")
async def create_sample_registrants():
    """Create sample webinar registrants with photos"""
    try:
        import asyncio
        import uuid
        import shutil
        from pathlib import Path
        from datetime import datetime, timezone
        from models import WebinarRegistrants
        from sqlmodel import select
        
        # Get the session factory from app state
        session_factory = app.state.session_factory
        
        # Sample registrants data
        sample_registrants = [
            {
                "name": "John Smith",
                "email": "john.smith@example.com",
                "company": "Tech Corp",
                "webinar_title": "Advanced FastAPI Development",
                "webinar_date": datetime(2024, 2, 15, 14, 0, tzinfo=timezone.utc),
                "status": "registered",
                "photo_filename": "john_smith.jpg",
                "notes": ("Interested in implementing authentication systems. "
                          "Has experience with Django and wants to migrate to FastAPI.")
            },
            {
                "name": "Sarah Johnson",
                "email": "sarah.johnson@startup.io",
                "company": "Startup Inc",
                "webinar_title": "Building Scalable APIs",
                "webinar_date": datetime(2024, 2, 20, 10, 0, tzinfo=timezone.utc),
                "status": "attended",
                "photo_filename": "sarah_johnson.jpg",
                "notes": ("Startup founder looking to scale their API from 100 to 10,000 users. "
                          "Currently using Express.js and considering FastAPI for better performance.")
            },
            {
                "name": "Michael Chen",
                "email": "michael.chen@enterprise.com",
                "company": "Enterprise Solutions",
                "webinar_title": "Database Design Best Practices",
                "webinar_date": datetime(2024, 2, 25, 16, 0, tzinfo=timezone.utc),
                "status": "registered",
                "photo_filename": "michael_chen.jpg",
                "notes": ("Senior architect evaluating database solutions for a new microservices project. "
                          "Interested in PostgreSQL and Redis integration patterns.")
            },
            {
                "name": "Emily Davis",
                "email": "emily.davis@freelance.dev",
                "company": "Freelance Developer",
                "webinar_title": "Modern Web Development",
                "webinar_date": datetime(2024, 3, 1, 13, 0, tzinfo=timezone.utc),
                "status": "registered",
                "photo_filename": "emily_davis.jpg",
                "notes": ("Full-stack developer specializing in React and Node.js. "
                          "Looking to expand skillset to include Python and FastAPI for backend development.")
            },
            {
                "name": "David Wilson",
                "email": "david.wilson@consulting.co",
                "company": "Tech Consulting",
                "webinar_title": "API Security Fundamentals",
                "webinar_date": datetime(2024, 3, 5, 15, 0, tzinfo=timezone.utc),
                "status": "registered",
                "photo_filename": "david_wilson.jpg",
                "notes": ("Security consultant working with financial services clients. "
                          "Needs to implement OAuth2 and JWT token validation for compliance requirements.")
            }
        ]
        
        # Setup photo directories
        upload_dir = Path(settings.upload_dir)
        sample_photos_dir = upload_dir / "sample_photos"
        photos_dir = upload_dir / "photos"
        photos_dir.mkdir(parents=True, exist_ok=True)
        
        created_count = 0
        
        with session_factory() as session:
            for registrant_data in sample_registrants:
                # Check if registrant already exists
                existing = session.execute(
                    select(WebinarRegistrants).where(WebinarRegistrants.email == registrant_data['email'])
                )
                if existing.scalar_one_or_none():
                    continue
                
                # Copy sample photo if it exists
                photo_url = None
                photo_filename = registrant_data.pop('photo_filename')
                sample_photo_path = sample_photos_dir / photo_filename
                
                if sample_photo_path.exists():
                    # Generate unique filename for the photo
                    unique_filename = f"{uuid.uuid4()}_{photo_filename}"
                    photo_dest_path = photos_dir / unique_filename
                    
                    # Copy the sample photo
                    shutil.copy2(sample_photo_path, photo_dest_path)
                    photo_url = f"/static/uploads/photos/{unique_filename}"
                
                # Create new registrant
                registrant = WebinarRegistrants(
                    id=uuid.uuid4(),
                    name=registrant_data['name'],
                    email=registrant_data['email'],
                    company=registrant_data['company'],
                    webinar_title=registrant_data['webinar_title'],
                    webinar_date=registrant_data['webinar_date'],
                    status=registrant_data['status'],
                    notes=registrant_data['notes'],
                    photo_url=photo_url
                )
                
                session.add(registrant)
                created_count += 1
            
            session.commit()
        
        return {
            "status": "success",
            "message": f"Created {created_count} sample registrants with photos",
            "created_count": created_count
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create sample registrants: {str(e)}",
            "error_type": type(e).__name__
        }


@app.post("/api/restore-files")
async def restore_files():
    """Restore uploaded files from LeapCell Object Storage"""
    try:
        import boto3
        from pathlib import Path
        
        # Check if S3 credentials are configured
        s3_access_key = os.getenv("S3_ACCESS_KEY")
        s3_secret_key = os.getenv("S3_SECRET_KEY")
        s3_bucket = os.getenv("S3_BUCKET")
        
        if not s3_access_key or not s3_secret_key:
            return {
                "status": "error", 
                "message": "S3 credentials not configured. Set S3_ACCESS_KEY and S3_SECRET_KEY environment variables."
            }
        
        if not s3_bucket:
            return {
                "status": "error",
                "message": "S3 bucket not configured. Set S3_BUCKET environment variable."
            }
        
        # Get upload directory
        settings = get_settings()
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize S3 client
        s3 = boto3.client(
            "s3",
            region_name=os.getenv("S3_REGION", "us-east-1"),
            endpoint_url=os.getenv("S3_ENDPOINT_URL", "https://objstorage.leapcell.io"),
            aws_access_key_id=s3_access_key,
            aws_secret_access_key=s3_secret_key
        )
        
        files_restored = 0
        
        # List objects in Object Storage
        response = s3.list_objects_v2(
            Bucket=s3_bucket
        )
        
        for obj in response.get("Contents", []):
            s3_key = obj["Key"]
            if s3_key.endswith("/"):
                continue  # Skip directories
            
            # Only process sample_photos files
            if not s3_key.startswith("sample_photos"):
                continue
            
            # Download file from Object Storage
            file_response = s3.get_object(Bucket=s3_bucket, Key=s3_key)
            
            # Create local file path
            # Convert URL-encoded key to normal path
            relative_path = s3_key.replace("sample_photos%2F", "sample_photos/")
            local_file_path = upload_dir / relative_path
            local_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save file locally
            with open(local_file_path, "wb") as f:
                f.write(file_response["Body"].read())
            
            files_restored += 1
        
        return {
            "status": "success",
            "message": f"Restored {files_restored} files from Object Storage",
            "files_count": files_restored
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Restore failed: {str(e)}",
            "error_type": type(e).__name__
        }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions and redirect to login if authentication fails"""
    if exc.status_code in [401, 403]:
        return RedirectResponse(url="/login", status_code=302)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
