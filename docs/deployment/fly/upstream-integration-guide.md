# Upstream Integration Guide: Environment-Based Upload Configuration

## Overview

This guide documents the changes needed to integrate environment-based upload configuration into the upstream fastopp project. This approach allows the application to work seamlessly across different deployment environments without hardcoded paths.

## Problem Statement

The original implementation hardcoded upload paths, making it difficult to deploy in different environments:
- **Local development**: Uses `static/uploads/`
- **Docker**: Needs configurable paths
- **Fly.io**: Requires persistent volume mounts
- **Kubernetes**: Needs flexible storage configuration

## Solution: Environment-Based Configuration

Use environment variables to control upload directory behavior while maintaining backward compatibility.

## Required Changes

### 1. Update `main.py`

#### Before
```python
# Create upload directories
UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
PHOTOS_DIR = UPLOAD_DIR / "photos"
PHOTOS_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
```

#### After
```python
import os

# Create upload directories
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "static/uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)
PHOTOS_DIR = UPLOAD_DIR / "photos"
PHOTOS_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount uploads directory based on environment
if os.getenv("UPLOAD_DIR") and os.getenv("UPLOAD_DIR") != "static/uploads":
    # In production environments, mount the uploads directory separately
    app.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
```

### 2. Update `services/webinar_service.py`

#### Before
```python
file_path = Path("static/uploads/photos") / unique_filename
```

#### After
```python
import os

file_path = Path(os.getenv("UPLOAD_DIR", "static/uploads")) / "photos" / unique_filename
```

### 3. Add Required Import

Ensure `os` is imported in files that use environment variables:
```python
import os
```

## Environment Variable Reference

### `UPLOAD_DIR`

**Purpose**: Controls where uploaded files are stored and served from

**Default Value**: `"static/uploads"` (maintains backward compatibility)

**Usage**: Set to override the default upload directory for production deployments

## Deployment Configurations

### 1. Local Development

**Configuration**: No environment variables set
**Behavior**: 
- Files stored in `static/uploads/`
- Standard static file serving
- No additional mounts

**Example**:
```bash
# No environment variables needed
python main.py
```

### 2. Docker Development

**Configuration**: 
```bash
UPLOAD_DIR=/app/uploads
```

**Behavior**:
- Files stored in `/app/uploads/`
- Separate mount for uploads at `/static/uploads`
- Container-relative paths

**Dockerfile Example**:
```dockerfile
ENV UPLOAD_DIR=/app/uploads
VOLUME /app/uploads
```

**docker-compose.yml Example**:
```yaml
environment:
  - UPLOAD_DIR=/app/uploads
volumes:
  - ./uploads:/app/uploads
```

### 3. Fly.io Production

**Configuration**:
```toml
[env]
  UPLOAD_DIR = "/data/uploads"

[[mounts]]
  source = "data"
  destination = "/data"
```

**Behavior**:
- Files stored in persistent volume at `/data/uploads/`
- Separate mount for uploads at `/static/uploads`
- Data survives container restarts and deployments

**Volume Creation**:
```bash
fly volumes create data --size 1 --region sjc
```

### 4. Kubernetes Production

**Configuration**:
```yaml
env:
  - name: UPLOAD_DIR
    value: "/persistent/uploads"
volumeMounts:
  - name: uploads-storage
    mountPath: /persistent/uploads
volumes:
  - name: uploads-storage
    persistentVolumeClaim:
      claimName: uploads-pvc
```

**Behavior**:
- Files stored in Kubernetes persistent volume
- Separate mount for uploads at `/static/uploads`
- Cluster-wide data persistence

### 5. Heroku

**Configuration**:
```bash
heroku config:set UPLOAD_DIR=/app/uploads
```

**Behavior**:
- Files stored in `/app/uploads/`
- **Note**: Heroku has ephemeral filesystem, consider using S3 or similar

### 6. AWS ECS/Fargate

**Configuration**:
```json
{
  "environment": [
    {
      "name": "UPLOAD_DIR",
      "value": "/efs/uploads"
    }
  ],
  "mountPoints": [
    {
      "sourceVolume": "efs-storage",
      "containerPath": "/efs/uploads",
      "readOnly": false
    }
  ]
}
```

