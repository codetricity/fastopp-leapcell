# LeapCell Support for FastOpp

## Overview

This document outlines the features and modifications needed to add comprehensive LeapCell support to the upstream FastOpp project. LeapCell is a serverless platform that offers PostgreSQL databases, Object Storage, and async task processing.

## Current Status

FastOpp currently supports:
- ✅ Local development with SQLite
- ✅ Fly.io deployment with persistent volumes
- ✅ Basic serverless deployments

**Missing**: Native LeapCell support with platform-specific optimizations.

## Required Features

### 1. Database Configuration

#### 1.1 PostgreSQL Support
- **Current**: SQLite-only with optional PostgreSQL
- **Needed**: Default PostgreSQL configuration for LeapCell
- **Implementation**:
  ```python
  # Add to dependencies/config.py
  class Settings(BaseSettings):
      database_url: str = "sqlite+aiosqlite:///./test.db"
      
      # LeapCell-specific defaults
      @property
      def leapcell_database_url(self) -> str:
          if self.environment == "leapcell":
              return os.getenv("DATABASE_URL", "postgresql+asyncpg://...")
          return self.database_url
  ```

#### 1.2 Environment Detection
- **Feature**: Auto-detect LeapCell environment
- **Implementation**:
  ```python
  def detect_platform():
      if os.getenv("LEAPCELL_APP_NAME"):
          return "leapcell"
      elif os.getenv("FLY_APP_NAME"):
          return "fly"
      else:
          return "local"
  ```

### 2. File Storage Configuration

#### 2.1 Upload Directory Management
- **Current**: Hardcoded `static/uploads`
- **Needed**: Environment-aware upload directories
- **Implementation**:
  ```python
  # Update oppdemo.py and all scripts
  def get_upload_dir():
      return os.getenv("UPLOAD_DIR", "static/uploads")
  ```

#### 2.2 Object Storage Integration (Optional)
- **Feature**: Optional LeapCell Object Storage for file persistence
- **Implementation**:
  ```python
  # Add to dependencies/storage.py
  class LeapCellStorage:
      def __init__(self):
          self.s3_client = boto3.client(
              "s3",
              endpoint_url="https://objstorage.leapcell.io",
              aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
              aws_secret_access_key=os.getenv("S3_SECRET_KEY")
          )
      
      async def backup_files(self, local_path: str):
          # Backup files to Object Storage
          pass
      
      async def restore_files(self, local_path: str):
          # Restore files from Object Storage
          pass
  ```

#### 2.3 File Backup and Restore Endpoints
- **Feature**: HTTP endpoints for file backup/restore operations
- **Implementation**:
  ```python
  @app.post("/admin/backup-files")
  async def backup_files():
      """Backup uploaded files to LeapCell Object Storage"""
      # Uploads all files from /tmp/uploads to Object Storage
      # Preserves directory structure
      # Returns count of files backed up
  
  @app.post("/admin/restore-files")
  async def restore_files():
      """Restore uploaded files from LeapCell Object Storage"""
      # Downloads all files from Object Storage to /tmp/uploads
      # Recreates directory structure
      # Returns count of files restored
  ```

### 3. Async Task Processing

#### 3.1 LeapCell Async Triggers
- **Feature**: Native support for LeapCell's async task system
- **Implementation**:
  ```python
  # Add to routes/async.py
  @app.post("/async/init-demo")
  async def init_demo_async():
      """Initialize demo data using LeapCell's async task system"""
      try:
          from oppdemo import run_full_init
          await run_full_init()
          return {"status": "success", "message": "Demo initialization complete"}
      except Exception as e:
          return {"status": "error", "message": str(e)}
  ```

#### 3.2 Background Task Management
- **Feature**: Queue management for long-running tasks
- **Implementation**:
  ```python
  # Add to services/task_service.py
  class TaskService:
      async def queue_init_task(self):
          # Queue initialization task
          pass
      
      async def queue_backup_task(self):
          # Queue backup task
          pass
  ```

### 4. Platform-Specific Configuration

#### 4.1 LeapCell Detection
- **Feature**: Auto-detect LeapCell environment
- **Implementation**:
  ```python
  # Add to dependencies/platform.py
  class PlatformDetector:
      @staticmethod
      def is_leapcell() -> bool:
          return bool(os.getenv("LEAPCELL_APP_NAME"))
      
      @staticmethod
      def get_platform_config():
          if PlatformDetector.is_leapcell():
              return {
                  "database_url": os.getenv("DATABASE_URL"),
                  "upload_dir": os.getenv("UPLOAD_DIR", "/tmp/uploads"),
                  "use_object_storage": bool(os.getenv("S3_ACCESS_KEY"))
              }
  ```

#### 4.2 Environment Variables
- **Required Variables**:
  ```bash
  DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
  UPLOAD_DIR=/tmp/uploads
  S3_ACCESS_KEY=your_access_key  # Optional
  S3_SECRET_KEY=your_secret_key   # Optional
  ```

### 5. Database Migration Support

#### 5.1 Alembic Configuration
- **Feature**: Platform-aware migration paths
- **Implementation**:
  ```python
  # Update alembic/env.py
  def get_database_url():
      if os.getenv("LEAPCELL_APP_NAME"):
          return os.getenv("DATABASE_URL")
      return "sqlite+aiosqlite:///./test.db"
  ```

#### 5.2 Migration Commands
- **Feature**: LeapCell-specific migration commands
- **Implementation**:
  ```python
  # Add to oppman.py
  def migrate_leapcell():
      """Run migrations for LeapCell deployment"""
      # Platform-specific migration logic
      pass
  ```

