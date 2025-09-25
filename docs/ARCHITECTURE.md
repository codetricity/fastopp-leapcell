# FastAPI MVS Architecture

This document outlines the Model-View-Service (MVS) architecture implemented in this FastAPI application.

## Directory Structure

```text
fastopp/
├── main.py                # New refactored entry point (MVS Architecture)
├── routes/                # Route handlers (View layer)
│   ├── __init__.py
│   ├── pages.py          # Page rendering routes
│   ├── auth.py           # Authentication routes
│   ├── api.py            # API data endpoints
│   └── webinar.py        # Webinar management routes
├── services/             # Business logic (Service layer)
│   ├── __init__.py
│   ├── product_service.py
│   └── webinar_service.py
├── models.py             # Data models (Model layer)
├── db.py                 # Database configuration
├── auth.py               # Authentication utilities
└── admin/                # Admin interface
```

## Components

| Functional Concept| Component | Django Equivalent |
| -- | -- | -- |
| Production Web Server | FastAPI + uvicorn (for loads < 1,000 concurrent connections). Used NGINX on last Digital Ocean deploy. Using uvicorn on fly and railway | NGINX + Gunicorn |
| Development Web Server | uvicorn  | `manage.py runserver` in development. Django Framework |
| Development SQL Database | SQLite | SQLite |
| Production SQL Database | PostgreSQL with pgvector. Though, we have used SQLite with FTS5 and FAISS in production | PostgreSQL + pgvector, asyncpg |
| User Management & Authentication | Custom implementation with SQLModel/SQLAlchemy + FastAPI Users password hashing only | Django Admin |
| Database Management | [SQLAdmin](https://aminalaee.github.io/sqladmin/) + Template | Django Admin |
| API Endpoints | Built-in FastAPI routes with automatic OpenAPI documentation | Django REST Framework |
| HTML Templating | Jinja2 with HTMX + Alpine.js + DaisyUI (optimized for AI applications with server-sent events). in-progress.  Currently used too much JavaScript. Will simplify in the future. | Django Templates (Jinja2-like syntax) |
| Dependency Injection | Built-in FastAPI `Depends()` system for services, database sessions, and configuration | No built-in DI. Requires manual service layer or third-party packages such as [django-injector](https://pypi.org/project/django-injector/) |

## Layer Responsibilities

### 1. Model Layer (`models.py`)

- **Purpose**: Define data structures and database models
- **Responsibilities**:
  - SQLModel/SQLAlchemy model definitions
  - Data validation and constraints
  - Database schema representation

### 2. View Layer (`routes/`)

- **Purpose**: Handle HTTP requests and responses
- **Responsibilities**:
  - Route definitions and HTTP method handling
  - Request/response formatting
  - Input validation
  - Authentication checks
  - Error handling

#### Route Modules

- **`pages.py`**: HTML page rendering routes
- **`auth.py`**: Authentication and session management
- **`api.py`**: JSON API endpoints for data
- **`webinar.py`**: Webinar registrant management operations

### 3. Service Layer (`services/`)

- **Purpose**: Business logic and data operations
- **Responsibilities**:
  - Database operations
  - File handling
  - Business rules implementation
  - Data transformation
  - Error handling for business logic

#### Service Classes

- **`ProductService`**: Product-related operations and statistics
- **`WebinarService`**: Webinar registrant management operations

## Benefits of This Architecture

### 1. **Separation of Concerns**

- Routes handle HTTP concerns only
- Services contain business logic
- Models focus on data structure

### 2. **Testability**

- Services can be unit tested independently
- Routes can be tested with mocked services
- Clear interfaces between layers

### 3. **Reusability**

- Services can be used by multiple routes
- Business logic is centralized
- Consistent error handling

### 4. **Scalability**

- Easy to add new route modules
- Services can be extended without affecting routes
- Clear patterns for new features

### Adding New Features

1. **New Route**: Add to appropriate route module
2. **New Service**: Create new service class in `services/`
3. **New Model**: Add to `models.py`

### Example: Adding a New Feature

```python
# 1. Add service method
# services/webinar_service.py
@staticmethod
async def get_registrant_by_id(registrant_id: str):
    # Business logic here
    pass

# 2. Add route
# routes/webinar.py
@router.get("/registrant/{registrant_id}")
async def get_registrant(registrant_id: str):
    registrant = await WebinarService.get_registrant_by_id(registrant_id)
    return JSONResponse(registrant)
```

## Best Practices

1. **Keep routes thin**: Routes should only handle HTTP concerns
2. **Use services for business logic**: All database/file operations go in services
3. **Consistent error handling**: Use service return tuples for success/error
4. **Clear naming**: Use descriptive names for routes and services
5. **Documentation**: Add docstrings to all public methods

## Future Enhancements

1. **Repository Pattern**: Add data access layer between services and models
2. **Dependency Injection**: Use FastAPI's dependency injection for services
3. **Validation Layer**: Add Pydantic models for request/response validation
4. **Caching Layer**: Add Redis or similar for caching
5. **Event System**: Add async event handling for side effects
