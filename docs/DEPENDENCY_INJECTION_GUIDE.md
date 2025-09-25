# FastAPI Dependency Injection Guide

## What is Dependency Injection?

Dependency Injection (DI) is a design pattern that makes your code more testable, maintainable, and flexible. Instead of creating objects directly inside your functions, you "inject" them as parameters.

## Before vs After

### ❌ Old Way (Tightly Coupled)
```python
@router.get("/products")
async def get_products():
    # Direct database access - hard to test
    session = AsyncSessionLocal()
    # Business logic mixed with database code
    products = await session.execute(select(Product))
    return products.scalars().all()
```

### ✅ New Way (Dependency Injection)
```python
@router.get("/products")
async def get_products(
    product_service = Depends(get_product_service)
):
    # Clean separation - easy to test
    return await product_service.get_products()
```

## Key Benefits

### 1. **Easy Testing**
```python
# You can easily mock the service for testing
def test_get_products():
    mock_service = Mock()
    mock_service.get_products.return_value = [{"id": 1, "name": "Test"}]
    
    # Test your endpoint with mock data
    result = get_products(product_service=mock_service)
    assert result == [{"id": 1, "name": "Test"}]
```

### 2. **Better Organization**
- **Configuration**: All settings in one place
- **Database**: Session management centralized
- **Services**: Business logic separated from routes
- **Authentication**: User management centralized with JWT and role-based access

### 3. **Flexibility**
- Swap implementations easily
- Add new features without changing existing code
- Configure different behaviors for different environments

## How It Works in FastOpp

### 1. **Configuration Management**
```python
# dependencies/config.py
class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./test.db"
    secret_key: str = "dev_secret_key"
    environment: str = "development"

def get_settings() -> Settings:
    return Settings()
```

### 2. **Database Sessions**
```python
# dependencies/database.py
async def get_db_session(
    session_factory: async_sessionmaker = Depends(create_session_factory)
) -> AsyncSession:
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 3. **Service Dependencies**
```python
# dependencies/services.py
def get_product_service(
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings)
):
    from services.product_service import ProductService
    return ProductService(session=session, settings=settings)
```

### 4. **Service Classes**
```python
# services/product_service.py
class ProductService:
    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings
    
    async def get_products(self):
        # Business logic using injected dependencies
        result = await self.session.execute(select(Product))
        return result.scalars().all()
```

### 5. **Authentication Dependencies**
```python
# dependencies/auth.py
async def get_current_user_from_cookies(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings)
) -> User:
    """Get current authenticated user using dependency injection"""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Verify JWT token using injected settings
    payload = verify_token(token, settings)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get user from database using injected session
    result = await session.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    return user
```

## What You Can Learn

### Beginner Level
- **Understand `Depends()`**: See how FastAPI injects dependencies
- **Service Pattern**: Learn how to structure business logic
- **Configuration**: Centralize your app settings

### Intermediate Level
- **Add New Services**: Create services following the established pattern
- **New API Endpoints**: Build endpoints with dependency injection
- **Testing**: Write tests with mockable dependencies

### Advanced Level
- **Authentication**: JWT token management and role-based access control
- **Security**: Session management and permission checking
- **Admin Integration**: SQLAdmin authentication with dependency injection
- **Middleware**: Add custom middleware patterns
- **Complex Services**: Build sophisticated business logic

## File Structure

```text
dependencies/
├── __init__.py
├── config.py          # Centralized settings
├── database.py        # Database session management
├── services.py        # Service dependency providers
└── auth.py            # Authentication dependencies (JWT, RBAC, session management)

services/
├── product_service.py    # Business logic with DI
├── webinar_service.py    # Business logic with DI
└── chat_service.py       # Business logic with DI

auth/
├── admin.py          # SQLAdmin authentication backend
├── core.py           # Core authentication functions
└── users.py          # User management utilities
```

## Key Patterns to Follow

### 1. **Service Constructor Injection**
```python
class MyService:
    def __init__(self, session: AsyncSession, settings: Settings):
        self.session = session
        self.settings = settings
```

### 2. **Route Handler Pattern**
```python
@router.get("/my-endpoint")
async def my_endpoint(
    my_service = Depends(get_my_service)
):
    return await my_service.do_something()
```

### 3. **Dependency Provider**
```python
def get_my_service(
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings)
):
    from services.my_service import MyService
    return MyService(session=session, settings=settings)
```

### 4. **Authentication Pattern**
```python
# Protected route with authentication
@router.get("/protected")
async def protected_endpoint(
    current_user: User = Depends(get_current_staff_or_admin)
):
    return {"message": f"Hello {current_user.email}!"}

# Authentication dependency
async def get_current_staff_or_admin(
    current_user: User = Depends(get_current_user_from_cookies)
) -> User:
    """Get current user with staff or admin privileges"""
    if not (current_user.is_staff or current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user
```

## Authentication System

### How Authentication Works with DI

The authentication system demonstrates advanced dependency injection patterns:

**JWT Token Management**:
```python
# Token creation with settings injection
def create_access_token(
    data: dict, 
    settings: Settings = Depends(get_settings)
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
```

**User Authentication**:
```python
# User authentication with database session injection
async def get_current_user_from_cookies(
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings)
) -> User:
    # Extract token from cookies
    token = request.cookies.get("access_token")
    
    # Verify token using injected settings
    payload = verify_token(token, settings)
    
    # Get user from database using injected session
    result = await session.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    
    return user
```

**Role-Based Access Control**:
```python
# Permission checking with dependency chaining
async def get_current_staff_or_admin(
    current_user: User = Depends(get_current_user_from_cookies)
) -> User:
    if not (current_user.is_staff or current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user
```

### Key Learning Points

1. **Dependency Chaining**: One dependency can depend on another
2. **Settings Injection**: Configuration is injected throughout the system
3. **Database Session Management**: Proper session lifecycle with DI
4. **Error Handling**: HTTP exceptions with proper status codes
5. **Security**: JWT tokens and role-based access control

## Next Steps

1. **Study the Code**: Look at `dependencies/` and `services/` directories
2. **Explore Authentication**: Check out `dependencies/auth.py` for advanced patterns
3. **Add a New Service**: Create a new service following the pattern
4. **Build an Endpoint**: Add a new API endpoint with dependency injection
5. **Write Tests**: Test your new code with mockable dependencies
6. **Extend Authentication**: Add new roles or permissions

## Why This Matters

- **Real-World Skills**: This is how professional FastAPI apps are built
- **Better Code**: Easier to maintain and extend
- **Testing**: You can actually test your code properly
- **Team Work**: Other developers can understand and modify your code

This implementation gives you a solid foundation for building FastAPI applications the right way!
