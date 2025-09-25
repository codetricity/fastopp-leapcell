# =========================
# main.py
# =========================
import os
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic
from starlette.middleware.sessions import SessionMiddleware
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
from dependencies.database import create_database_engine, create_session_factory
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

# Mount uploads directory based on environment (MUST come before /static mount)
if settings.upload_dir != "static/uploads":
    # In production environments, mount the uploads directory separately
    app.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Mount static files (MUST come after /static/uploads to avoid conflicts)
app.mount("/static", StaticFiles(directory="static"), name="static")

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


@app.post("/async/init-demo")
async def init_demo_async():
    """Initialize demo data using Leapcell's async task system"""
    try:
        print("🚀 Starting demo initialization...")
        
        # Import and run the initialization
        from oppdemo import run_full_init
        await run_full_init()
        
        print("✅ Demo initialization complete!")
        return {
            "status": "success", 
            "message": "Demo initialization completed successfully",
            "details": {
                "database_initialized": True,
                "superuser_created": "admin@example.com / admin123",
                "test_users_added": True,
                "sample_data_added": True
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
    import os
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
            with open(db_file, "a") as f:
                db_writable = True
        except Exception as e:
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
async def debug_database_data():
    """Debug database data - check if tables exist and have data"""
    try:
        from dependencies.database import get_db_session
        from sqlmodel import text
        
        async with get_db_session() as session:
            # Check if tables exist
            tables_result = await session.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            tables = [row[0] for row in tables_result.fetchall()]
            
            # Count records in each table
            table_counts = {}
            for table in tables:
                try:
                    count_result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = count_result.scalar()
                    table_counts[table] = count
                except Exception as e:
                    table_counts[table] = f"Error: {str(e)}"
            
            # Check users specifically
            users_data = []
            if "users" in tables:
                try:
                    users_result = await session.execute(text("SELECT email, is_active, is_staff FROM users LIMIT 5"))
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


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions and redirect to login if authentication fails"""
    if exc.status_code in [401, 403]:
        return RedirectResponse(url="/login", status_code=302)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )