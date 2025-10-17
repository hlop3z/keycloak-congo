# Kong API Gateway (DB-less Mode)

Standalone Kong deployment in DB-less mode with declarative configuration supporting multiple instances.

## Overview

This component provides:

- ✅ Kong 3.7 in DB-less mode
- ✅ Declarative configuration with templates
- ✅ Support for multiple Kong instances
- ✅ Keycloak integration for JWT validation
- ✅ Pre-configured instance examples
- ✅ Independent deployment capability

## Quick Start

### 1. Configure Instance

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration
nano .env
```

### 2. Choose or Create Configuration

```bash
# Use existing instance configuration
export KONG_DECLARATIVE_CONFIG=/kong/config/instances/kong-public.yml

# Or use template
export KONG_DECLARATIVE_CONFIG=/kong/config/kong.template.yml
```

### 3. Deploy

```bash
# Start Kong
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f kong
```

### 4. Verify

```bash
# Check Admin API
curl http://localhost:8001/status

# Test proxy
curl http://localhost:8000/api/public
```

## Configuration

### Environment Variables

| Variable                      | Default               | Description         |
| ----------------------------- | --------------------- | ------------------- |
| `KONG_INSTANCE_NAME`          | kong                  | Instance identifier |
| `KONG_PROXY_PORT`             | 8000                  | Proxy HTTP port     |
| `KONG_PROXY_SSL_PORT`         | 8443                  | Proxy HTTPS port    |
| `KONG_ADMIN_PORT`             | 8001                  | Admin API port      |
| `KONG_DECLARATIVE_CONFIG`     | /kong/config/kong.yml | Config file path    |
| `KONG_LOG_LEVEL`              | notice                | Logging level       |
| `KONG_NGINX_WORKER_PROCESSES` | auto                  | Worker processes    |

### Declarative Configuration

Kong uses YAML files for configuration. Three types available:

1. **Template** (`config/kong.template.yml`):

   - Base template with placeholders
   - Use for creating new instances

2. **Instance configs** (`config/instances/*.yml`):

   - Pre-configured for specific use cases
   - kong-public.yml - Public APIs
   - kong-internal.yml - Internal services

3. **Custom configs**:
   - Create your own based on template
   - Place in `config/` or `config/instances/`

See [config/instances/README.md](config/instances/README.md) for details.

## Usage

### Single Instance Deployment

```bash
# Configure for your instance
export KONG_INSTANCE_NAME=kong-public
export KONG_DECLARATIVE_CONFIG=/kong/config/instances/kong-public.yml
export KONG_PROXY_PORT=8000

# Deploy
docker-compose up -d
```

### Multiple Instance Deployment

Deploy separate Kong instances:

```bash
# Instance 1: Public APIs
KONG_INSTANCE_NAME=kong-public \
KONG_PROXY_PORT=8000 \
KONG_ADMIN_PORT=8001 \
KONG_DECLARATIVE_CONFIG=/kong/config/instances/kong-public.yml \
docker-compose -p kong-public up -d

# Instance 2: Internal APIs
KONG_INSTANCE_NAME=kong-internal \
KONG_PROXY_PORT=9000 \
KONG_ADMIN_PORT=9001 \
KONG_DECLARATIVE_CONFIG=/kong/config/instances/kong-internal.yml \
docker-compose -p kong-internal up -d
```

Or use the composition layer for easier management.

### Keycloak Integration

Kong validates JWTs issued by Keycloak:

1. **User requests token** from Keycloak
2. **Keycloak issues** signed JWT
3. **User sends** JWT to Kong
4. **Kong validates** JWT signature
5. **Kong forwards** request to backend

**No pre-configured consumers needed** - Kong validates any JWT signed by Keycloak's private key.

## Admin API

### Access Admin API

```bash
# Get Kong status
curl http://localhost:8001/status

# List services
curl http://localhost:8001/services

# List routes
curl http://localhost:8001/routes

# List plugins
curl http://localhost:8001/plugins
```

### Validate Configuration

```bash
# Inside container
docker-compose exec kong kong config parse /kong/config/kong.yml

# Using deployment CLI
kc-deploy config validate --component kong
```

## Adding Routes and Services

### Option 1: Update Declarative Config

Edit your instance YAML file:

```yaml
services:
  - name: my-new-service
    url: http://my-service:8080
    routes:
      - name: my-route
        paths: ["/my-api"]
        methods: [GET, POST]
```

Reload Kong:

```bash
docker-compose restart kong
```

### Option 2: Use CLI (Recommended)

```bash
# Add service and route
kc-deploy kong service add --name my-service --url http://my-service:8080
kc-deploy kong route add --service my-service --path /my-api
```

## Plugins

### Global Plugins

Applied to all services/routes (configured in YAML):

- **CORS**: Cross-origin resource sharing
- **Rate Limiting**: Request throttling
- **Request Transformer**: Add headers, modify requests
- **Correlation ID**: Request tracking

### Route-Specific Plugins

Add to specific routes:

```yaml
routes:
  - name: my-route
    paths: ["/api"]
    plugins:
      - name: jwt
        config:
          claims_to_verify: [exp]
```

### Available Plugins

Kong includes many plugins:

- Authentication: JWT, OAuth 2.0, Key Auth, Basic Auth
- Security: ACL, IP Restriction, Bot Detection
- Traffic Control: Rate Limiting, Request Size Limiting
- Transformations: Request/Response Transformer
- Logging: File Log, HTTP Log, Syslog
- Analytics: Prometheus, Datadog, StatsD

See [Kong Plugin Hub](https://docs.konghq.com/hub/) for all plugins.

## Networking

### Default Network

- **Network**: `kong-network`
- **Type**: Bridge
- **Purpose**: Connect Kong to backend services

### Multi-Network Setup

Kong can connect to multiple networks:

```yaml
services:
  kong:
    networks:
      - kong-network # Backend services
      - keycloak-network # Keycloak access
      - external # External services
```

## Health and Monitoring

### Health Checks

Built-in health check: `kong health`

```bash
# Check health
docker-compose exec kong kong health

# Via HTTP
curl http://localhost:8001/status
```

### Monitoring Endpoints

- Status: `http://localhost:8001/status`
- Metrics: Enable Prometheus plugin for `/metrics`

### Logs

```bash
# View logs
docker-compose logs -f kong

# Tail access logs
docker-compose logs kong | grep "access"

# Tail error logs
docker-compose logs kong | grep "error"
```

## Production Considerations

### Security

1. **Restrict Admin API**:

   ```yaml
   KONG_ADMIN_LISTEN: "127.0.0.1:8001"
   ```

2. **Use SSL/TLS**:

   ```yaml
   KONG_PROXY_LISTEN: "0.0.0.0:8000, 0.0.0.0:8443 ssl"
   KONG_SSL_CERT: /path/to/cert.pem
   KONG_SSL_CERT_KEY: /path/to/key.pem
   ```

3. **Enable Security Plugins**:
   - Rate limiting
   - IP restrictions
   - Bot detection

### Performance

1. **Worker Processes**:

   ```yaml
   KONG_NGINX_WORKER_PROCESSES: "auto" # or specific number
   ```

2. **Resource Limits**:

   ```yaml
   deploy:
     resources:
       limits:
         cpus: "2"
         memory: 1G
   ```

3. **Caching**: Enable proxy caching plugin

### High Availability

- Deploy multiple Kong instances
- Use load balancer (Nginx, HAProxy, cloud LB)
- Share declarative configuration
- Monitor health endpoints

## Troubleshooting

### Kong Won't Start

```bash
# Check logs
docker-compose logs kong

# Common issues:
# - Invalid declarative config: Validate YAML syntax
# - Port conflict: Change KONG_PROXY_PORT
# - Config file not found: Check volume mount
```

### Configuration Not Loading

```bash
# Verify file exists
docker-compose exec kong ls -la /kong/config/

# Validate configuration
docker-compose exec kong kong config parse /kong/config/kong.yml

# Check for syntax errors
docker-compose exec kong cat /kong/config/kong.yml
```

### Routes Not Working

```bash
# List routes
curl http://localhost:8001/routes | jq

# Check service status
curl http://localhost:8001/services | jq

# Test backend connectivity
docker-compose exec kong ping backend
```

### JWT Validation Failing

```bash
# Check Keycloak connectivity
docker-compose exec kong curl http://keycloak:8080/realms/kong-realm

# Verify JWKS endpoint
curl http://keycloak:8080/realms/kong-realm/protocol/openid-connect/certs

# Test with valid token
kc-test token get --user testuser --realm kong-realm
```

## Directory Structure

```
infrastructure/kong/
├── docker-compose.yml              # Service definition
├── .env.example                    # Environment template
├── config/
│   ├── kong.template.yml           # Configuration template
│   ├── instances/
│   │   ├── kong-public.yml         # Public instance
│   │   ├── kong-internal.yml       # Internal instance
│   │   └── README.md               # Instance documentation
│   └── plugins/
│       └── custom/                 # Custom plugins
└── README.md                       # This file
```

## CLI Commands

Using the deployment CLI:

```bash
# Deploy Kong instance
kc-deploy kong --name kong-public --realm kong-realm

# Add new instance
kc-deploy kong add --name kong-api-v2

# List instances
kc-deploy kong list

# Remove instance
kc-deploy kong remove --name kong-api-v2

# Validate configuration
kc-deploy config validate --component kong

# View logs
kc-deploy logs kong --follow
```

## Testing

Using the Python testing CLI:

```bash
# Test API endpoint
kc-test api call --endpoint /api/public

# Run test suite
kc-test suite run --component kong-public

# Get token and test
kc-test token get --user testuser --realm kong-realm
kc-test api test --endpoint /api/protected --token <token>
```

## Examples

### Example 1: Add New Service

```yaml
# Add to your declarative config
services:
  - name: users-api
    url: http://users-service:3000
    routes:
      - name: users-list
        paths: ["/users"]
        methods: [GET]
      - name: users-create
        paths: ["/users"]
        methods: [POST]
        plugins:
          - name: rate-limiting
            config:
              second: 10
```

### Example 2: Enable JWT for Route

```yaml
routes:
  - name: protected-route
    paths: ["/protected"]
    # JWT validation happens automatically
    # Backend extracts claims from validated token
```

### Example 3: Custom Rate Limiting

```yaml
plugins:
  - name: rate-limiting
    route: specific-route
    config:
      second: 5
      minute: 100
      hour: 1000
      policy: local
```

## References

- [Kong Documentation](https://docs.konghq.com/)
- [Kong DB-less Mode](https://docs.konghq.com/gateway/latest/production/deployment-topologies/db-less-and-declarative-config/)
- [Declarative Configuration](https://docs.konghq.com/gateway/latest/production/deployment-topologies/db-less-and-declarative-config/#declarative-configuration)
- [Kong + Keycloak Integration](../../docs/multi-kong-setup.md)

## Support

For issues specific to this component:

1. Check logs: `docker-compose logs kong`
2. Validate config: `kong config parse <file>`
3. Test connectivity: Verify network access to backends
4. Review [Troubleshooting](#troubleshooting) section
5. Consult main project documentation

---

**Component Status**: ✅ Production-ready in DB-less mode