**Behavior**:
- Files stored in EFS (Elastic File System)
- Persistent across container restarts
- Multi-AZ availability

### 7. Google Cloud Run

**Configuration**:
```bash
gcloud run deploy --set-env-vars UPLOAD_DIR=/tmp/uploads
```

**Behavior**:
- Files stored in `/tmp/uploads/`
- **Note**: Cloud Run has ephemeral filesystem, consider using Cloud Storage

## Implementation Checklist

### Core Changes
- [ ] Update `main.py` with environment-based `UPLOAD_DIR`
- [ ] Add conditional static file mounting
- [ ] Update `services/webinar_service.py` to use environment variable
- [ ] Add `import os` where needed

### Testing
- [ ] Test local development (no env vars)
- [ ] Test with `UPLOAD_DIR` set to different values
- [ ] Verify file uploads work in all configurations
- [ ] Verify static file serving works correctly

### Documentation
- [ ] Update deployment guides
- [ ] Add environment variable reference
- [ ] Document each deployment option
- [ ] Provide configuration examples

## Backward Compatibility

### What Stays the Same
- **URL paths**: All uploads still served at `/static/uploads/photos/`
- **API endpoints**: No changes to existing endpoints
- **Database schema**: No changes to data models
- **Default behavior**: Local development works unchanged

### What Changes
- **File storage location**: Configurable via environment variable
- **Static file mounting**: Conditional based on environment
- **File operations**: Use environment-based paths

## Migration Guide

### For Existing Deployments
1. **No immediate changes required** - default behavior preserved
2. **Optional**: Set `UPLOAD_DIR` environment variable for production
3. **Gradual rollout**: Can be deployed alongside existing versions

### For New Deployments
1. **Set `UPLOAD_DIR`** based on deployment environment
2. **Configure storage volumes** as needed
3. **Test file uploads** in target environment

## Troubleshooting

### Common Issues

#### Files Not Uploading
- Check `UPLOAD_DIR` environment variable is set correctly
- Verify directory exists and is writable
- Check application logs for permission errors

#### Files Not Serving
- Verify static file mounting is configured correctly
- Check that uploads directory is accessible
- Ensure URL paths match mounted directories

#### Permission Errors
- Check file system permissions on upload directory
- Verify container user has write access
- Check volume mount permissions

### Debug Commands

```bash
# Check environment variable
echo $UPLOAD_DIR

# Verify directory exists
ls -la $UPLOAD_DIR

# Check file permissions
ls -la $UPLOAD_DIR/photos/

# Test file creation
touch $UPLOAD_DIR/test.txt
```

## Performance Considerations

### Local Development
- **Pros**: Fast file I/O, simple setup
- **Cons**: No persistence, limited scalability

### Production Deployments
- **Pros**: Data persistence, scalable storage
- **Cons**: Network latency, storage costs

### Recommendations
- Use local storage for development
- Use persistent volumes for production
- Consider CDN for high-traffic applications
- Monitor storage usage and costs

## Security Considerations

### File Upload Security
- Validate file types and sizes
- Scan for malware in production
- Implement proper authentication
- Use secure file permissions

### Storage Security
- Encrypt volumes in production
- Use IAM roles for cloud storage
- Implement access logging
- Regular security audits

## Future Enhancements

### Potential Improvements
1. **Multiple storage backends**: S3, GCS, Azure Blob
2. **CDN integration**: CloudFront, Cloud CDN
3. **Image processing**: Thumbnails, resizing
4. **File versioning**: Keep multiple versions
5. **Backup strategies**: Automated backups

### Configuration Extensions
```python
# Future: Multiple storage backends
STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")
STORAGE_CONFIG = {
    "local": {"path": os.getenv("UPLOAD_DIR", "static/uploads")},
    "s3": {"bucket": os.getenv("S3_BUCKET"), "region": os.getenv("AWS_REGION")},
    "gcs": {"bucket": os.getenv("GCS_BUCKET")}
}
```

## Conclusion

This environment-based approach provides:
- **Flexibility**: Works in any deployment environment
- **Compatibility**: Maintains backward compatibility
- **Maintainability**: Single configuration point
- **Scalability**: Easy to extend for future needs

The implementation is minimal and focused, making it easy to integrate into the upstream project while providing significant deployment flexibility.
