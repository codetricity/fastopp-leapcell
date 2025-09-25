# Fly.io Deployment Configuration

## 📚 Quick Start

**For a complete step-by-step tutorial, see: [Fly.io Deployment Tutorial](./fly-deployment-tutorial.md)**

## Overview

This document explains how the fastopp application is configured for deployment on Fly.io, particularly regarding file uploads and storage.

## Environment-Based Configuration

The application uses environment variables to handle different deployment scenarios:

### Local Development
- **UPLOAD_DIR**: Not set (defaults to `static/uploads`)
- **Storage**: Files stored in local `static/uploads` directory
- **Mounting**: Standard static file serving

### Fly.io Production
- **UPLOAD_DIR**: Set to `/data/uploads`
- **Storage**: Files stored in persistent volume mounted at `/data`
- **Mounting**: Separate mount for uploads at `/static/uploads`

## Configuration Files

### fly.toml
```toml
[env]
  ENVIRONMENT = "production"
  UPLOAD_DIR = "/data/uploads"

[[mounts]]
  source = "data"
  destination = "/data"
```

### Environment Variables
- `UPLOAD_DIR`: Directory for storing uploads (default: `static/uploads`)
- `ENVIRONMENT`: Deployment environment identifier

## How It Works

1. **Conditional Logic**: The application checks `UPLOAD_DIR` environment variable
2. **Default Behavior**: If not set, uses local `static/uploads` directory
3. **Production Override**: If set to `/data/uploads`, creates separate static mount
4. **URL Compatibility**: Uploads are always served at `/static/uploads/photos/` URLs

## Benefits

- **Upstream Compatible**: No hardcoded Fly.io paths in main application
- **Environment Flexible**: Works in local, Docker, and Fly.io deployments
- **Data Persistence**: Uploads survive container restarts and deployments
- **Easy Configuration**: Single environment variable controls behavior

## Testing with oppdemo

The `oppdemo` script will work correctly because:
- It uses relative paths for sample photos (`static/uploads/sample_photos`)
- The application handles the upload directory configuration automatically
- File operations use the environment-based `UPLOAD_DIR` variable

## Adding to Upstream

To make this upstream-friendly, you can:

1. **Add environment variable support** to the main fastopp project
2. **Document the configuration options** in deployment guides
3. **Provide example configurations** for different deployment strategies
4. **Keep the default behavior unchanged** for backward compatibility
