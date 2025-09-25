# Files Moved to to_be_deleted

This folder contains documentation files that have been consolidated into other documents or are no longer needed.

## Why These Files Were Moved

As part of the documentation consolidation effort, we've reduced the docs folder from 22 files to 8 main documentation files. The files in this folder were either:

1. **Consolidated** - Content merged into comprehensive guides
2. **Outdated** - Information that's no longer current
3. **Temporary** - Historical notes that don't need to be in main docs
4. **Redundant** - Information duplicated in multiple files

## Files Moved and Their Status

### Consolidated Files

| File | Status | Merged Into |
|------|--------|-------------|
| `REFACTORING_SUMMARY.md` | ✅ Consolidated | `DEVELOPMENT.md` |
| `ALEMBIC_CONFIGURATION_CHANGES.md` | ✅ Consolidated | `deployment/FLY_DEPLOYMENT.md` |
| `basic_add_new_page.md` | ✅ Consolidated | `DEVELOPMENT.md` |
| `streaming_chat.md` | ✅ Consolidated | `FEATURES.md` |
| `postgresql_install.md` | ✅ Consolidated | `deployment/POSTGRESQL_SETUP.md` |
| `production_vs_development.md` | ✅ Consolidated | `deployment/POSTGRESQL_SETUP.md` |
| `database_loading_problems.md` | ✅ Consolidated | `DATABASE.md` |
| `MIGRATION_GUIDE.md` | ✅ Consolidated | `DATABASE.md` |
| `file_upload.md` | ✅ Consolidated | `FEATURES.md` |
| `image_storage.md` | ✅ Consolidated | `FEATURES.md` |
| `AUTH_ARCHITECTURE.md` | ✅ Consolidated | `AUTHENTICATION.md` |
| `oppkey_development_plans.md` | ✅ Consolidated | `plan/ROADMAP.md` |
| `timeline.md` | ✅ Consolidated | `plan/ROADMAP.md` |
| `call_for_students.md` | ✅ Consolidated | `plan/ROADMAP.md` |
| `demo/prompts.txt` | ✅ Consolidated | `FEATURES.md` |

### New Consolidated Structure

The documentation has been reorganized into these main files:

1. **`deployment/POSTGRESQL_SETUP.md`** - PostgreSQL setup, database configuration, environment variables
2. **`deployment/FLY_DEPLOYMENT.md`** - Fly.io deployment, server setup, troubleshooting
3. **`DATABASE.md`** - Database management, migrations, troubleshooting, best practices
4. **`AUTHENTICATION.md`** - Complete authentication system overview and implementation
5. **`FEATURES.md`** - Application features, file management, AI chat, admin interface
6. **`DEVELOPMENT.md`** - Development workflow, adding new pages, testing, debugging
7. **`plan/ROADMAP.md`** - Development timeline, student recruitment, project planning
8. **`ARCHITECTURE.md`** - System architecture overview (kept as-is)

## Benefits of Consolidation

- **Reduced file count** from 22 to 8 main documentation files
- **Better navigation** for developers
- **Eliminated duplication** of information
- **Cleaner structure** with logical groupings
- **Easier maintenance** of documentation

## What to Do with These Files

These files are kept for reference but should not be updated. If you need to:

- **Find information**: Check the new consolidated files first
- **Update content**: Edit the appropriate consolidated file
- **Add new content**: Add to the relevant consolidated file
- **Reference old content**: Use these files as historical reference

## Migration Notes

- All cross-references have been updated to point to new consolidated files
- Content has been preserved and reorganized for better readability
- Examples and code snippets have been updated where necessary
- Links between documents have been maintained

For questions about the new documentation structure, see the main `README.md` in the docs folder.
