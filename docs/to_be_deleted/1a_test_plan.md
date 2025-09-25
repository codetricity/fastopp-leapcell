# Phase 1A Testing Plan - Dependency Injection Foundation

**Date**: September 18, 2025  
**Phase**: 1A - Foundation & Quick Wins  
**Status**: Ready for Testing

## Overview

This test plan validates that Phase 1A dependency injection changes are working correctly. The tests cover the core functionality without requiring the full demo application to be running.

## Prerequisites

- Python environment with `uv` package manager
- All Phase 1A changes implemented
- Database initialized (if testing database functionality)

## Test Categories

### 1. Configuration System Tests

#### 1.1 Basic Configuration Loading
**Purpose**: Verify the new configuration system works

**Test Steps**:
```bash
# Test 1: Basic configuration loading
uv run python -c "
from dependencies.config import get_settings
settings = get_settings()
print(f'Database URL: {settings.database_url}')
print(f'Environment: {settings.environment}')
print(f'Secret Key: {settings.secret_key[:10]}...')
print('✅ Configuration loading works')
"
```

**Expected Result**: 
- No errors
- Database URL shows `sqlite+aiosqlite:///./test.db`
- Environment shows `development`
- Secret key shows first 10 characters

#### 1.2 Environment Variable Override
**Purpose**: Verify environment variables override defaults

**Test Steps**:
```bash
# Test 2: Environment variable override
export DATABASE_URL="sqlite+aiosqlite:///./test_override.db"
export ENVIRONMENT="testing"

uv run python -c "
from dependencies.config import get_settings
settings = get_settings()
print(f'Database URL: {settings.database_url}')
print(f'Environment: {settings.environment}')
assert settings.database_url == 'sqlite+aiosqlite:///./test_override.db'
assert settings.environment == 'testing'
print('✅ Environment variable override works')
"
```

**Expected Result**: 
- Database URL shows the overridden value
- Environment shows `testing`
- No assertion errors

### 2. Database Dependency Tests

#### 2.1 Database Engine Creation
**Purpose**: Verify database engine can be created with dependency injection

**Test Steps**:
```bash
# Test 3: Database engine creation
uv run python -c "
from dependencies.database import create_database_engine
from dependencies.config import get_settings

settings = get_settings()
engine = create_database_engine(settings)
print(f'Engine created: {type(engine)}')
print(f'Engine URL: {engine.url}')
print('✅ Database engine creation works')
"
```

**Expected Result**: 
- No errors
- Engine type shows SQLAlchemy engine
- Engine URL matches configuration

#### 2.2 Session Factory Creation
**Purpose**: Verify session factory can be created

**Test Steps**:
```bash
# Test 4: Session factory creation
uv run python -c "
from dependencies.database import create_session_factory, create_database_engine
from dependencies.config import get_settings

settings = get_settings()
engine = create_database_engine(settings)
session_factory = create_session_factory(engine)
print(f'Session factory created: {type(session_factory)}')
print('✅ Session factory creation works')
"
```

**Expected Result**: 
- No errors
- Session factory type shows async sessionmaker

### 3. Service Dependency Tests

#### 3.1 ProductService Dependency Injection
**Purpose**: Verify ProductService can be created with dependency injection

**Test Steps**:
```bash
# Test 5: ProductService dependency injection
uv run python -c "
from dependencies.services import get_product_service
from dependencies.database import create_database_engine, create_session_factory
from dependencies.config import get_settings

# Create dependencies manually for testing
settings = get_settings()
engine = create_database_engine(settings)
session_factory = create_session_factory(engine)

# Test the dependency function
product_service = get_product_service(session_factory(), settings)
print(f'ProductService created: {type(product_service)}')
print(f'Has session: {hasattr(product_service, \"session\")}')
print(f'Has settings: {hasattr(product_service, \"settings\")}')
print('✅ ProductService dependency injection works')
"
```

**Expected Result**: 
- No errors
- ProductService instance created
- Has `session` and `settings` attributes

### 4. Application Integration Tests

#### 4.1 Application Startup
**Purpose**: Verify the application starts without errors

**Test Steps**:
```bash
# Test 6: Application startup
uv run python -c "
from main import app
print(f'App created: {type(app)}')
print(f'App title: {app.title}')
print('✅ Application startup works')
"
```

**Expected Result**: 
- No errors
- FastAPI app instance created
- App title shows correctly

#### 4.2 Dependency Setup
**Purpose**: Verify dependency setup is working

**Test Steps**:
```bash
# Test 7: Dependency setup verification
uv run python -c "
from main import app
print(f'App state has db_engine: {hasattr(app.state, \"db_engine\")}')
print(f'App state has session_factory: {hasattr(app.state, \"session_factory\")}')
print(f'App state has settings: {hasattr(app.state, \"settings\")}')
print('✅ Dependency setup works')
"
```

**Expected Result**: 
- All three state attributes exist
- No errors

### 5. API Endpoint Tests

#### 5.1 Products Endpoint with Dependency Injection
**Purpose**: Verify the `/api/products` endpoint works with dependency injection

**Test Steps**:
```bash
# Test 8: Products endpoint with DI
uv run python -c "
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)
response = client.get('/api/products')
print(f'Status Code: {response.status_code}')
print(f'Response Type: {type(response.json())}')

if response.status_code == 200:
    data = response.json()
    print(f'Products Count: {len(data.get(\"products\", []))}')
    print(f'Has Stats: {\"stats\" in data}')
    print('✅ Products endpoint with DI works')
else:
    print(f'Error: {response.text}')
"
```

**Expected Result**: 
- Status code 200
- Response contains products array
- Response contains stats object
- No errors

### 6. State Management Tests

