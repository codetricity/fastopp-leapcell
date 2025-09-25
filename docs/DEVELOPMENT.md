# Development Workflow

## Environment Setup

Ensure your development environment is properly configured:

```bash
# Check environment
python oppman.py env

# Verify database connection
python oppman.py migrate current

# Check dependencies
uv sync
```

## Development Server

Start the development server:

```bash
# Start development server
python oppman.py runserver

# Or use uvicorn directly
uv run uvicorn main:app --reload
```

## Database Management

```bash
# Create new migration
python oppman.py migrate create "Description of changes"

# Apply migrations
python oppman.py migrate upgrade

# Check migration status
python oppman.py migrate current
```

## Testing Changes

```bash
# Test database operations
python oppman.py migrate check

# Test authentication
python -m scripts.test_auth

# Test user management
python -m scripts.check_users
```

## Development Patterns

### Model-View-Service (MVS) Architecture

Follow the established MVS pattern:

- **Models** (`models.py`): Data structures and database models
- **Views** (`routes/`): HTTP endpoints and request handling
- **Services** (`services/`): Business logic and data operations

### Route Organization

Organize routes by functionality:

```python
# routes/pages.py - Page rendering routes
@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# routes/api.py - JSON API endpoints
@router.get("/api/data")
async def get_data():
    return {"data": "example"}

# routes/auth.py - Authentication routes
@router.post("/login")
async def login():
    # Login logic
    pass
```

### Service Layer

Implement business logic in services:

```python
# services/product_service.py
class ProductService:
    @staticmethod
    async def get_products():
        # Database query logic
        pass
    
    @staticmethod
    async def create_product(product_data):
        # Product creation logic
        pass
```

### Template Structure

Use consistent template organization:

```
templates/
├── index.html              # Homepage
├── partials/               # Reusable components
│   ├── header.html         # Navigation header
│   ├── footer.html         # Page footer
│   └── sidebar.html        # Sidebar navigation
├── pages/                  # Page-specific templates
│   ├── dashboard.html      # Dashboard page
│   └── profile.html        # User profile page
└── components/             # Reusable UI components
    ├── forms.html          # Form components
    └── tables.html         # Table components
```

## Testing and Debugging

### Testing New Features

#### Manual Testing
1. Start development server
2. Navigate to new page/feature
3. Test all functionality
4. Check error handling
5. Verify responsive design

#### Automated Testing
```bash
# Run tests
uv run python -m pytest

# Run specific test file
uv run python -m pytest tests/test_pages.py

# Run with coverage
uv run python -m pytest --cov=.
```

### Debugging Techniques

#### Logging
```python
import logging

logger = logging.getLogger(__name__)

@router.get("/debug")
async def debug_endpoint():
    logger.debug("Debug endpoint accessed")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    return {"status": "debug"}
```

#### Debug Mode
```python
# Enable debug mode
import debugpy
debugpy.listen(("0.0.0.0", 5678))

# Connect with VS Code or other debugger
```

#### HTMX Debugging
```html
<!-- Enable HTMX debugging -->
<script>
    htmx.logAll();
</script>

<!-- Debug HTMX requests -->
<div hx-get="/api/data" 
     hx-trigger="click"
     hx-debug="true">
    Click to load data
</div>
```

### Common Issues and Solutions

#### HTMX Loading Issues
If automatic loading doesn't work:

```javascript
// Add fallback for HTMX load triggers
setTimeout(() => {
    const container = document.getElementById('container');
    if (container && container.innerHTML.includes('Loading...')) {
        htmx.trigger(container, 'load');
    }
}, 500);
```

#### Database Connection Issues
```bash
# Check database status
python oppman.py env

# Verify migrations
python oppman.py migrate current

# Test database connection
python -c "from db import AsyncSessionLocal; print('DB connection OK')"
```

#### Template Rendering Issues
```python
# Check template path
print(templates.directory)

# Verify template exists
import os
template_path = "templates/index.html"
print(f"Template exists: {os.path.exists(template_path)}")
```

## Code Standards

### Python Style

Follow PEP 8 guidelines:

```python
# Good
def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID from database."""
    return db.query(User).filter(User.id == user_id).first()

# Avoid
def getUserById(userId):
    return db.query(User).filter(User.id==userId).first()
```

### Type Hints

Use type hints consistently:

```python
from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel

async def create_user(
    user_data: Dict[str, Any],
    db: AsyncSession
) -> User:
    """Create a new user."""
    user = User(**user_data)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
```

### Error Handling

Implement proper error handling:

```python
from fastapi import HTTPException

@router.get("/users/{user_id}")
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    try:
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Documentation

Document your code:

```python
async def process_webinar_registration(
    registration_data: WebinarRegistration,
    db: AsyncSession
) -> WebinarRegistrant:
    """
    Process a new webinar registration.
    
    Args:
        registration_data: Registration information from form
        db: Database session
        
    Returns:
        Created webinar registrant record
        
    Raises:
        HTTPException: If registration validation fails
    """
    # Implementation
    pass
```

## Performance Optimization

### Database Queries

Optimize database operations:

```python
# Use select() for better performance
from sqlalchemy import select

# Good
stmt = select(User).where(User.is_active == True)
users = await db.execute(stmt)

# Avoid
users = await db.query(User).filter(User.is_active == True).all()
```

### Caching

Implement caching for expensive operations:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_configuration():
    """Cache configuration data."""
    return load_config_from_file()

# Or use Redis for distributed caching
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

async def get_cached_data(key: str):
    data = redis_client.get(key)
    if not data:
        data = await fetch_data_from_database()
        redis_client.setex(key, 3600, data)  # Cache for 1 hour
    return data
```

### Async Operations

Use async/await properly:

```python
# Good - concurrent operations
async def get_user_data(user_id: str):
    async with httpx.AsyncClient() as client:
        user_response, profile_response = await asyncio.gather(
            client.get(f"/api/users/{user_id}"),
            client.get(f"/api/users/{user_id}/profile")
        )
        return user_response.json(), profile_response.json()

# Avoid - sequential operations
async def get_user_data(user_id: str):
    async with httpx.AsyncClient() as client:
        user_response = await client.get(f"/api/users/{user_id}")
        profile_response = await client.get(f"/api/users/{user_id}/profile")
        return user_response.json(), profile_response.json()
```

## Deployment Preparation

### Environment Configuration

Prepare for production:

```bash
# Create production .env
cp .env .env.production

# Update production values
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
ENVIRONMENT=production
DEBUG=false
```

### Database Migrations

Ensure migrations are ready:

```bash
# Check migration status
python oppman.py migrate check

# Create production migration if needed
python oppman.py migrate create "Production preparation"

# Test migrations
python oppman.py migrate upgrade
```

### Static Files

Prepare static assets:

```bash
# Collect static files
python -m scripts.collect_static

# Optimize images
python -m scripts.optimize_images

# Generate favicon
python -m scripts.generate_favicon
```

## Next Steps

After setting up development workflow:

1. **Create New Pages**: Add new features and pages to the application
2. **Implement Testing**: Add automated tests for new functionality
3. **Optimize Performance**: Monitor and improve application performance
4. **Prepare for Production**: Ensure code is production-ready
