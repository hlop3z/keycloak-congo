# Kong Instance Configurations

This directory contains pre-configured Kong instances for different use cases.

## Available Instances

### kong-public.yml

**Purpose**: Public-facing API gateway

**Configuration**:

- Routes: `/api/public`, `/api/protected`, `/api/admin`
- Rate limit: 100 req/sec, 10,000 req/hour
- Connects to: `kong-realm` in Keycloak
- CORS: Enabled for all origins (configure for production)

**Use case**: External APIs, mobile apps, web applications

### kong-internal.yml

**Purpose**: Internal service mesh

**Configuration**:

- Routes: `/internal/api`
- Rate limit: 500 req/sec, 50,000 req/hour
- Connects to: `internal-realm` in Keycloak
- CORS: Disabled

**Use case**: Service-to-service communication, microservices

## Creating New Instances

### Method 1: Copy Template

```bash
# Copy the template
cp ../kong.template.yml my-instance.yml

# Customize for your needs
# - Change service names
# - Update routes
# - Adjust rate limits
# - Add/remove plugins
```

### Method 2: Use CLI (Recommended)

```bash
# Create new instance via deployment CLI
kc-deploy kong add --name kong-api-v2 --realm api-v2-realm

# This will:
# 1. Generate kong-api-v2.yml from template
# 2. Create kong-api-v2.env with settings
# 3. Update compose file to include new instance
```

## Instance Configuration Best Practices

### Naming Convention

- **kong-public** - Public-facing APIs
- **kong-internal** - Internal services
- **kong-{service}** - Service-specific gateways
- **kong-{version}** - API version-specific gateways

### Rate Limiting

```yaml
# Public APIs (stricter)
rate-limiting:
  second: 10-100
  hour: 1000-10000

# Internal APIs (more lenient)
rate-limiting:
  second: 100-1000
  hour: 10000-100000
```

### Environment-Specific Settings

**Development**:

```yaml
plugins:
  - name: cors
    config:
      origins: ["*"] # Allow all for dev
```

**Production**:

```yaml
plugins:
  - name: cors
    config:
      origins:
        - "https://app.example.com"
        - "https://mobile.example.com"
```

## Deploying Instances

### Single Instance

```bash
# Set instance configuration
export KONG_DECLARATIVE_CONFIG=/kong/config/instances/kong-public.yml
export KONG_INSTANCE_NAME=kong-public
export KONG_PROXY_PORT=8000

# Deploy
docker-compose up -d
```

### Multiple Instances

Use the composition layer:

```bash
# Deploy all configured instances
kc-deploy multi-kong --instances kong-public,kong-internal

# Or use docker-compose directly
docker-compose -f compose/docker-compose.multi-kong.yml up -d
```

## Instance-Specific Environment Variables

Create `.env` file for each instance:

**kong-public.env**:

```bash
KONG_INSTANCE_NAME=kong-public
KONG_DECLARATIVE_CONFIG=/kong/config/instances/kong-public.yml
KONG_PROXY_PORT=8000
KONG_ADMIN_PORT=8001
KEYCLOAK_REALM=kong-realm
```

**kong-internal.env**:

```bash
KONG_INSTANCE_NAME=kong-internal
KONG_DECLARATIVE_CONFIG=/kong/config/instances/kong-internal.yml
KONG_PROXY_PORT=9000
KONG_ADMIN_PORT=9001
KEYCLOAK_REALM=internal-realm
```

## Connecting to Different Keycloak Realms

Each instance can connect to a different realm:

```yaml
# In instance configuration, reference environment variables
_comment: "Realm: ${KEYCLOAK_REALM}"

# Set in .env or compose file
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=kong-realm  # or internal-realm, api-v2-realm, etc.
```

## Testing Instance Configuration

### Validate Configuration

```bash
# Using deployment CLI
kc-deploy config validate --file kong-public.yml

# Using Kong directly
docker run --rm -v $(pwd):/kong kong:3.7-alpine kong config parse /kong/kong-public.yml
```

### Test Instance

```bash
# Using Python testing CLI
kc-test api test --instance kong-public --endpoint /api/public

# Manual test
curl http://localhost:8000/api/public
```

## Instance Management via CLI

```bash
# List all instances
kc-deploy kong list

# Add new instance
kc-deploy kong add --name kong-api-v2 --realm api-v2-realm

# Remove instance
kc-deploy kong remove --name kong-api-v2

# Update instance configuration
kc-deploy kong update --name kong-public --config new-config.yml

# Get instance status
kc-deploy status kong-public
```

## Multi-Tenant Setup Example

Different instances for different tenants:

```yaml
# kong-tenant-a.yml
services:
  - name: tenant-a-api
    url: http://tenant-a-backend:8080

# kong-tenant-b.yml
services:
  - name: tenant-b-api
    url: http://tenant-b-backend:8080
```

Each connects to tenant-specific Keycloak realm.

## Version-Based Routing Example

Different instances for API versions:

```yaml
# kong-api-v1.yml
routes:
  - paths: ["/v1/api"]

# kong-api-v2.yml
routes:
  - paths: ["/v2/api"]
```

## Troubleshooting

### Instance Won't Start

```bash
# Check configuration syntax
kc-deploy config validate --file instances/kong-public.yml

# View logs
docker logs kong-public

# Common issues:
# - Invalid YAML syntax
# - Missing environment variables
# - Port conflicts
```

### Routes Not Working

```bash
# List routes via Admin API
curl http://localhost:8001/routes

# Check service status
curl http://localhost:8001/services

# Verify plugins
curl http://localhost:8001/plugins
```

### JWT Validation Failing

```bash
# Verify Keycloak is accessible
curl http://keycloak:8080/realms/${KEYCLOAK_REALM}

# Check JWKS endpoint
curl http://keycloak:8080/realms/${KEYCLOAK_REALM}/protocol/openid-connect/certs

# Test with valid token
kc-test token get --user testuser --realm kong-realm
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/protected
```

## Directory Structure

```
infrastructure/kong/config/instances/
├── kong-public.yml          # Public API instance
├── kong-internal.yml        # Internal API instance
└── README.md                # This file

# When using CLI to add instances:
├── kong-api-v2.yml          # Auto-generated
├── kong-tenant-a.yml        # Auto-generated
└── ...
```

## References

- [Kong DB-less Mode](https://docs.konghq.com/gateway/latest/production/deployment-topologies/db-less-and-declarative-config/)
- [Kong Configuration Reference](https://docs.konghq.com/gateway/latest/reference/configuration/)
- [Multi-Kong Setup Guide](../../../../docs/multi-kong-setup.md)

---

**Best Practice**: Start with template, customize incrementally, test thoroughly before production.
