# Alembic Versions Directory

This directory contains Alembic database migration files. These files are generated when you create new migrations using the Alembic CLI.

## Important Notes

- **Do not commit migration files to Git**: Migration files should be generated locally and applied to your database, but not committed to version control.
- **Deployment requirement**: This directory must exist for Alembic to work properly in production deployments (e.g., on Fly.io).
- **The `.gitkeep` file**: This file ensures the directory is tracked in Git even when empty.

## Migration Workflow

1. **Create a migration**:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

2. **Apply migrations locally**:
   ```bash
   alembic upgrade head
   ```

3. **Deploy to production**: The migration files will be generated on the production server when needed.

## Deployment Considerations

- On Fly.io and other deployment platforms, this directory must exist for Alembic to function
- Migration files are generated dynamically during deployment
- The `.gitkeep` file ensures the directory structure is preserved across deployments

## Backup Strategy

- Migration files are backed up in `versions_backup_YYYYMMDD_HHMMSS/` directories
- These backups contain the actual migration files for reference
- The backup directories are not committed to Git
