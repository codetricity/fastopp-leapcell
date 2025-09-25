# FastOpp Base Assets

A minimal FastAPI application with authentication and protected content, built on the FastOpp framework.

## Features

- **Admin Panel**: SQLAdmin interface for database management
- **User Authentication**: Login/logout system with JWT tokens
- **Protected Content**: Password-protected pages requiring staff/admin access
- **Session Management**: Secure session handling with cookies
- **Modern UI**: Tailwind CSS styling with responsive design

## Quick Start

### 1. Setup Database

```bash
uv run python oppman.py db
```

### 2. Create Admin User

```bash
uv run python oppman.py superuser
```

### 3. Add Sample Data (Optional)

```bash
uv run python oppman.py users
uv run python oppman.py products
```

### 4. Start the Application

```bash
uv run python oppman.py runserver
```

## Available Routes

- **`/`** - Home page with navigation
- **`/login`** - User authentication page
- **`/protected`** - Password-protected content (requires login)
- **`/admin/`** - SQLAdmin interface for database management
- **`/health`** - Health check endpoint

## Authentication

The application uses a dual authentication system:

1. **Admin Panel Authentication**: Uses SQLAdmin's built-in authentication backend
2. **User Authentication**: Custom JWT-based system with cookie storage

### User Roles

- **Staff Users**: Can access protected content and admin panel
- **Superusers**: Full administrative access
- **Regular Users**: No access to protected content

### Default Credentials

- **Superuser**: `admin@example.com` / `admin123`
- **Test Users**: `test123` (for all test users)

## Architecture

```
base_assets/
├── main.py              # FastAPI application entry point
├── routes/
│   ├── auth.py         # Authentication routes (login/logout)
│   └── pages.py        # Page routes (home, protected content)
└── templates/
    ├── index.html      # Home page
    ├── login.html      # Login form
    └── protected.html  # Protected content page
```

## Dependencies

- FastAPI
- SQLAdmin
- Jinja2Templates
- FastAPI Users (for password hashing)
- JWT for token management

## Security Features

- JWT token-based authentication
- Secure cookie storage
- Password hashing with FastAPI Users
- Session expiration (30 minutes)
- Role-based access control
- CSRF protection via session middleware

## Development

This is a minimal implementation that demonstrates:

- User authentication flow
- Protected route implementation
- Template rendering with Jinja2
- Session management
- Admin panel integration

To extend functionality, add new routes in the `routes/` directory and corresponding templates in `templates/`.
