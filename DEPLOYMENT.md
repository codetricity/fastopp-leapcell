# FastOpp PostgreSQL Edition - Deployment Guide

This guide covers deploying FastOpp PostgreSQL Edition to various platforms, with special focus on **LeapCell** for educational use.

## Table of Contents

- [LeapCell Deployment (Recommended for Students)](#leapcell-deployment)
- [Local Development](#local-development)
- [Other Platforms](#other-platforms)
- [Troubleshooting](#troubleshooting)

## LeapCell Deployment

**LeapCell** offers a free tier perfect for students learning serverless deployment.

### Prerequisites

1. **LeapCell Account**: Sign up at [leapcell.io](https://leapcell.io/)
2. **GitHub Repository**: Your code must be in a GitHub repository
3. **PostgreSQL Database**: LeapCell provides free PostgreSQL

### Step 1: Prepare Your Repository

```bash
# Ensure your code is committed and pushed to GitHub
git add .
git commit -m "Prepare for LeapCell deployment"
git push origin main
```

### Step 2: Create LeapCell Project

1. Go to [LeapCell Dashboard](https://leapcell.io/dashboard)
2. Click **"New Project"**
3. Connect your GitHub repository
4. Select the repository containing FastOpp

### Step 3: Configure Environment Variables

In the LeapCell dashboard, set these environment variables:

```bash
# Database (automatically provided by LeapCell)
DATABASE_URL=postgresql+psycopg2://username:password@host:port/database

# Security (generate with: uv run python oppman.py secrets)
SECRET_KEY=your_generated_secret_key_here

# Environment
ENVIRONMENT=production

# File Uploads
UPLOAD_DIR=/tmp/uploads

# Optional: AI Features
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Step 4: Deploy

1. Click **"Deploy"** in LeapCell dashboard
2. Wait for deployment to complete
3. Your app will be available at `https://your-app.leapcell.dev`

### Step 5: Initialize Database

After deployment, initialize your database:

```bash
# Using LeapCell's built-in terminal or curl
curl -X POST https://your-app.leapcell.dev/async/init-demo
```

### Step 6: Verify Deployment

Visit your deployed app:
- **Homepage**: `https://your-app.leapcell.dev/`
- **Admin Panel**: `https://your-app.leapcell.dev/admin/`
- **API Docs**: `https://your-app.leapcell.dev/docs`

**Default Credentials:**
- **Email**: `admin@example.com`
- **Password**: `admin123`

## Local Development

### Prerequisites

- **Python 3.12+**
- **PostgreSQL** (local installation)
- **uv** package manager

### Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/fastopp-postgresql-edition.git
cd fastopp-postgresql-edition
```

### Step 2: Install Dependencies

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### Step 3: Set Up Database

```bash
# Install PostgreSQL (macOS with Homebrew)
brew install postgresql
brew services start postgresql

# Create database
createdb fastopp_test

# Or use Docker
docker run --name postgres-fastopp -e POSTGRES_PASSWORD=password -e POSTGRES_DB=fastopp_test -p 5432:5432 -d postgres:15
```

### Step 4: Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env with your database settings
DATABASE_URL=postgresql+psycopg2://username@localhost:5432/fastopp_test
SECRET_KEY=$(uv run python oppman.py secrets | grep SECRET_KEY | cut -d'=' -f2)
```

### Step 5: Initialize and Run

```bash
# Initialize database
uv run python oppdemo.py init

# Start development server
uv run uvicorn main:app --reload
```

Visit `http://localhost:8000` to see your app.

## Other Platforms

### Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
fly deploy
```

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### Heroku

```bash
# Install Heroku CLI
# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

## Troubleshooting

### Common Issues

#### Database Connection Errors

```bash
# Check database URL format
echo $DATABASE_URL

# Test connection
uv run python -c "from db import engine; print('Connection OK')"
```

#### Environment Variables

```bash
# Check all environment variables
uv run python -c "from dependencies.config import get_settings; print(get_settings())"
```

#### File Upload Issues

```bash
# Check upload directory permissions
ls -la static/uploads/

# Create upload directory if missing
mkdir -p static/uploads
```

### LeapCell Specific Issues

#### Health Check Failures

```bash
# Check health endpoint
curl https://your-app.leapcell.dev/kaithheathcheck
```

#### Database Initialization

```bash
# Check database status
curl https://your-app.leapcell.dev/debug/connection

# Initialize if needed
curl -X POST https://your-app.leapcell.dev/async/init-demo
```

#### File Storage

```bash
# Check file uploads
curl https://your-app.leapcell.dev/debug/files
```

### Getting Help

1. **Check Logs**: Look at deployment logs in LeapCell dashboard
2. **Test Locally**: Ensure everything works locally first
3. **GitHub Issues**: Report bugs and ask questions
4. **Documentation**: Check README.md for detailed information

## Best Practices

### Security

- **Never commit** `.env` files
- **Use strong** SECRET_KEY values
- **Rotate** credentials regularly
- **Limit** database access

### Performance

- **Monitor** database connections
- **Optimize** queries for production
- **Use** connection pooling
- **Cache** expensive operations

### Monitoring

- **Set up** health checks
- **Monitor** error rates
- **Track** database performance
- **Log** important events

## Educational Resources

### Tutorials

- [FastAPI Official Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [LeapCell Getting Started](https://leapcell.io/docs)

### Related Projects

- [Original FastOpp](https://github.com/Oppkey/FastOpp)
- [FastAPI Examples](https://github.com/tiangolo/fastapi)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)

## Support

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and community help
- **LeapCell Support**: Platform-specific issues
- **FastAPI Community**: General FastAPI questions
