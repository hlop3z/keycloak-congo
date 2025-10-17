# Backend Demo Application

FastAPI service demonstrating Kong + Keycloak integration with JWT validation.

## Overview

This is a sample backend application that:

- ✅ Receives JWT-validated requests from Kong
- ✅ Extracts user information from JWT claims
- ✅ Implements role-based access control
- ✅ Provides public, protected, and admin endpoints
- ✅ Can be deployed standalone or with Kong

## Quick Start

### 1. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit if needed
nano .env
```

### 2. Deploy

```bash
# Start backend
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 3. Test

```bash
# Test health endpoint
curl http://localhost:8080/health

# Test public endpoint
curl http://localhost:8080/api/public
```

## API Endpoints

| Endpoint           | Method    | Auth | Role  | Description                    |
| ------------------ | --------- | ---- | ----- | ------------------------------ |
| `/`                | GET       | No   | -     | Service information            |
| `/health`          | GET       | No   | -     | Health check                   |
| `/docs`            | GET       | No   | -     | API documentation (Swagger UI) |
| `/api/public`      | GET, POST | No   | -     | Public endpoint                |
| `/api/protected`   | GET, POST | Yes  | any   | Protected endpoint             |
| `/api/admin`       | GET       | Yes  | admin | Admin-only endpoint            |
| `/api/admin/users` | GET       | Yes  | admin | Admin user list                |

## Configuration

### Environment Variables

| Variable       | Default          | Description          |
| -------------- | ---------------- | -------------------- |
| `APP_NAME`     | Backend Demo API | Application name     |
| `APP_VERSION`  | 1.0.0            | Application version  |
| `LOG_LEVEL`    | info             | Logging level        |
| `HOST`         | 0.0.0.0          | Server host          |
| `PORT`         | 8080             | Server port          |
| `WORKERS`      | 1                | Uvicorn workers      |
| `CORS_ORIGINS` | \*               | Allowed CORS origins |
| `ENABLE_DOCS`  | true             | Enable Swagger docs  |

### Production Settings

```bash
# .env for production
LOG_LEVEL=warning
WORKERS=4
CORS_ORIGINS=https://app.example.com,https://mobile.example.com
ENABLE_DOCS=false
```

## Development

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8080
```

### Project Structure

```
applications/backend-demo/
├── docker-compose.yml          # Standalone deployment
├── Dockerfile                  # Container image
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py           # API endpoints
│   │   └── auth.py             # JWT utilities
│   ├── models/                 # Data models
│   │   └── __init__.py
│   └── utils/
│       ├── __init__.py
│       └── config.py           # Configuration
├── tests/                      # Test suite
│   └── __init__.py
└── README.md                   # This file
```

## JWT Integration

### How It Works

1. **Kong validates JWT** signature using Keycloak's public key
2. **Kong forwards request** to backend with Authorization header
3. **Backend extracts claims** from JWT (safe, already validated)
4. **Backend implements** role-based access control

### JWT Claims Used

```json
{
  "preferred_username": "testuser",
  "email": "user@example.com",
  "realm_roles": ["user", "admin"],
  "sub": "user-id",
  "iss": "http://keycloak:8080/realms/kong-realm",
  "exp": 1234567890,
  "iat": 1234567890
}
```

### Extracting User Info

```python
from src.api.auth import decode_jwt_payload

# In your route
jwt_payload = decode_jwt_payload(authorization)
username = jwt_payload.get("preferred_username")
roles = jwt_payload.get("realm_roles", [])
```

### Role-Based Access Control

```python
from src.api.auth import check_role

# Check for admin role
if not check_role(jwt_payload, "admin"):
    raise HTTPException(status_code=403, detail="Admin required")
```

## Usage

### Standalone (No Kong)

```bash
# Start backend only
docker-compose up -d

# Access directly
curl http://localhost:8080/api/public
```

### With Kong

```bash
# Backend is accessed through Kong
curl http://kong:8000/api/public

# Kong validates JWT, then forwards to backend
curl -H "Authorization: Bearer <token>" http://kong:8000/api/protected
```

## Testing

### Manual Testing

```bash
# Public endpoint (no auth)
curl http://localhost:8080/api/public

# Get JWT token from Keycloak
kc-test token get --user testuser --realm kong-realm

# Protected endpoint (with JWT)
curl -H "Authorization: Bearer <token>" \
  http://localhost:8080/api/protected

# Admin endpoint (admin role required)
kc-test token get --user admin --realm kong-realm
curl -H "Authorization: Bearer <admin-token>" \
  http://localhost:8080/api/admin
```

### Python Testing CLI

```bash
# Run test suite
kc-test suite run --component backend

# Test specific endpoint
kc-test api test --endpoint /api/protected --expect-role user
```

### Unit Tests

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

## API Documentation

When `ENABLE_DOCS=true`:

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

## Logging

Application uses Python logging:

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

Set log level via `LOG_LEVEL` environment variable.

## Health Checks

```bash
# Health endpoint
curl http://localhost:8080/health

# Expected response
{
  "status": "healthy",
  "service": "Backend Demo API",
  "version": "1.0.0"
}
```

## Troubleshooting

### Backend Won't Start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Port conflict: Change PORT in .env
# - Missing dependencies: Rebuild container
# - Syntax errors: Check Python files
```

### JWT Not Being Decoded

```bash
# Verify Authorization header is present
# Header format: "Bearer <token>"

# Check if Kong is forwarding the header
docker-compose logs backend | grep Authorization
```

### Role Check Failing

```bash
# Verify JWT contains roles
kc-test token decode <token>

# Check realm_roles claim
# Should be array: ["user", "admin"]
```

## Production Deployment

1. **Security**:

   - Disable docs: `ENABLE_DOCS=false`
   - Restrict CORS: Set specific origins
   - Use production logging: `LOG_LEVEL=warning`

2. **Performance**:

   - Multiple workers: `WORKERS=4`
   - Resource limits in docker-compose

3. **Monitoring**:
   - Health checks enabled by default
   - Add metrics endpoint if needed
   - Centralized logging

## Extending

### Adding New Endpoints

```python
# In src/api/routes.py

@router.get("/my-endpoint")
async def my_endpoint(authorization: Optional[str] = Header(None)):
    jwt_payload = decode_jwt_payload(authorization)
    # Your logic here
    return {"message": "Success"}
```

### Adding Models

```python
# In src/models/user.py

from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str
    roles: List[str]
```

### Adding Middleware

```python
# In src/main.py

from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    return response
```

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Uvicorn](https://www.uvicorn.org/)

## Support

For issues specific to this component:

1. Check logs: `docker-compose logs backend`
2. Verify configuration: Review `.env` file
3. Test endpoints: Use Swagger UI at `/docs`
4. Review [Troubleshooting](#troubleshooting) section

---

**Component Status**: ✅ Production-ready FastAPI application
