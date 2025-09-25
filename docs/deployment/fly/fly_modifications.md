# Fly.io Deployment Guide

This guide covers deploying your FastOpp application to Fly.io, including environment configuration, production server setup, and troubleshooting common deployment issues.

## Overview

- **Development**: SQLite with aiosqlite (default) or PostgreSQL with asyncpg
- **Production**: PostgreSQL with asyncpg + pgvector (optional)
- **Configuration**: Environment variables for flexible database switching
- **Server**: DigitalOcean Ubuntu 24.04 Droplet (production)
- **Process Manager**: Gunicorn + Uvicorn (production)

## Fly.io Deployment

### Problem Description

When deploying to Fly.io, we encountered a critical issue with database migrations:

```
sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here. Was IO attempted in an unexpected place?
```

### Root Cause

The issue occurred because:

1. **App uses async SQLAlchemy**: Our FastAPI app uses `sqlite+aiosqlite:////data/test.db` for async database operations
2. **Alembic needs sync operations**: Database migrations must run synchronously, not in async context
3. **URL mismatch**: Alembic was trying to use the async driver during migrations, causing context errors

### Solution: URL Conversion in env.py

We modified `alembic/env.py` to automatically convert async SQLite URLs to regular SQLite URLs during migrations.

#### Before (Problematic)
```python
# alembic/env.py
def run_migrations_offline() -> None:
    url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
    # This would be: sqlite+aiosqlite:////data/test.db
    context.configure(url=url, ...)

def run_migrations_online() -> None:
    database_url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
    # Same async URL causing issues
    config.set_main_option("sqlalchemy.url", database_url)
```

#### After (Fixed)
```python
# alembic/env.py
def run_migrations_offline() -> None:
    url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
    
    # Convert async SQLite URL to regular SQLite URL for migrations
    if url and "aiosqlite" in url:
        url = url.replace("sqlite+aiosqlite://", "sqlite://")
    
    context.configure(url=url, ...)

def run_migrations_online() -> None:
    database_url = os.getenv("DATABASE_URL", config.get_main_option("sqlalchemy.url"))
    
    # Convert async SQLite URL to regular SQLite URL for migrations
    if database_url and "aiosqlite" in url:
        database_url = database_url.replace("sqlite+aiosqlite://", "sqlite://")
    
    config.set_main_option("sqlalchemy.url", database_url)
```

### What This Fixes

1. **App Runtime**: Still uses `sqlite+aiosqlite:////data/test.db` for normal async operations
2. **Migrations**: Automatically converts to `sqlite:////data/test.db` for sync migration operations
3. **No Code Changes**: The app code doesn't need to change, only the Alembic configuration

### Key Benefits

- ✅ **Migrations work**: No more async context errors
- ✅ **App unchanged**: FastAPI app continues using async SQLAlchemy
- ✅ **Automatic**: URL conversion happens transparently during migrations
- ✅ **Maintainable**: Single place to handle the conversion logic

## Environment Configuration

### Fly.io Secrets

Set these environment variables in Fly.io:

```bash
DATABASE_URL=sqlite+aiosqlite:////data/test.db
SECRET_KEY=your_very_secure_production_secret_key_here
ENVIRONMENT=production
```

### Local Development

```bash
DATABASE_URL=sqlite+aiosqlite:///./test.db
SECRET_KEY=your_development_secret_key_here
ENVIRONMENT=development
```

Both work seamlessly with this configuration.

## Production Server Setup

### Server Requirements

- **OS**: Ubuntu 24.04 LTS (recommended)
- **RAM**: Minimum 2GB, 4GB recommended
- **Storage**: 20GB+ for database and application files
- **CPU**: 2+ cores recommended

### Process Management

#### Using Systemd

Create a systemd service file:

```ini
# /etc/systemd/system/fastopp.service
[Unit]
Description=FastOpp FastAPI Application
After=network.target

[Service]
Type=exec
User=fastopp
WorkingDirectory=/opt/fastopp
Environment=PATH=/opt/fastopp/venv/bin
ExecStart=/opt/fastopp/venv/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Using Gunicorn + Uvicorn

```bash
# Install production dependencies
uv add gunicorn

# Start production server
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/fastopp
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/fastopp/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## SSL Configuration

### Let's Encrypt Setup

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Database Setup

### PostgreSQL Installation

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE fastopp_db;
CREATE USER fastopp_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE fastopp_db TO fastopp_user;
\q

# Enable pgvector extension (for AI features)
sudo -u postgres psql -d fastopp_db -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Database Configuration

```bash
# /etc/postgresql/14/main/postgresql.conf
# Adjust memory settings based on server resources
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
```

## Monitoring and Logging

### Log Configuration

```python
# main.py
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/fastopp.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
```

### Health Checks

```python
# routes/api.py
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

## Backup Strategy

### Database Backups

```bash
# PostgreSQL backup script
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump fastopp_db > $BACKUP_DIR/fastopp_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "fastopp_*.sql" -mtime +7 -delete
```

### Application Backups

```bash
# Backup application files
tar -czf /opt/backups/fastopp_app_$DATE.tar.gz /opt/fastopp
```

## Security Considerations

### Firewall Configuration

```bash
# UFW firewall setup
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### Environment Security

- Use strong, unique passwords
- Rotate secrets regularly
- Limit database user permissions
- Enable SSL/TLS encryption
- Regular security updates

## Deployment Commands

### Using oppman.py

```bash
# Check environment
python oppman.py env

# Run migrations
python oppman.py migrate upgrade

# Start production server
python oppman.py production

# Backup database
python oppman.py backup
```

### Manual Deployment

```bash
# Pull latest code
git pull origin main

# Install dependencies
uv sync

# Run migrations
alembic upgrade head

# Restart service
sudo systemctl restart fastopp
```

## Troubleshooting

### Common Issues

1. **Migration Errors**: Check Alembic configuration and database connectivity
2. **Permission Issues**: Verify file ownership and database user permissions
3. **Memory Issues**: Adjust Gunicorn worker count and PostgreSQL memory settings
4. **SSL Issues**: Verify certificate validity and Nginx configuration

### Debug Mode

For troubleshooting, temporarily enable debug mode:

```bash
# Set debug environment variable
export DEBUG=true

# Start with verbose logging
gunicorn main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --log-level debug
```

## Next Steps

After successful deployment:

1. **Monitor Performance**: Check logs and server metrics
2. **Set Up Monitoring**: Implement application performance monitoring
3. **Configure Alerts**: Set up notifications for critical issues
4. **Plan Scaling**: Prepare for increased traffic and load

For more information, see:
- [POSTGRESQL_SETUP.md](POSTGRESQL_SETUP.md) - PostgreSQL setup and database configuration
- [DATABASE.md](../DATABASE.md) - Database management and migrations
- [ARCHITECTURE.md](../ARCHITECTURE.md) - System architecture overview