#### 6.1 Demo Save Functionality
**Purpose**: Verify `oppdemo.py save` includes dependencies

**Test Steps**:
```bash
# Test 9: Demo save includes dependencies
uv run python oppdemo.py save

# Verify dependencies were saved
ls -la demo_assets/dependencies/
echo "✅ Dependencies saved to demo_assets"
```

**Expected Result**: 
- `demo_assets/dependencies/` directory exists
- Contains `config.py`, `database.py`, `services.py`
- No errors during save

#### 6.2 Demo Restore Functionality
**Purpose**: Verify `oppdemo.py restore` restores dependencies

**Test Steps**:
```bash
# Test 10: Demo restore includes dependencies
# First, remove dependencies to test restore
rm -rf dependencies/

# Restore from demo_assets
uv run python oppdemo.py restore

# Verify dependencies were restored
ls -la dependencies/
echo "✅ Dependencies restored from demo_assets"
```

**Expected Result**: 
- `dependencies/` directory restored
- Contains all dependency files
- No errors during restore

#### 6.3 Demo Destroy Functionality
**Purpose**: Verify `oppdemo.py destroy` removes dependencies

**Test Steps**:
```bash
# Test 11: Demo destroy removes dependencies
uv run python oppdemo.py destroy

# Verify dependencies were removed
if [ ! -d "dependencies" ]; then
    echo "✅ Dependencies removed during destroy"
else
    echo "❌ Dependencies still exist after destroy"
fi
```

**Expected Result**: 
- `dependencies/` directory removed
- No errors during destroy

### 7. Error Handling Tests

#### 7.1 Missing Dependencies
**Purpose**: Verify graceful handling of missing dependencies

**Test Steps**:
```bash
# Test 12: Missing dependencies handling
uv run python -c "
try:
    from dependencies.services import get_product_service
    # This should work if dependencies exist
    print('✅ Dependencies import works')
except ImportError as e:
    print(f'❌ Import error: {e}')
"
```

**Expected Result**: 
- No import errors
- Dependencies can be imported

#### 7.2 Database Connection Errors
**Purpose**: Verify database connection error handling

**Test Steps**:
```bash
# Test 13: Database connection error handling
uv run python -c "
from dependencies.database import create_database_engine
from dependencies.config import Settings

# Test with invalid database URL
invalid_settings = Settings(database_url='invalid://url')
try:
    engine = create_database_engine(invalid_settings)
    print('❌ Should have failed with invalid URL')
except Exception as e:
    print(f'✅ Database error handling works: {type(e).__name__}')
"
```

**Expected Result**: 
- Appropriate error handling
- No application crash

## Test Execution Summary

### Quick Test Suite
Run all tests in sequence:

```bash
#!/bin/bash
echo "🧪 Running Phase 1A Test Suite..."

# Configuration tests
echo "1. Testing configuration system..."
uv run python -c "from dependencies.config import get_settings; settings = get_settings(); print('✅ Config works')"

# Database tests  
echo "2. Testing database dependencies..."
uv run python -c "from dependencies.database import create_database_engine, create_session_factory; from dependencies.config import get_settings; settings = get_settings(); engine = create_database_engine(settings); session_factory = create_session_factory(engine); print('✅ Database DI works')"

# Service tests
echo "3. Testing service dependencies..."
uv run python -c "from dependencies.services import get_product_service; print('✅ Service DI works')"

# Application tests
echo "4. Testing application startup..."
uv run python -c "from main import app; print('✅ App startup works')"

# API tests
echo "5. Testing API endpoint..."
uv run python -c "from main import app; from fastapi.testclient import TestClient; client = TestClient(app); response = client.get('/api/products'); print(f'✅ API works: {response.status_code}')"

echo "🎉 All Phase 1A tests completed!"
```

### Manual Verification Checklist

- [ ] Configuration system loads without errors
- [ ] Environment variables override defaults
- [ ] Database engine creates successfully
- [ ] Session factory creates successfully
- [ ] ProductService creates with dependency injection
- [ ] Application starts without errors
- [ ] Dependency setup stores state correctly
- [ ] `/api/products` endpoint returns 200 status
- [ ] `oppdemo.py save` includes dependencies
- [ ] `oppdemo.py restore` restores dependencies
- [ ] `oppdemo.py destroy` removes dependencies
- [ ] Error handling works gracefully

## Success Criteria

**Phase 1A is considered successful if**:

1. ✅ All configuration tests pass
2. ✅ All database dependency tests pass
3. ✅ All service dependency tests pass
4. ✅ Application starts without errors
5. ✅ API endpoint works with dependency injection
6. ✅ State management (save/restore/destroy) works correctly
7. ✅ No breaking changes to existing functionality
8. ✅ Error handling is graceful

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed with `uv add pydantic-settings httpx`
2. **Database Errors**: Ensure database file exists or is created properly
3. **Configuration Errors**: Check environment variables and `.env` file
4. **State Management Errors**: Verify `demo_assets/` directory exists

### Debug Commands

```bash
# Check dependencies installation
uv list | grep -E "(pydantic|httpx|fastapi)"

# Check database file
ls -la test.db

# Check configuration
uv run python -c "from dependencies.config import get_settings; print(get_settings())"

# Check application state
uv run python -c "from main import app; print(dir(app.state))"
```

## Next Steps

After successful Phase 1A testing:

1. **Phase 1B**: Add remaining service dependencies (WebinarService, ChatService)
2. **Phase 1C**: Comprehensive testing and validation
3. **Phase 2**: Advanced features and state detection

---

**Test Plan Version**: 1.0  
**Last Updated**: September 18, 2025  
**Created By**: AI Assistant
