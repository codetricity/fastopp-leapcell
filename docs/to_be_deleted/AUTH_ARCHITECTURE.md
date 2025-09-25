# Authentication Architecture

## Overview

The authentication system has been reorganized to follow a cleaner Model-View-Services architecture. All authentication-related functionality is now consolidated in the `auth/` module.

## Structure

```
auth/
├── __init__.py      # Module exports and public API
├── core.py          # Core JWT authentication logic
├── users.py         # FastAPI Users integration
└── admin.py         # SQLAdmin authentication
```

## Components

### `auth/core.py`
Contains the core JWT-based authentication logic:

- `create_access_token()` - Create JWT tokens
- `verify_token()` - Verify JWT tokens
- `get_current_user()` - Get authenticated user from Bearer token
- `get_current_superuser()` - Get authenticated superuser
- `get_current_staff_or_admin()` - Get authenticated staff/admin user
- `create_user_token()` - Create user-specific tokens
- `get_current_user_from_cookies()` - Get user from cookies
- `get_current_staff_or_admin_from_cookies()` - Get staff/admin from cookies

### `auth/users.py`
Handles FastAPI Users integration:

- `UserManager` - User management class
- `get_user_db()` - Database dependency
- `get_user_manager()` - User manager dependency
- `jwt_strategy` - JWT authentication strategy
- `auth_backend` - Authentication backend
- `fastapi_users` - FastAPI Users instance

### `auth/admin.py`
Manages SQLAdmin authentication:

- `AdminAuth` - SQLAdmin authentication backend
- Login/logout/authentication methods for admin panel

## Usage

### Importing Authentication Components

```python
# Core authentication
from auth.core import get_current_user, create_user_token

# FastAPI Users
from auth.users import fastapi_users, auth_backend

# Admin authentication
from auth.admin import AdminAuth

# Or import everything
from auth import *
```

### Route Protection

```python
from fastapi import Depends
from auth.core import get_current_staff_or_admin_from_cookies

@router.get("/protected")
async def protected_route(request: Request):
    user = await get_current_staff_or_admin_from_cookies(request)
    return {"message": f"Hello {user.email}"}
```

## Migration from Old Structure

The following files were moved from the root directory:

- `users.py` → `auth/users.py`
- `auth.py` → `auth/core.py`
- `admin_auth.py` → `auth/admin.py`

All imports have been updated to use the new structure.

## Benefits

1. **Cleaner Root Directory**: Authentication files no longer clutter the root
2. **Better Organization**: Related functionality is grouped together
3. **Easier Maintenance**: Clear separation of concerns
4. **Better Imports**: Explicit imports from specific modules
5. **Follows MVS Pattern**: Aligns with Model-View-Services architecture

## Testing

To test the authentication module:

```bash
uv run python -c "from auth import *; print('Auth module works')"
```

To test the main application:

```bash
uv run python -c "from main import app; print('App works')"
``` 