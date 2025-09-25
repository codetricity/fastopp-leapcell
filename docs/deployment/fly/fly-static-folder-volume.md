# Fly Deploy Static Structure

Problem: losing access to webinar attendee photos when restarting the Fly server.

## Problem Analysis

**Yes, you are losing the photos on Fly machine restart, and yes, you need to put the static uploads on a Fly volume.**

### Root Cause

The issue is that **photos are stored in the ephemeral filesystem** of the Fly machine. Here's what's happening:

1. **Photo Storage Location**: Photos are stored in `static/uploads/photos/` directory
2. **Ephemeral Storage**: This directory is part of the container's filesystem, which is **ephemeral** - it gets wiped when the machine restarts
3. **Volume Mount**: Your `fly.toml` only mounts a volume at `/data` for the SQLite database, but **not for the static uploads**

### Current Configuration

Looking at your `fly.toml`:

```toml
[[mounts]]
  source = "data"
  destination = "/data"
```

This only persists the database at `/data`, but your photos are stored in the application directory at `static/uploads/photos/`.

### The Solution

You need to **add a second volume mount** for the static uploads directory. Here's how to fix it:

#### 1. Create a new volume for static uploads

```bash
fly volumes create static-uploads --region sjc --size 1
```

#### 2. Update your `fly.toml` to mount the static uploads volume

Add this to your `fly.toml`:

```toml
[[mounts]]
  source = "data"
  destination = "/data"

[[mounts]]
  source = "static-uploads"
  destination = "/app/static/uploads"
```

#### 3. Update the application code to ensure upload directories exist

The application already creates upload directories in `main.py`, but you should ensure this happens at startup. The current code in `main.py` lines 28-32 does this:

```python
# Create upload directories
UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
PHOTOS_DIR = UPLOAD_DIR / "photos"
PHOTOS_DIR.mkdir(exist_ok=True)
```

#### 4. Redeploy and reinitialize

After making these changes:

```bash
fly deploy
fly ssh console -C "uv run python oppman.py init"
```

### Alternative Approach (Recommended)

Instead of mounting the entire `static/uploads` directory, you could mount just the `photos` subdirectory:

```toml
[[mounts]]
  source = "data"
  destination = "/data"

[[mounts]]
  source = "static-uploads"
  destination = "/app/static/uploads/photos"
```

This approach is cleaner because:
- It only persists the user-uploaded photos
- Keeps the sample photos in the container (they can be re-downloaded)
- Reduces volume size requirements

### Why This Happens

1. **Container Ephemeral Storage**: Fly machines use ephemeral storage for the application filesystem
2. **Volume Persistence**: Only data in mounted volumes persists across restarts
3. **Current Setup**: Your photos are stored in the ephemeral filesystem, not in a persistent volume

### Verification

After implementing the fix, you can verify it works by:

1. Uploading a photo
2. Restarting the machine: `fly machine restart <machine-id>`
3. Checking that the photo is still accessible

The photos should now persist across machine restarts because they'll be stored in the persistent Fly volume instead of the ephemeral container filesystem.
