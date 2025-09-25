# PostgreSQL Installation Guide

This guide covers setting up PostgreSQL with asyncpg for both development and production environments.

## Overview

- **Development**: SQLite with aiosqlite (default) or PostgreSQL with asyncpg
- **Production**: PostgreSQL with asyncpg + pgvector (optional)
- **Configuration**: Environment variables for flexible database switching
- **Server**: DigitalOcean Ubuntu 24.04 Droplet (production)
- **Process Manager**: Gunicorn + Uvicorn (production)

## Quick Start (Development)

### 1. Install Dependencies

```bash
# Add environment variable support
uv add python-dotenv

# Add PostgreSQL support (optional for development)
uv add asyncpg
```

### 2. Environment-Based Database Configuration

Create a `.env` file in your project root:

```bash
# .env (development)
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

### 3. Development Database Options

#### Option A: SQLite (Default - Recommended for Development)

```bash
# .env
DATABASE_URL=sqlite+aiosqlite:///./test.db
```

#### Option B: PostgreSQL (For Testing PostgreSQL Features)

```bash
# .env
DATABASE_URL=postgresql+asyncpg://fastopp_user:your_password@localhost/fastopp_db
```

### 4. Initialize Database

```bash
# Initialize migrations
python oppman.py migrate init

# Create initial migration
python oppman.py migrate create "Initial migration"

# Apply migrations
python oppman.py migrate upgrade

# Initialize database with sample data
python oppman.py init
```

### 5. Start Development Server

```bash
# Start development server
python oppman.py runserver
```

---

## Production Setup (Optional - For Future Use)

For production deployment on DigitalOcean Ubuntu 24.04:

## 1. Server Setup (DigitalOcean Ubuntu 24.04)

### Initial Server Configuration

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y curl wget git build-essential python3 python3-pip python3-venv

# Create application user
sudo adduser fastopp
sudo usermod -aG sudo fastopp
```

### Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw allow OpenSSH
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8000  # For development/testing
sudo ufw enable
```

## 2. PostgreSQL Installation

### Install PostgreSQL 15

```bash
# Add PostgreSQL repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update

# Install PostgreSQL
sudo apt install -y postgresql-15 postgresql-contrib-15

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Configure PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE fastopp_db;
CREATE USER fastopp_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE fastopp_db TO fastopp_user;

# Enable pgvector extension (optional, for AI features)
CREATE EXTENSION IF NOT EXISTS vector;

# Exit PostgreSQL
\q
```

### Configure PostgreSQL for Remote Access

```bash
# Edit PostgreSQL configuration
sudo nano /etc/postgresql/15/main/postgresql.conf

# Add/modify these lines:
listen_addresses = 'localhost'
port = 5432
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
```

```bash
# Configure client authentication
sudo nano /etc/postgresql/15/main/pg_hba.conf

# Add this line for local connections:
local   fastopp_db    fastopp_user                    md5
```

```bash
# Restart PostgreSQL
sudo systemctl restart postgresql
```

## 3. Application Deployment

### Install Application Dependencies

```bash
# Switch to application user
sudo su - fastopp

# Clone application
git clone https://github.com/your-repo/fastopp.git
cd fastopp

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.cargo/env

# Install Python dependencies
uv sync
```

### Production Environment Configuration

Create production `.env` file:

```bash
# .env (production)
DATABASE_URL=postgresql+asyncpg://fastopp_user:your_secure_password@localhost/fastopp_db
SECRET_KEY=your_very_secure_production_secret_key_here
ENVIRONMENT=production
```

### Install Production Dependencies

```bash
# Add production dependencies
uv add asyncpg gunicorn
```

Update `pyproject.toml`:

```toml
[project]
dependencies = [
    # ... existing dependencies ...
    "asyncpg>=0.29.0",
    "gunicorn>=21.2.0",
    "python-dotenv>=1.0.0",
]
```

## 4. Database Migration for Production

### Initialize Production Database

```bash
# Switch to application user
sudo su - fastopp
cd fastopp

# Initialize migrations
python oppman.py migrate init

# Create initial migration
python oppman.py migrate create "Initial migration"

# Apply migrations
python oppman.py migrate upgrade

# Initialize database with sample data
python oppman.py init
```

## 5. Gunicorn + Uvicorn Configuration

### Create Gunicorn Configuration

```bash
# Create gunicorn config
nano gunicorn.conf.py
```

```python
# gunicorn.conf.py
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/fastopp/access.log"
errorlog = "/var/log/fastopp/error.log"
loglevel = "info"

# Process naming
proc_name = "fastopp"

# Server mechanics
daemon = False
pidfile = "/var/run/fastopp/gunicorn.pid"
user = "fastopp"
group = "fastopp"
tmp_upload_dir = None
```

### Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/fastopp.service
```

```ini
[Unit]
Description=FastOpp Gunicorn daemon
After=network.target

[Service]
User=fastopp
Group=fastopp
WorkingDirectory=/home/fastopp/fastopp
Environment="PATH=/home/fastopp/.cargo/bin:/home/fastopp/.local/bin"
ExecStart=/home/fastopp/.cargo/bin/uv run gunicorn main:app -c gunicorn.conf.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### Create Log Directory

```bash
# Create log directory
sudo mkdir -p /var/log/fastopp
sudo chown fastopp:fastopp /var/log/fastopp

# Create run directory
sudo mkdir -p /var/run/fastopp
sudo chown fastopp:fastopp /var/run/fastopp
```

## 6. Start Services

### Enable and Start Services

```bash
# Enable and start FastOpp service
sudo systemctl enable fastopp
sudo systemctl start fastopp

# Check status
sudo systemctl status fastopp
```

### Verify Installation

```bash
# Check if service is running
curl http://localhost:8000/

# Check logs
sudo journalctl -u fastopp -f
```

## Environment Variable Benefits

### Security
- ✅ Credentials never in source code
- ✅ Different settings per environment
- ✅ Easy to change without code changes

### Flexibility
- ✅ Easy switching between SQLite and PostgreSQL
- ✅ Development team can use different settings
- ✅ CI/CD friendly

### Best Practices
- ✅ Follows 12-factor app methodology
- ✅ Industry standard approach
- ✅ Works with containerization (Docker)

## Development vs Production Database URLs

### Development (SQLite)
```bash
DATABASE_URL=sqlite+aiosqlite:///./test.db
```

### Development (PostgreSQL - Optional)
```bash
DATABASE_URL=postgresql+asyncpg://fastopp_user:password@localhost/fastopp_db
```

### Production (PostgreSQL)
```bash
DATABASE_URL=postgresql+asyncpg://fastopp_user:your_secure_password@localhost/fastopp_db
```

## Summary

### For Development (Current Focus)

- ✅ **Environment variables** for flexible configuration
- ✅ **SQLite by default** for easy development
- ✅ **PostgreSQL optional** for testing
- ✅ **Migration system** works with both databases
- ✅ **Easy switching** between database types

### For Production (Future Use)

- ✅ **PostgreSQL 15** with asyncpg driver
- ✅ **Gunicorn + Uvicorn** for production serving
- ✅ **Environment variables** for secure configuration
- ✅ **Systemd service** for process management
- ✅ **Log rotation** and monitoring
- ✅ **Database backups** automation

Your FastAPI application now supports flexible database configuration through environment variables!
