# Keycloak Realms Configuration

This directory contains Keycloak realm configurations that are automatically imported on startup.

## Available Realms

### kong-realm.json

**Purpose**: Public-facing API authentication

**Configuration**:

- Client: `kong-client` (public client for JWT validation)
- Token lifetime: 5 minutes (300 seconds)
- Roles: `admin`, `user`
- Pre-configured users:
  - `admin` / `admin123` (admin + user roles)
  - `testuser` / `user123` (user role)

**Use case**: External API consumers, mobile apps, web applications

### internal-realm.json

**Purpose**: Internal services and microservices authentication

**Configuration**:

- Client: `kong-internal-client`
- Token lifetime: 10 minutes (600 seconds)
- Roles: `internal-admin`, `internal-user`
- Pre-configured users:
  - `internal-admin` / `internal-admin123`

**Use case**: Service-to-service communication, internal tools

## Creating New Realms

1. **Export from existing Keycloak**:

   ```bash
   # Access Keycloak admin console
   # Navigate to: Realm Settings → Action → Partial Export
   # Select what to export (users, clients, roles, etc.)
   # Download JSON file
   ```

2. **Create from template**:

   ```bash
   # Copy an existing realm and modify
   cp kong-realm.json my-new-realm.json
   # Edit realm name, clients, users, etc.
   ```

3. **Place in this directory**:
   - Keycloak automatically imports `*.json` files from `/opt/keycloak/data/import/realms/`
   - Files in this directory are mounted to that location

## Realm Configuration Best Practices

### Security

- ✅ Use strong passwords for production users
- ✅ Enable brute force protection
- ✅ Set appropriate token lifetimes
- ✅ Use SSL in production (`sslRequired: "all"`)
- ⚠️ Change default user passwords before production deployment

### Token Settings

- **Short-lived tokens**: 5-15 minutes for external APIs
- **Medium-lived tokens**: 15-60 minutes for internal services
- **Session timeout**: Balance security vs. user experience

### Clients

- **Public clients**: For frontend apps, mobile apps (no client secret)
- **Confidential clients**: For backend services (with client secret)
- **Service accounts**: For machine-to-machine communication

## Updating Realms

### Method 1: Update JSON and Restart

1. Edit the realm JSON file
2. Restart Keycloak: `docker-compose restart keycloak`
3. Changes are imported on startup

### Method 2: Admin Console (Runtime Changes)

1. Make changes via Keycloak admin console
2. Export updated realm configuration
3. Save to this directory for persistence

**Note**: Runtime changes not exported to JSON will be lost on container restart.

## Connecting Kong to Realms

Each Kong instance can connect to a different realm:

```yaml
# Kong configuration
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=kong-realm # or internal-realm

# JWKS endpoint for JWT validation
# http://keycloak:8080/realms/kong-realm/protocol/openid-connect/certs
```

## Realm-Specific Use Cases

### Multi-Tenancy

Create separate realms for different tenants:

- `tenant-a-realm.json`
- `tenant-b-realm.json`

Each tenant has isolated users, roles, and clients.

### Environment Separation

Different realms for different environments:

- `dev-realm.json` - Development environment
- `staging-realm.json` - Staging environment
- `prod-realm.json` - Production environment

### API Versioning

Separate realms for API versions:

- `api-v1-realm.json`
- `api-v2-realm.json`

## Testing Realm Configuration

Use the Python testing CLI to validate realm setup:

```bash
# Test token acquisition
kc-test token get --user testuser --realm kong-realm

# List users in realm
kc-test keycloak list-users --realm kong-realm

# Verify client configuration
kc-test keycloak verify-client --realm kong-realm --client kong-client
```

## Troubleshooting

### Realm not importing

- Check JSON syntax: `jq . kong-realm.json`
- Review Keycloak logs: `docker-compose logs keycloak`
- Ensure file is in correct directory and has `.json` extension

### Users not created

- Verify `users` array in JSON
- Check if `enabled: true`
- Ensure passwords are set correctly

### Token issues

- Verify `accessTokenLifespan` setting
- Check client configuration
- Ensure `directAccessGrantsEnabled: true` for password grant

## References

- [Keycloak Server Administration](https://www.keycloak.org/docs/latest/server_admin/)
- [Realm Import/Export](https://www.keycloak.org/docs/latest/server_admin/#_export_import)
- [Client Configuration](https://www.keycloak.org/docs/latest/server_admin/#_clients)
