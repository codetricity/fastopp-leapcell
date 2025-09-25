# Development vs Production Setup

## Quick Reference

| Component | Development | Production |
|-----------|-------------|------------|
| **Database** | SQLite + aiosqlite | PostgreSQL + asyncpg |
| **Server** | uvicorn --reload | Gunicorn + Uvicorn |
| **Process Manager** | None (manual) | Systemd |
| **Reverse Proxy** | None | Nginx |
| **SSL** | None | Let's Encrypt |
| **Logging** | Console | File + rotation |
| **Backups** | Manual | Automated |

## Database Configuration (Recommended: Environment Variables)

### Development Setup

Create a `.env` file in your project root:

```bash
# .env
DATABASE_URL=sqlite+aiosqlite:///./test.db
SECRET_KEY=your_development_secret_key_here
ENVIRONMENT=development
```

Update your `db.py` to use environment variables:

```python
# db.py
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment (defaults to SQLite for development)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

# Create async engine
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # set to False in production
    future=True
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)
```

### Production Setup

For production, your `.env` file would contain:

```bash
# .env (production)
DATABASE_URL=postgresql+asyncpg://fastopp_user:your_secure_password@localhost/fastopp_db
SECRET_KEY=your_very_secure_production_secret_key_here
ENVIRONMENT=production
```

### Install python-dotenv

```bash
# Add dotenv dependency
uv add python-dotenv
```

## Database URLs by Environment

### Development (SQLite)
```python
DATABASE_URL = "sqlite+aiosqlite:///./test.db"
```

### Production (PostgreSQL)
```python
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/fastopp_db"
```

## Server Commands

### Development
```bash
# Start development server
uv run uvicorn main:app --reload

# Or use oppman.py
python oppman.py runserver
```

### Production
```bash
# Start service
sudo systemctl start fastopp

# Check status
sudo systemctl status fastopp

# View logs
sudo journalctl -u fastopp -f
```

## Key Differences

### 1. **Environment-Based Configuration**
- **Development**: Uses `.env` file with SQLite configuration
- **Production**: Uses `.env` file with PostgreSQL configuration
- **Benefits**: Easy switching, secure credential management

### 2. **asyncpg vs aiosqlite**
- **Development**: `aiosqlite` for SQLite async operations
- **Production**: `asyncpg` for PostgreSQL async operations
- **Performance**: asyncpg is much faster for PostgreSQL

### 3. **Gunicorn + Uvicorn**
- **Development**: Single uvicorn process with auto-reload
- **Production**: Multiple worker processes managed by Gunicorn
- **Benefits**: Better performance, process isolation, auto-restart

### 4. **Environment Variables**
- **Development**: `.env` file with development settings
- **Production**: `.env` file with production settings
- **Security**: Credentials never hardcoded in source code

### 5. **Logging**
- **Development**: Console output
- **Production**: Structured file logging with rotation

### 6. **Security**
- **Development**: Basic setup
- **Production**: SSL, security headers, firewall

## Development Setup Checklist

For development environment:

- [ ] Install python-dotenv: `uv add python-dotenv`
- [ ] Create `.env` file with development settings
- [ ] Update `db.py` to use environment variables
- [ ] Test database connection
- [ ] Run migrations: `python oppman.py migrate init`
- [ ] Initialize database: `python oppman.py init`
- [ ] Start development server: `python oppman.py runserver`

## Production Migration Checklist

When moving from development to production:

- [ ] Install PostgreSQL 15
- [ ] Install asyncpg: `uv add asyncpg`
- [ ] Create production `.env` file
- [ ] Install Gunicorn: `uv add gunicorn`
- [ ] Create gunicorn.conf.py
- [ ] Create systemd service
- [ ] Set up Nginx (optional)
- [ ] Configure SSL certificates
- [ ] Set up log rotation
- [ ] Create backup scripts
- [ ] Test database migration
- [ ] Verify all endpoints work

## Performance Comparison

| Metric | Development | Production |
|--------|-------------|------------|
| **Concurrent Users** | 1-10 | 1000+ |
| **Database Performance** | Good | Excellent |
| **Memory Usage** | Low | Optimized |
| **Reliability** | Basic | High |
| **Monitoring** | None | Comprehensive |

## Environment Variable Benefits

### Security
- ✅ Credentials never in source code
- ✅ Different settings per environment
- ✅ Easy to change without code changes

### Flexibility
- ✅ Easy switching between databases
- ✅ Development team can use different settings
- ✅ CI/CD friendly

### Best Practices
- ✅ Follows 12-factor app methodology
- ✅ Industry standard approach
- ✅ Works with containerization (Docker) 