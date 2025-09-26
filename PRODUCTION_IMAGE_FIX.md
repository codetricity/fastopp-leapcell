# Production Image Fix

## Problem
Images are missing in the LeapCell production version because of environment-based static file serving configuration.

## Root Cause
- **Local**: `UPLOAD_DIR` defaults to `"static/uploads"`, files served via general `/static` mount
- **Production**: `UPLOAD_DIR` is set to a different path (e.g., `/tmp/uploads`), but database URLs still point to `/static/uploads/photos/`
- The conditional mounting logic only works when `UPLOAD_DIR != "static/uploads"`

## Root Cause: Ephemeral File Storage

The real issue is that your production setup has:
- **Database (PostgreSQL)**: Persistent, contains photo URLs
- **File Storage (`/tmp/uploads`)**: Ephemeral, gets wiped on each deployment
- **Result**: Database references files that no longer exist

## Solution: Fix Photo Serving with Object Storage Fallback

### The Issue
Your application already has Object Storage integration, but the static file mounting was preventing the custom photo serving endpoint from working.

### What I Fixed
1. **Removed conflicting static file mounting** for `/static/uploads` in production
2. **Added custom photo serving endpoint** that tries local storage first, then Object Storage
3. **Created script to restore sample photos** to Object Storage

### Step 1: Deploy the Updated Code
The updated `main.py` now:
- Serves general static files from `/static`
- Uses custom endpoint `/static/uploads/photos/{filename}` for photos
- Falls back to Object Storage when local files don't exist

### Step 2: Restore Photos from Object Storage
Call the existing restore endpoint:
```bash
curl -X POST https://fastopp-leapcell-craig5992-0c07r9lc.leapcell.dev/api/restore-files
```

### Step 3: Test the Fix
1. Visit `/webinar-demo` - images should now load
2. Check `/debug/settings` to verify configuration
3. Test individual images via `/debug/test-image/{filename}`

## Solution 2: Fix the Conditional Mounting Logic (Alternative)

If you need to keep a different `UPLOAD_DIR` in production, update the mounting logic:

### Update main.py
```python
# Mount uploads directory based on environment (MUST come before /static mount)
if settings.upload_dir != "static/uploads":
    # In production environments, mount the uploads directory separately
    app.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
else:
    # Ensure the uploads directory is accessible via /static
    app.mount("/static", StaticFiles(directory="static"), name="static")
```

## Verification Steps

1. **Check current UPLOAD_DIR in production:**
   ```bash
   # Add this debug endpoint to check current settings
   @app.get("/debug/settings")
   async def debug_settings():
       return {
           "upload_dir": settings.upload_dir,
           "environment": settings.environment
       }
   ```

2. **Test image URLs:**
   - Visit `/webinar-demo` in production
   - Check browser dev tools Network tab for 404 errors on image requests
   - Verify that `/static/uploads/photos/filename.jpg` returns the actual image

3. **Check file existence:**
   ```bash
   # If you have access to production filesystem
   ls -la /path/to/upload/dir/photos/
   ```

## Expected Result
After applying Solution 1, the webinar demo page should show actual profile photos instead of colored circles with initials.
