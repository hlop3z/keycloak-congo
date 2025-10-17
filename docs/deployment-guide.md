# Deployment Guide

Comprehensive guide for deploying Kong + Keycloak modular architecture.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Component Deployment](#component-deployment)
4. [Composition Deployment](#composition-deployment)
5. [Configuration](#configuration)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software

- **Docker Engine**: 20.10 or later
- **Docker Compose**: 2.0 or later
- **Go**: 1.21+ (for building deployment CLI)
- **Python**: 3.12+ (for testing CLI)

### System Requirements

**Development**:

- CPU: 2 cores
- RAM: 4 GB
- Disk: 10 GB free

**Production**:

- CPU: 4+ cores
- RAM: 8+ GB
- Disk: 50+ GB free (with backups)

### Network Requirements

**Development**:

- Ports: 8000-8001 (Kong), 8080 (Keycloak), 9000-9001 (Kong Internal)

**Production**:

- Ports: 80, 443 (with reverse proxy)
- Domain names configured
- SSL certificates

## Quick Start

### 1. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd keycloak-congo

# Quick deploy using Makefile
make deploy-dev
```

### 2. Verify Deployment

```bash
# Check service status
make status

# Test endpoints
curl http://localhost:8000/api/public
curl http://localhost:8080  # Keycloak

# View logs
make logs
```

### 3. Get JWT Token

```bash
# Using curl
curl -X POST 'http://localhost:8080/realms/kong-realm/protocol/openid-connect/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=testuser' \
  -d 'password=user123' \
  -d 'grant_type=password' \
  -d 'client_id=kong-client'

# Or using Python CLI
cd tools/testing-cli
python -m src.cli token get --user testuser --realm kong-realm
```

### 4. Test Protected Endpoint

```bash
# Replace <TOKEN> with actual token
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/api/protected
```

## Component Deployment

Deploy components individually for development or custom compositions.

### Keycloak Standalone

```bash
# Navigate to component
cd infrastructure/keycloak

# Copy environment file
cp .env.example .env

# Edit passwords (important!)
nano .env

# Deploy
docker-compose up -d

# Verify
curl http://localhost:8080/health/ready
```

**Access**:

- URL: http://localhost:8080
- Username: `admin` (from .env)
- Password: (from .env)

### Kong Standalone

```bash
# Navigate to component
cd infrastructure/kong

# Copy environment file
cp .env.example .env

# Deploy
docker-compose up -d

# Verify
curl http://localhost:8001/status
```

**Note**: Kong needs Keycloak accessible for JWT validation.

### Backend Standalone

```bash
# Navigate to component
cd applications/backend-demo

# Copy environment file
cp .env.example .env

# Deploy
docker-compose up -d

# Verify
docker logs backend-api
```

## Composition Deployment

Deploy full stack or multi-instance configurations.

### Full Stack (Development)

```bash
# Copy environment file
cp compose/environments/dev.env.example compose/environments/dev.env

# Deploy all components
docker-compose -f compose/docker-compose.full.yml \
  --env-file compose/environments/dev.env up -d

# Or use Makefile
make deploy-dev
```

**Includes**:

- PostgreSQL
- Keycloak (with realms)
- Kong (single instance)
- Backend

### Multi-Kong Setup

```bash
# Deploy multiple Kong instances
docker-compose -f compose/docker-compose.multi-kong.yml \
  --env-file compose/environments/dev.env up -d

# Or use Makefile
make deploy-multi-kong
```

**Includes**:

- PostgreSQL
- Keycloak (with multiple realms)
- Kong Public (port 8000, kong-realm)
- Kong Internal (port 9000, internal-realm)
- Backend

### Production Deployment

```bash
# Copy production environment
cp compose/environments/prod.env.example compose/environments/prod.env

# ⚠️ IMPORTANT: Edit and change ALL passwords
nano compose/environments/prod.env

# Deploy
docker-compose -f compose/docker-compose.full.yml \
  --env-file compose/environments/prod.env up -d
```

## Configuration

### Environment Variables

Each component has its own `.env.example` file:

**Keycloak** (`infrastructure/keycloak/.env.example`):

```bash
POSTGRES_PASSWORD=changeme_secure_password
KEYCLOAK_ADMIN_PASSWORD=changeme_admin_password
```

**Kong** (`infrastructure/kong/.env.example`):

```bash
KONG_INSTANCE_NAME=kong
KONG_PROXY_PORT=8000
KONG_DECLARATIVE_CONFIG=/kong/config/kong.yml
```

**Backend** (`applications/backend-demo/.env.example`):

```bash
LOG_LEVEL=info
PORT=8080
```

### Declarative Configuration

**Kong** (`infrastructure/kong/config/instances/kong-public.yml`):

```yaml
services:
  - name: backend-api
    url: http://backend:8080
    routes:
      - name: protected
        paths: ["/api/protected"]
```

**Keycloak** (`infrastructure/keycloak/config/realms/kong-realm.json`):

```json
{
  "realm": "kong-realm",
  "clients": [
    {
      "clientId": "kong-client",
      "publicClient": true
    }
  ]
}
```

### Secrets Management

**Development**:

- Use `.env` files (not committed)
- Simple passwords acceptable

**Production**:

- Use secret management service (Vault, AWS Secrets Manager)
- Strong passwords (20+ characters)
- Rotate regularly
- Audit access

## Verification

### Service Health

```bash
# All services
make health

# Individual checks
curl http://localhost:8080/health/ready  # Keycloak
curl http://localhost:8001/status        # Kong
curl http://localhost:8000/api/public    # Backend via Kong
```

### Network Connectivity

```bash
# Check if Kong can reach Keycloak
docker exec kong-gateway ping keycloak

# Check if Kong can reach Backend
docker exec kong-gateway ping backend

# View networks
docker network ls
docker network inspect kong-network
```

### Configuration Validation

```bash
# Validate Kong config
docker exec kong-gateway kong config parse /kong/config/kong.yml

# Check Keycloak realm import
docker logs keycloak | grep "import"
```

### Integration Test

```bash
# Full workflow
make demo

# Or manual:
# 1. Get token
TOKEN=$(curl -s -X POST \
  'http://localhost:8080/realms/kong-realm/protocol/openid-connect/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=testuser&password=user123&grant_type=password&client_id=kong-client' \
  | jq -r '.access_token')

# 2. Test public
curl http://localhost:8000/api/public

# 3. Test protected
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/protected

# 4. Test admin (should fail with testuser)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/admin
```

## Troubleshooting

### Services Won't Start

**Symptom**: `docker-compose up` fails

**Check**:

```bash
# View logs
docker-compose logs

# Check ports
netstat -tulpn | grep 8080  # Check if port in use

# Check Docker
docker ps -a
docker network ls
```

**Solutions**:

- Change conflicting ports in `.env`
- Stop other services using the same ports
- Check Docker daemon status

### Keycloak Health Check Failing

**Symptom**: Keycloak container restarting

**Check**:

```bash
docker logs keycloak

# Common issues:
# - Database not ready
# - Invalid realm JSON
# - Memory issues
```

**Solutions**:

```bash
# Fix realm JSON
jq . infrastructure/keycloak/config/realms/*.json

# Increase memory
docker-compose -f compose/docker-compose.full.yml \
  --env-file compose/environments/dev.env \
  config | grep memory

# Wait for PostgreSQL
docker-compose up -d postgres
sleep 20
docker-compose up -d keycloak
```

### Kong Configuration Errors

**Symptom**: Kong fails to start or routes not working

**Check**:

```bash
docker logs kong-gateway

# Validate configuration
docker run --rm -v $(pwd)/infrastructure/kong/config:/kong \
  kong:3.9.1-ubuntu kong config parse /kong/instances/kong-public.yml
```

**Solutions**:

- Fix YAML syntax errors
- Ensure required environment variables are set
- Check backend service connectivity

### JWT Validation Failing

**Symptom**: 401 Unauthorized on protected endpoints

**Check**:

```bash
# Verify Keycloak JWKS accessible
curl http://localhost:8080/realms/kong-realm/protocol/openid-connect/certs

# Check token
TOKEN="<your-token>"
echo $TOKEN | cut -d. -f2 | base64 -d

# Verify Kong can reach Keycloak
docker exec kong-gateway curl http://keycloak:8080/health
```

**Solutions**:

- Ensure Keycloak is healthy
- Check network connectivity (kong-network)
- Verify token not expired
- Check client configuration in Keycloak

### Backend Not Accessible

**Symptom**: 502/503 errors from Kong

**Check**:

```bash
# Check backend logs
docker logs backend-api

# Test backend directly
curl http://localhost:8080/health  # If exposed

# Test from Kong container
docker exec kong-gateway curl http://backend:8080/health
```

**Solutions**:

- Ensure backend is running
- Check network connectivity
- Verify service name resolution
- Review backend logs for errors

## Advanced Deployments

### Custom Realm

1. Create realm JSON:

```bash
cp infrastructure/keycloak/config/realms/kong-realm.json \
   infrastructure/keycloak/config/realms/my-realm.json
```

2. Edit realm configuration:

```json
{
  "realm": "my-realm",
  "clients": [{"clientId": "my-client", ...}],
  "users": [...]
}
```

3. Restart Keycloak:

```bash
docker-compose -f compose/docker-compose.full.yml restart keycloak
```

### Additional Kong Instance

1. Create configuration:

```bash
cp infrastructure/kong/config/instances/kong-public.yml \
   infrastructure/kong/config/instances/kong-api-v2.yml
```

2. Update docker-compose:

```yaml
services:
  kong-api-v2:
    image: kong:3.9.1-ubuntu
    # ... configuration
    ports:
      - "10000:10000"
```

3. Deploy:

```bash
docker-compose up -d kong-api-v2
```

### SSL/TLS Termination

**Option 1: Reverse Proxy** (Recommended)

```
Nginx/Traefik (SSL) → Kong (HTTP) → Backend
```

**Option 2: Kong SSL**

```yaml
# Kong configuration
KONG_SSL_CERT: /path/to/cert.pem
KONG_SSL_CERT_KEY: /path/to/key.pem
```

## Next Steps

After successful deployment:

1. **Change default passwords** (production)
2. **Configure monitoring** (Prometheus, Grafana)
3. **Set up backups** (PostgreSQL)
4. **Configure logging** (centralized logging)
5. **Review security** (firewall, network policies)
6. **Load testing** (ensure capacity)
7. **Documentation** (custom configurations)

## References

- [Architecture Overview](architecture.md)
- [Multi-Kong Setup](multi-kong-setup.md)
- [CLI Reference](cli-reference.md)
- [Component READMEs](../infrastructure/)

---

**Last Updated**: 2025-10-17  
**Version**: 2.0.0
