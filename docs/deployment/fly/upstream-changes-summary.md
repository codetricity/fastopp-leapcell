# Upstream Changes Summary

## Quick Reference: Required Changes

This document summarizes the minimal changes needed to implement environment-based upload configuration in the upstream fastopp project.

## Files to Modify

### 1. `main.py`

**Add import:**
```python
import os
```

**Change upload directory configuration:**
```python
# Before
UPLOAD_DIR = Path("static/uploads")

# After  
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "static/uploads"))
```

**Add conditional mounting:**
```python
# After existing static mount
if os.getenv("UPLOAD_DIR") and os.getenv("UPLOAD_DIR") != "static/uploads":
    app.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
```

### 2. `services/webinar_service.py`

**Add import:**
```python
import os
```

**Change file path:**
```python
# Before
file_path = Path("static/uploads/photos") / unique_filename

# After
file_path = Path(os.getenv("UPLOAD_DIR", "static/uploads")) / "photos" / unique_filename
```

## Environment Variable

### `UPLOAD_DIR`
- **Default**: `"static/uploads"` (maintains backward compatibility)
- **Purpose**: Override upload directory for production deployments
- **Examples**:
  - Local: Not set (uses default)
  - Docker: `/app/uploads`
  - Fly.io: `/data/uploads`
  - Kubernetes: `/persistent/uploads`

## What This Enables

✅ **Local development** works unchanged  
✅ **Docker deployments** with configurable storage  
✅ **Fly.io deployments** with persistent volumes  
✅ **Kubernetes deployments** with flexible storage  
✅ **Other cloud platforms** (Heroku, ECS, Cloud Run)  

## Backward Compatibility

- **No breaking changes** to existing functionality
- **Default behavior** identical to current implementation
- **URL paths** remain the same (`/static/uploads/photos/`)
- **API endpoints** unchanged
- **Database schema** unchanged

## Testing

1. **Local**: Run without environment variables
2. **Production**: Set `UPLOAD_DIR` and test file uploads
3. **Verify**: Files are stored in correct location and served correctly

## Deployment Examples

### Local Development
```bash
python main.py  # No changes needed
```

### Docker
```bash
docker run -e UPLOAD_DIR=/app/uploads your-app
```

### Fly.io
```toml
[env]
  UPLOAD_DIR = "/data/uploads"
```

### Kubernetes
```yaml
env:
  - name: UPLOAD_DIR
    value: "/persistent/uploads"
```

## Summary

**Total changes**: 3 files, ~10 lines of code  
**Impact**: Minimal, backward-compatible  
**Benefit**: Deploy anywhere without code changes  
**Maintenance**: Single configuration point
