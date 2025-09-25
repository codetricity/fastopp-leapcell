# HTTPS Setup for Production Deployments

## Environment Variables

To enable the HTTPS fix for SQLAdmin in production, set one of these environment variables:

```bash
# Railway
RAILWAY_ENVIRONMENT=production

# Generic production
PRODUCTION=true

# Environment identifier (existing pattern in codebase)
ENVIRONMENT=production

# Force HTTPS mode
FORCE_HTTPS=true
```

## How It Works

1. **Production Detection**: The admin setup automatically detects production environments
2. **HTTPS Configuration**: When in production, SQLAdmin is configured with HTTPS-safe settings
3. **Proxy Headers**: Middleware handles proxy headers to detect HTTPS requests
4. **Mixed Content Prevention**: Logo and other assets are configured to avoid mixed content issues

## Deployment Checklist

- [ ] Set one of the production environment variables
- [ ] Ensure your deployment platform serves over HTTPS
- [ ] Verify admin interface loads without mixed content errors
- [ ] Check that all CSS/JS files load over HTTPS

## Testing

After deployment, access your admin interface at `/admin` and check:

1. Browser console for mixed content errors
2. Network tab to verify all assets load over HTTPS
3. Admin interface renders with proper styling
