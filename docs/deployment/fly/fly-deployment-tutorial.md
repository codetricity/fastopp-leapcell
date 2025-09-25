# Fly.io Deployment Tutorial

## Overview

This tutorial walks you through deploying the fastopp application to Fly.io, including setting up persistent storage for file uploads and running the demo.

## Prerequisites

- [Fly.io CLI installed](https://fly.io/docs/hands-on/install-flyctl/)
- [Fly.io account](https://fly.io/docs/hands-on/sign-up/)
- [Git repository](https://github.com/your-org/fastopp) cloned locally

## Step 1: Initial Setup

### 1.1 Login to Fly.io
```bash
fly auth login
```

### 1.2 Create a New App
```bash
fly apps create fastopp-fly-static
```

### 1.3 Create Persistent Volume
```bash
fly volumes create data --size 1 --region sjc
```

## Step 2: Configure the Application

### 2.1 Environment-Based Configuration

The application uses environment variables to handle different deployment scenarios. Update your `main.py`:

```python
# Create upload directories
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "static/uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)
PHOTOS_DIR = UPLOAD_DIR / "photos"
PHOTOS_DIR.mkdir(exist_ok=True)

# Mount uploads directory based on environment (MUST come before /static mount)
if os.getenv("UPLOAD_DIR") and os.getenv("UPLOAD_DIR") != "static/uploads":
    # In production (Fly.io), mount the uploads directory separately
    app.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Mount static files (MUST come after /static/uploads to avoid conflicts)
app.mount("/static", StaticFiles(directory="static"), name="static")
```

**Important**: The mount order is critical. The more specific path (`/static/uploads`) must be mounted before the general path (`/static`) to avoid conflicts.

### 2.2 Update Services

Update `services/webinar_service.py` to use environment variables:

```python
import os

# Change file path operations
file_path = Path(os.getenv("UPLOAD_DIR", "static/uploads")) / "photos" / unique_filename
```

### 2.3 Configure fly.toml

```toml
app = 'fastopp-fly-static'
primary_region = 'sjc'
swap_size_mb = 512 

[build]

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = 'stop'
  auto_start_machines = true
  min_machines_running = 0
  processes = ['app']

[[vm]]
  memory = '512mb'
  cpu_kind = 'shared'
  cpus = 1

[env]
  ENVIRONMENT = "production"
  UPLOAD_DIR = "/data/uploads"

[[mounts]]
  source = "data"
  destination = "/data"

[[services]]
  internal_port = 8000
  protocol = "tcp"
  [[services.ports]]
    port = 80
    handlers = ["http"]
  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

## Step 3: Deploy the Application

### 3.1 Deploy
```bash
fly deploy
```

### 3.2 Verify Deployment
```bash
fly status
```

## Step 4: Initialize the Demo

### 4.1 Connect to Fly.io Console
```bash
fly ssh console
```

### 4.2 Create Upload Directories
```bash
mkdir -p /data/uploads/photos
```

### 4.3 Run Initialization
```bash
python oppman.py init
```

### 4.4 Copy Sample Photos to Fly.io Volume
```bash
cp -r static/uploads/sample_photos/* /data/uploads/photos/
```

## Step 5: Test the Application

### 5.1 Visit Your App
Open your browser and go to: `https://fastopp-fly-static.fly.dev/`

### 5.2 Test the Demo
- Navigate to `/webinar-demo`
- Verify photos are loading correctly
- Check that no 404 errors appear in the console

## Step 6: Verify Everything Works

### 6.1 Check File Storage
```bash
# In Fly.io console
ls -la /data/uploads/photos/
```

### 6.2 Test File Persistence
```bash
# Restart the machine to verify persistence
fly machine restart
```

### 6.3 Verify Photos Still Load
Refresh the webinar-demo page to confirm photos survive restarts.

## Troubleshooting

### Photos Not Loading (404 Errors)

**Problem**: Photos return 404 errors after deployment.

**Solution**: Check the mount order in `main.py`:
```python
# CORRECT ORDER
app.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")  # FIRST
app.mount("/static", StaticFiles(directory="static"), name="static")             # SECOND

# WRONG ORDER (will cause 404 errors)
app.mount("/static", StaticFiles(directory="static"), name="static")             # FIRST
app.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")  # Never reached!
```

### Photos Not in Volume

**Problem**: `/data/uploads/photos/` directory is empty.

**Solution**: Copy sample photos manually:
```bash
cp -r static/uploads/sample_photos/* /data/uploads/photos/
```

### Environment Variable Not Set

**Problem**: `UPLOAD_DIR` environment variable is not set.

**Solution**: Verify in `fly.toml`:
```toml
[env]
  UPLOAD_DIR = "/data/uploads"
```

### Mount Conflicts

**Problem**: Static files not serving correctly.

**Solution**: Ensure mount order is correct and specific paths come before general paths.

## File Upload Workflow

### Initial Setup
1. **Run initialization**: `python oppman.py init`
2. **Copy sample photos**: `cp -r static/uploads/sample_photos/* /data/uploads/photos/`
3. **Photos are served** from `/static/uploads/photos/` URLs

### Ongoing Usage
1. **Users upload photos** via web GUI
2. **Photos stored in** `/data/uploads/photos/` (persistent volume)
3. **Photos served from** `/static/uploads/photos/` URLs
4. **Everything survives** restarts and deployments

## Benefits of This Approach

- ✅ **Environment-agnostic**: Works locally and in production
- ✅ **Persistent storage**: Files survive container restarts
- ✅ **Scalable**: Easy to extend to other deployment platforms
- ✅ **Maintainable**: Single environment variable controls behavior
- ✅ **Upstream-friendly**: Minimal changes to main application code

## Next Steps

- **Monitor usage**: Check Fly.io dashboard for resource usage
- **Scale if needed**: Adjust VM size or add more machines
- **Backup strategy**: Consider automated backups of the data volume
- **CDN integration**: Add CloudFlare or similar for high-traffic scenarios

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify mount order in `main.py`
3. Confirm environment variables are set
4. Check Fly.io logs: `fly logs`
5. Verify volume mounting: `fly volumes list`
