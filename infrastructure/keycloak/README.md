# Keycloak Identity and Access Management

Standalone Keycloak deployment with PostgreSQL backend and automatic realm import.

## Overview

This component provides:

- ✅ Keycloak 24.0 with PostgreSQL persistence
- ✅ Automatic realm import from configuration files
- ✅ Health checks and monitoring
- ✅ Independent deployment capability
- ✅ Pre-configured realms for Kong integration

## Quick Start

### 1. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and set secure passwords
nano .env
```

**Required variables**:

- `POSTGRES_PASSWORD` - Database password
- `KEYCLOAK_ADMIN_PASSWORD` - Admin console password

### 2. Deploy

```bash
# Start Keycloak + PostgreSQL
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f keycloak
```

### 3. Access Admin Console

- URL: http://localhost:8080
- Username: `admin` (or value from `.env`)
- Password: Value from `KEYCLOAK_ADMIN_PASSWORD`

## Configuration

### Environment Variables

| Variable                  | Default      | Description                             |
| ------------------------- | ------------ | --------------------------------------- |
| `POSTGRES_DB`             | keycloak     | Database name                           |
| `POSTGRES_USER`           | keycloak     | Database user                           |
| `POSTGRES_PASSWORD`       | **required** | Database password                       |
| `KEYCLOAK_ADMIN`          | admin        | Admin username                          |
| `KEYCLOAK_ADMIN_PASSWORD` | **required** | Admin password                          |
| `KEYCLOAK_PORT`           | 8080         | Exposed port                            |
| `KC_HOSTNAME`             | localhost    | Keycloak hostname                       |
| `KC_PROXY`                | edge         | Proxy mode (edge/reencrypt/passthrough) |

### Realms

Realms are automatically imported from `config/realms/*.json`.

**Pre-configured realms**:

- `kong-realm` - Public API authentication
- `internal-realm` - Internal services authentication

See [config/realms/README.md](config/realms/README.md) for details.

### Adding New Realms

1. Create JSON file in `config/realms/`:

   ```bash
   cp config/realms/kong-realm.json config/realms/my-realm.json
   ```

2. Edit realm configuration:

   - Change `realm` name
   - Configure clients
   - Add users and roles

3. Restart Keycloak:
   ```bash
   docker-compose restart keycloak
   ```

## Usage

### Standalone Deployment

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Stop and remove data
docker-compose down -v
```

### Integration with Kong

Kong instances connect to Keycloak realms for JWT validation:

```yaml
# Kong environment
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=kong-realm
```

### Testing Token Generation

```bash
# Using Python CLI (recommended)
kc-test token get --user testuser --realm kong-realm

# Using curl
curl -X POST 'http://localhost:8080/realms/kong-realm/protocol/openid-connect/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=testuser' \
  -d 'password=user123' \
  -d 'grant_type=password' \
  -d 'client_id=kong-client'
```

## Management

### User Management

```bash
# Using Python CLI
kc-test keycloak create-user --realm kong-realm --username newuser
kc-test keycloak list-users --realm kong-realm
kc-test keycloak assign-role --user newuser --role admin
```

### Backup and Restore

**Backup**:

```bash
# Backup PostgreSQL database
docker-compose exec postgres pg_dump -U keycloak keycloak > backup.sql

# Or backup entire volume
docker run --rm -v keycloak-postgres-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/keycloak-data.tar.gz /data
```

**Restore**:

```bash
# Restore from SQL dump
cat backup.sql | docker-compose exec -T postgres psql -U keycloak keycloak

# Or restore volume
docker run --rm -v keycloak-postgres-data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/keycloak-data.tar.gz -C /
```

## Networking

### Default Network

- **Network**: `keycloak-internal`
- **Type**: Bridge
- **Purpose**: Isolate Keycloak and PostgreSQL

### Exposing to Kong

When deploying with Kong, add Keycloak to Kong's network:

```yaml
# In composition layer
services:
  keycloak:
    networks:
      - keycloak-internal
      - kong-network # Added for Kong access
```

## Health and Monitoring

### Health Checks

- **PostgreSQL**: `pg_isready` command
- **Keycloak**: HTTP check on `/health/ready` endpoint

### Monitoring Endpoints

- Health: `http://localhost:8080/health`
- Ready: `http://localhost:8080/health/ready`
- Metrics: `http://localhost:8080/metrics` (if enabled)

### Logs

```bash
# View all logs
docker-compose logs -f

# Keycloak only
docker-compose logs -f keycloak

# PostgreSQL only
docker-compose logs -f postgres
```

## Production Considerations

### Security

1. **Change default passwords**:

   ```bash
   # Generate secure passwords
   openssl rand -base64 32
   ```

2. **Enable SSL/TLS**:

   ```yaml
   KC_HOSTNAME_STRICT: "true"
   KC_HOSTNAME_STRICT_HTTPS: "true"
   KC_HTTPS_CERTIFICATE_FILE: /opt/keycloak/conf/cert.pem
   KC_HTTPS_CERTIFICATE_KEY_FILE: /opt/keycloak/conf/key.pem
   ```

3. **Use production mode**:

   ```yaml
   command:
     - start
     - --optimized
     - --import-realm
   ```

4. **Restrict admin access**:
   - Use firewall rules
   - VPN for admin console access
   - Strong admin passwords
   - Enable MFA

### Performance

1. **Database tuning**:

   ```yaml
   command:
     - postgres
     - -c
     - shared_buffers=256MB
     - -c
     - max_connections=200
   ```

2. **Resource limits**:

   ```yaml
   deploy:
     resources:
       limits:
         cpus: "2"
         memory: 2G
   ```

3. **Connection pooling**: Configure in Keycloak datasource

### High Availability

- Deploy multiple Keycloak instances
- Use PostgreSQL replication
- Load balancer for Keycloak instances
- Shared cache configuration (Infinispan)

## Troubleshooting

### Keycloak won't start

```bash
# Check logs
docker-compose logs keycloak

# Common issues:
# - Database not ready: Wait for PostgreSQL health check
# - Port conflict: Change KEYCLOAK_PORT
# - Invalid realm JSON: Validate with `jq . config/realms/*.json`
```

### Realm not importing

```bash
# Verify JSON syntax
jq . config/realms/kong-realm.json

# Check file is mounted
docker-compose exec keycloak ls -la /opt/keycloak/data/import/realms/

# Review import logs
docker-compose logs keycloak | grep import
```

### Connection refused

```bash
# Check if services are running
docker-compose ps

# Verify network connectivity
docker-compose exec keycloak ping postgres

# Check port mapping
docker-compose port keycloak 8080
```

### Performance issues

```bash
# Check resource usage
docker stats

# Review database connections
docker-compose exec postgres psql -U keycloak -c "SELECT count(*) FROM pg_stat_activity;"

# Enable query logging
docker-compose exec postgres psql -U keycloak -c "ALTER SYSTEM SET log_statement = 'all';"
```

## Directory Structure

```
infrastructure/keycloak/
├── docker-compose.yml              # Service definition
├── .env.example                    # Environment template
├── config/
│   ├── realms/
│   │   ├── kong-realm.json         # Public realm
│   │   ├── internal-realm.json     # Internal realm
│   │   └── README.md               # Realm documentation
│   └── keycloak.conf.template      # Optional: Keycloak config
└── README.md                       # This file
```

## References

- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [Keycloak on Docker](https://www.keycloak.org/server/containers)
- [PostgreSQL Docker](https://hub.docker.com/_/postgres)
- [Kong + Keycloak Integration](../../docs/multi-kong-setup.md)

## Support

For issues specific to this component:

1. Check logs: `docker-compose logs`
2. Verify configuration: Review `.env` and realm JSON files
3. Test connectivity: Ensure PostgreSQL is accessible
4. Review [Troubleshooting](#troubleshooting) section
5. Consult main project documentation

---

**Component Status**: ✅ Production-ready with proper configuration
