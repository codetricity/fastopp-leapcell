# Authentication System

This FastAPI application includes a comprehensive authentication system with both web-based and API authentication. We use a **hybrid approach** that combines:

- **[FastAPI Users](https://github.com/fastapi-users/fastapi-users)** for password hashing and user management
- **Custom JWT authentication** for API access
- **Custom session-based authentication** for the admin panel
- **Advanced group-based permission system** for granular access control

## Architecture Overview

The authentication system has been reorganized to follow a cleaner Model-View-Services architecture. All authentication-related functionality is now consolidated in the `auth/` module.

### Structure

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

## Admin Panel Authentication

The admin panel uses session-based authentication similar to Django's admin interface. **Authentication verifies users against the database** instead of using hardcoded credentials.

### Access Admin Panel

1. **Visit**: http://localhost:8000/admin/
2. **Login with any staff or superuser account**:
   - Superuser: `admin@example.com` / `admin123`
   - Marketing: `marketing@example.com` / `test123`
   - Sales: `sales@example.com` / `test123`
   - Support: `staff@example.com` / `test123`

### Advanced Permission System

The system implements a **group-based permission system** with multiple permission levels:

#### **Permission Levels**

| Group | Products | Webinars | Users | Audit Logs | Description |
|-------|----------|----------|-------|------------|-------------|
| **Superuser** | ✅ Full | ✅ Full | ✅ Full | ✅ Full | Complete admin access |
| **Marketing** | ✅ Full | ✅ Full | ❌ None | ❌ None | Can manage products and webinars |
| **Sales** | ✅ Full | ✅ Assigned | ❌ None | ❌ None | Can manage products, view assigned webinars |
| **Support** | ✅ Full | ❌ None | ❌ None | ❌ None | Can only manage products |
| **Regular Users** | ❌ None | ❌ None | ❌ None | ❌ None | No admin access |

#### **Action-Based Permissions**

- **Create**: Only superusers can create products, marketing can create webinars
- **Edit**: Marketing can edit all webinars, sales can edit assigned webinars
- **Delete**: Only superusers can delete products
- **View**: Group-based data filtering (sales see only assigned webinars)

#### **Data Filtering by Group**

- **Marketing users**: See all webinar registrants
- **Sales users**: See only their assigned registrants
- **Support users**: See only public registrants
- **Superusers**: See all registrants

### Features

- ✅ **Session-based authentication**
- ✅ **Secure password verification**
- ✅ **Group-based permission system**
- ✅ **Model-specific access control**
- ✅ **Action-based permissions (CRUD)**
- ✅ **Data filtering by user group**
- ✅ **Database user lookup**
- ✅ **User management interface**
- ✅ **Audit trail (superuser only)**

## API Authentication

The application provides JWT-based authentication for API access.

### Get Authentication Token

```bash
curl -X POST http://localhost:8000/login \
  -u "admin@example.com:admin123" \
  -H "Content-Type: application/json"
```

**Response**:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Use Authentication Token

```bash
curl -X GET http://localhost:8000/admin/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

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

## Test Data

The application comes with pre-loaded test data for authentication testing:

### Users

#### **Superusers (Full Access)**

- `admin@example.com` / `admin123`
- `admin2@example.com` / `test123`

#### **Marketing Users (Products + Webinars)**

- `marketing@example.com` / `test123`
- `marketing2@example.com` / `test123`

#### **Sales Users (Products + Assigned Webinars)**

- `sales@example.com` / `test123`
- `sales2@example.com` / `test123`

#### **Support Users (Products Only)**

- `staff@example.com` / `test123`
- `support@example.com` / `test123`

#### **Regular Users (No Admin Access)**

- `user@example.com` / `test123`
- `demo@example.com` / `test123`

## Testing

To test the authentication module:

```bash
uv run python -c "from auth import *; print('Auth module works')"
```

### Test Authentication Flow

1. **Login to Admin Panel**: Visit `/admin/` and login with test credentials
2. **Test Permissions**: Try accessing different sections based on user role
3. **Test API Auth**: Use JWT tokens for API requests
4. **Test Session Auth**: Verify session persistence across requests

## Security Features

### Password Security

- **FastAPI Users PasswordHelper**: Secure password hashing
- **JWT Tokens**: Stateless authentication for APIs
- **Session Management**: Secure session handling for admin panel
- **Permission Validation**: Server-side permission checks

### Best Practices

- Use strong, unique passwords for production
- Rotate JWT secrets regularly
- Implement rate limiting for login attempts
- Log authentication events for audit purposes
- Use HTTPS in production

## Implementation Details

### FastAPI Users Integration

The application uses FastAPI Users for:

- Password hashing and verification
- User model management
- Registration and login endpoints

### Custom JWT Authentication

JWT tokens are used for:

- API access authentication
- Stateless authentication for external clients
- Token-based session management

### Session-Based Admin Authentication

The admin panel uses:

- Database-backed session storage
- Secure cookie-based sessions
- User permission verification against database records
- Group-based permission checking
- Model-specific access control

### Permission System

The permission system implements:

- **Group-based access control**: Users belong to groups with different permissions
- **Model-specific permissions**: Different models have different access rules
- **Action-based permissions**: Create, read, update, delete permissions
- **Data filtering**: Users see different data based on their group
- **Audit trail**: Audit logs for tracking changes (superuser only)
- **Session-based permissions**: Permissions stored in session for performance

### Database Models

#### **User Model**

```python
class User(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    is_staff: bool = Field(default=False)
    group: Optional[str] = Field(default=None)  # marketing, sales, support, etc.
```

#### **WebinarRegistrants Model**

```python
class WebinarRegistrants(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True, nullable=False)
    name: str = Field(max_length=100, nullable=False)
    company: Optional[str] = Field(max_length=100, default=None, nullable=True)
    webinar_title: str = Field(max_length=200, nullable=False)
    webinar_date: datetime = Field(nullable=False)
    registration_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="registered")  # registered, attended, cancelled, no_show
    assigned_sales_rep: Optional[str] = Field(default=None, nullable=True)
    group: Optional[str] = Field(default=None)  # marketing, sales, support
    is_public: bool = Field(default=True)  # Whether this registration is visible to all
    notes: Optional[str] = Field(default=None, nullable=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

#### **AuditLog Model**

```python
class AuditLog(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    action: str = Field(max_length=50)  # create, update, delete, view
    model_name: str = Field(max_length=50)  # products, webinar_registrants, users
    record_id: str = Field(max_length=50)
    changes: Optional[str] = Field(default=None, nullable=True)  # JSON of changes
    ip_address: Optional[str] = Field(default=None, nullable=True)
    user_agent: Optional[str] = Field(default=None, nullable=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

## Extension Ideas

The permission system can be easily extended with:

1. **Role-Based Permissions**: Add roles like "webinar_manager", "product_editor"
2. **Permission Groups**: Create permission groups for different departments
3. **Time-Based Permissions**: Permissions that expire
4. **API Permissions**: Decorators for API endpoint permissions
5. **Dynamic Permissions**: Load permissions from database
6. **Hierarchical Permissions**: Permission inheritance system

## Next Steps

After setting up authentication:

1. **Configure User Groups**: Set up appropriate permission levels
2. **Test Permissions**: Verify access control works correctly
3. **Customize UI**: Adapt admin interface for your needs
4. **Add Audit Logging**: Track user actions and changes

For more information, see:
- [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md) - PostgreSQL setup and database configuration
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture overview
- [FEATURES.md](FEATURES.md) - Application features and usage
