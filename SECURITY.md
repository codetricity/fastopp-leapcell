# Security Policy

## Educational Project Notice

⚠️ **This is an educational project** designed for learning FastAPI, PostgreSQL, and web development. It includes debug endpoints and logging that are intentionally exposed for educational purposes.

## Debug Endpoints (Educational Use)

This project includes several debug endpoints that are **intentionally exposed** for learning:

- `/debug/current-user` - Shows authentication state
- `/debug/database` - Database configuration and permissions
- `/debug/settings` - Application settings and upload directory
- `/debug/simple` - Basic health check
- `/debug/connection` - Database connectivity test
- `/debug/database-data` - Database table contents
- `/debug/list-files` - File system contents
- `/debug/test-image/{filename}` - Image serving test

**These endpoints are safe for educational use** but should be removed or protected in production deployments.

## Security Features

### ✅ Implemented Security Measures

- **Authentication**: JWT tokens with 30-minute expiration
- **Authorization**: Role-based access control (staff/admin)
- **Password Security**: bcrypt hashing with salt
- **Security Headers**: Comprehensive security headers implemented
- **Input Validation**: File type and size validation
- **SQL Injection Protection**: SQLModel/SQLAlchemy ORM prevents SQL injection
- **Session Management**: Secure HTTP-only cookies

### 🔧 Security Headers

The application includes comprehensive security headers:

```python
# Security headers implemented
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
Content-Security-Policy: [configured for educational use]
```

## Production Deployment Security

If you plan to use this codebase in production, follow these guidelines:

### 1. Remove Debug Endpoints

Remove or protect these endpoints:
```python
# Remove these routes from main.py
@app.get("/debug/current-user")
@app.get("/debug/database")
@app.get("/debug/settings")
# ... other debug endpoints
```

### 2. Secure Logging

Remove sensitive information from logs:
```python
# Remove or secure these debug prints
print(f"🔐 Password verification - Input password: {password}")
print(f"🔐 Stored hash: {user.hashed_password}")
print(f"DEBUG: API key found: {api_key[:10]}...")
```

### 3. Environment Configuration

Set production environment variables:
```bash
# Production environment
ENVIRONMENT=production
SECRET_KEY=your_secure_production_secret_key_here
DATABASE_URL=postgresql+psycopg2://user:password@host:port/database
```

### 4. Database Configuration

Disable debug mode in production:
```python
# In db.py, set echo=False for production
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to False in production
    # ... other settings
)
```

### 5. File Upload Security

Enhance file upload validation:
```python
# Add file content validation
import magic

def validate_file_content(file_content: bytes) -> bool:
    """Validate file content, not just MIME type"""
    file_type = magic.from_buffer(file_content, mime=True)
    return file_type.startswith('image/')
```

## Vulnerability Reporting

### For Educational Use
- Debug endpoints are intentionally exposed for learning
- Logging includes educational information
- Security is relaxed for tutorial purposes

### For Production Use
If you find security vulnerabilities in production deployments:

1. **Do NOT** create public GitHub issues for security vulnerabilities
2. **Do NOT** post security issues in public forums
3. **Email** security concerns to: [your-email@example.com]
4. **Include** detailed information about the vulnerability
5. **Wait** for acknowledgment before public disclosure

## Security Best Practices

### For Educational Projects
- Debug endpoints help students understand authentication
- Logging shows the flow of requests and responses
- File uploads demonstrate security concepts
- Database queries are visible for learning

### For Production Projects
- Remove all debug endpoints
- Implement proper logging (no sensitive data)
- Add rate limiting for authentication
- Use environment-specific configurations
- Implement proper error handling
- Add monitoring and alerting

## Dependencies

This project uses the following security-relevant dependencies:

- **FastAPI**: Web framework with built-in security features
- **SQLModel**: ORM that prevents SQL injection
- **PyJWT**: Secure JWT token handling
- **bcrypt**: Secure password hashing
- **python-multipart**: Secure file upload handling

All dependencies are regularly updated and free from known critical vulnerabilities.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contact

For security questions or concerns:
- **Educational Use**: Debug endpoints are intentionally exposed
- **Production Use**: Follow the security guidelines above
- **Vulnerability Reports**: Use the reporting process outlined above
