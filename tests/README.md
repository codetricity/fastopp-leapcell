# FastAPI Dependency Injection Tests

This test suite demonstrates basic FastAPI dependency injection concepts for educational purposes.

## Test Structure

```
tests/
├── __init__.py
├── dependencies.py          # Test-specific dependency overrides
├── test_dependency_injection.py  # Main test suite
└── README.md               # This file
```

## Running Tests

### Run All Tests
```bash
uv run pytest tests/ -v
```

### Run Specific Test Classes
```bash
# Test dependency injection basics
uv run pytest tests/test_dependency_injection.py::TestDependencyInjection -v

# Test API endpoints
uv run pytest tests/test_dependency_injection.py::TestAPIEndpoints -v

# Test mock services
uv run pytest tests/test_dependency_injection.py::TestMockServices -v
```

### Run Individual Tests
```bash
# Test a specific endpoint
uv run pytest tests/test_dependency_injection.py::TestAPIEndpoints::test_products_endpoint -v

# Test dependency injection
uv run pytest tests/test_dependency_injection.py::TestDependencyInjection::test_settings_dependency -v
```

## Test Categories

### 1. TestDependencyInjection
Tests the core dependency injection functionality:
- Settings dependency
- Database session dependency  
- Service dependencies

### 2. TestAPIEndpoints
Tests essential API endpoints:
- `/api/products` - Product data endpoint
- `/api/webinar-attendees` - Webinar attendees endpoint
- `/chat/test` - Chat service test endpoint

### 3. TestDependencyOverrides
Tests the dependency override mechanism used for testing:
- App creation with overrides
- Dependency substitution

### 4. TestMockServices
Tests mock service implementations:
- MockProductService
- MockWebinarService  
- MockChatService

### 5. TestConfiguration
Tests configuration and settings:
- Test settings defaults
- Settings validation

### 6. TestDatabaseDependencies
Tests database dependency functions:
- Database engine creation
- Session factory creation

## Educational Focus

This test suite is designed for teaching FastAPI dependency injection concepts:

1. **Simple and Clear**: Each test demonstrates a specific concept
2. **No Complex Edge Cases**: Focus on core functionality
3. **Fast Execution**: Tests run quickly for immediate feedback
4. **Easy to Understand**: Clear test names and structure
5. **Practical Examples**: Real-world FastAPI patterns

## Key Learning Points

- **Dependency Injection**: How FastAPI manages dependencies
- **Testing**: How to test FastAPI applications with mocks
- **Configuration**: How to manage application settings
- **Database Sessions**: How to handle database connections
- **Service Layer**: How to structure business logic

## Dependencies

The tests use these key dependencies:
- `pytest` - Testing framework
- `pytest-asyncio` - Async test support
- `httpx` - HTTP client for testing
- `fastapi` - FastAPI framework
- `sqlalchemy` - Database ORM

## Best Practices Demonstrated

1. **Dependency Overrides**: Using `app.dependency_overrides` for testing
2. **Mock Services**: Creating mock implementations for testing
3. **Test Fixtures**: Using pytest fixtures for setup
4. **Async Testing**: Testing async FastAPI endpoints
5. **Configuration Testing**: Testing application settings