### 6. Debug and Monitoring

#### 6.1 Platform-Specific Debug Endpoints
- **Feature**: Debug endpoints for LeapCell
- **Implementation**:
  ```python
  @app.get("/debug/leapcell")
  async def debug_leapcell():
      """Debug LeapCell-specific configuration"""
      return {
          "platform": "leapcell",
          "database_url": settings.database_url,
          "upload_dir": settings.upload_dir,
          "object_storage_enabled": bool(os.getenv("S3_ACCESS_KEY"))
      }
  ```

#### 6.2 Health Checks
- **Feature**: LeapCell-aware health checks
- **Implementation**:
  ```python
  @app.get("/health")
  async def health_check():
      """Platform-aware health check"""
      if PlatformDetector.is_leapcell():
          # Check PostgreSQL connection
          # Check Object Storage (if enabled)
          pass
      return {"status": "healthy"}
  ```

### 7. Documentation Updates

#### 7.1 Deployment Guide
- **Feature**: LeapCell deployment documentation
- **Content**:
  - Environment variable setup
  - Database configuration
  - File storage options
  - Async task usage

#### 7.2 Platform Comparison
- **Feature**: Compare platforms (Local, Fly.io, LeapCell)
- **Content**:
  - Feature matrix
  - Performance characteristics
  - Cost analysis
  - Use case recommendations

## LeapCell-Specific Endpoints

### Core Endpoints
| Endpoint | Method | Description | Purpose |
|----------|--------|-------------|---------|
| `/async/init-demo` | POST | Initialize demo data | Run `oppdemo.py init` via async trigger |
| `/debug/database-data` | GET | Check database contents | Verify tables and data exist |
| `/debug/database` | GET | Database configuration | Check database settings and permissions |
| `/debug/simple` | GET | Simple health check | Test if app is working |

### File Management Endpoints
| Endpoint | Method | Description | Purpose |
|----------|--------|-------------|---------|
| `/admin/backup-files` | POST | Backup files to Object Storage | Upload all files from `/tmp/uploads` to Object Storage |
| `/admin/restore-files` | POST | Restore files from Object Storage | Download all files from Object Storage to `/tmp/uploads` |

### Usage Examples
```bash
# Initialize demo data
curl -X POST https://your-app.leapcell.dev/async/init-demo

# Check database contents
curl https://your-app.leapcell.dev/debug/database-data

# Backup files to Object Storage
curl -X POST https://your-app.leapcell.dev/admin/backup-files

# Restore files from Object Storage
curl -X POST https://your-app.leapcell.dev/admin/restore-files
```

### Workflow
1. **Initial Setup**: Run `/async/init-demo` to create database and sample data
2. **Backup Files**: Run `/admin/backup-files` to save uploaded files to Object Storage
3. **After Restart**: Run `/admin/restore-files` to restore files from Object Storage
4. **Verification**: Use `/debug/database-data` to verify data exists

## Implementation Priority

### Phase 1: Core Support
1. ✅ PostgreSQL configuration
2. ✅ Environment detection
3. ✅ Upload directory management
4. ✅ Async task endpoints
5. ✅ File backup/restore endpoints

### Phase 2: Enhanced Features
1. Object Storage integration
2. Advanced task management
3. Platform-specific optimizations
4. Monitoring and debugging

### Phase 3: Documentation
1. Deployment guides
2. Platform comparison
3. Best practices
4. Troubleshooting guides

## Testing Requirements

### Unit Tests
- Platform detection
- Configuration loading
- Database connections
- File operations

### Integration Tests
- End-to-end deployment
- Async task processing
- Object Storage operations
- Migration testing

### Performance Tests
- Database performance
- File upload/download
- Async task throughput
- Memory usage

## Backward Compatibility

### Existing Deployments
- ✅ Local development unchanged
- ✅ Fly.io deployments unchanged
- ✅ SQLite support maintained
- ✅ Existing environment variables respected

### Migration Path
- Gradual adoption of new features
- Optional LeapCell-specific optimizations
- Fallback to existing behavior

## Security Considerations

### Environment Variables
- Secure credential management
- Platform-specific secrets
- Access control for Object Storage

### Database Security
- SSL/TLS requirements
- Connection pooling
- Query optimization

### File Storage Security
- Access control
- Encryption at rest
- Secure file uploads

## Performance Optimizations

### Database
- Connection pooling for PostgreSQL
- Query optimization
- Index management

### File Storage
- Efficient Object Storage usage
- Local caching strategies
- CDN integration

### Async Tasks
- Task queuing optimization
- Resource management
- Error handling and retries

## Monitoring and Observability

### Metrics
- Database performance
- File storage usage
- Async task metrics
- Platform-specific metrics

### Logging
- Structured logging
- Platform-aware log levels
- Error tracking
- Performance monitoring

### Alerting
- Health check failures
- Resource usage alerts
- Error rate monitoring
- Performance degradation

## Future Enhancements

### Advanced Features
- Multi-region support
- Auto-scaling configuration
- Advanced caching strategies
- Real-time monitoring

### Integration
- CI/CD pipeline support
- Automated testing
- Deployment automation
- Configuration management

## Conclusion

Adding LeapCell support to FastOpp will provide users with a modern serverless deployment option that offers:

- **Persistent PostgreSQL databases**
- **Object Storage for files**
- **Async task processing**
- **Cost-effective scaling**
- **Easy deployment**

The implementation should be backward-compatible while providing new capabilities for LeapCell users.
