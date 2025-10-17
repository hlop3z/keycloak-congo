# CLI Tools Usage Examples

This document provides comprehensive examples for using the testing and deployment CLIs.

## Table of Contents

- [Testing CLI (kc-test)](#testing-cli-kc-test)
  - [Basic Token Operations](#basic-token-operations)
  - [API Testing](#api-testing)
  - [Keycloak Admin Operations](#keycloak-admin-operations)
  - [Comprehensive Testing](#comprehensive-testing)
  - [Report Generation](#report-generation)
- [Deployment CLI (kc-deploy)](#deployment-cli-kc-deploy)
  - [Basic Deployment](#basic-deployment)
  - [Kong Instance Management](#kong-instance-management)
  - [Status and Monitoring](#status-and-monitoring)
  - [Configuration Management](#configuration-management)

---

## Testing CLI (kc-test)

### Installation

Using uv (recommended):

```bash
cd tools/testing-cli
uv sync
```

Using pip:

```bash
cd tools/testing-cli
pip install -e .
```

### Basic Token Operations

#### Get a JWT token

```bash
# Interactive password prompt
kc-test token get --user testuser --realm kong-realm

# With custom Keycloak URL
kc-test token get \
  --user testuser \
  --realm kong-realm \
  --keycloak-url http://localhost:8080
```

#### Decode a JWT token

```bash
kc-test token decode eyJhbGciOiJSUzI1NiIsInR5cCI...
```

#### Refresh a JWT token

```bash
kc-test token refresh eyJhbGciOiJSUzI1NiIsInR5cCI... \
  --realm kong-realm \
  --keycloak-url http://localhost:8080
```

### API Testing

#### Call a public endpoint

```bash
kc-test api call --endpoint /api/public
```

#### Call a protected endpoint with token

```bash
# First get a token
TOKEN=$(kc-test token get --user testuser --realm kong-realm | grep "Access Token" | cut -d: -f2 | xargs)

# Then use it
kc-test api call \
  --endpoint /api/protected \
  --token "$TOKEN"
```

#### Call with different HTTP methods

```bash
kc-test api call \
  --endpoint /api/users \
  --method POST \
  --token "$TOKEN"
```

### Keycloak Admin Operations

#### List users in a realm

```bash
kc-test keycloak list-users \
  --realm kong-realm \
  --keycloak-url http://localhost:8080 \
  --admin-user admin
```

#### Create a new user

```bash
kc-test keycloak create-user \
  --realm kong-realm \
  --username newuser \
  --email newuser@example.com \
  --keycloak-url http://localhost:8080 \
  --admin-user admin
```

#### Assign a role to a user

```bash
kc-test keycloak assign-role \
  --realm kong-realm \
  --username newuser \
  --role admin \
  --keycloak-url http://localhost:8080 \
  --admin-user admin
```

### Comprehensive Testing

#### Run full test suite

```bash
# Console output
kc-test suite run --env dev

# With custom URLs
kc-test suite run \
  --env dev \
  --keycloak-url http://localhost:8080 \
  --kong-url http://localhost:8000
```

#### Generate JSON report

```bash
kc-test suite run \
  --env dev \
  --format json \
  --output test-results.json
```

#### Generate HTML report

```bash
kc-test suite run \
  --env dev \
  --format html \
  --output test-report.html
```

#### Generate Markdown report

```bash
kc-test suite run \
  --env dev \
  --format markdown \
  --output test-report.md
```

### Report Generation

#### Generate report from existing results

```bash
kc-test report generate \
  --input test-results.json \
  --format html \
  --output report.html
```

### Configuration File

Create `~/.kc-test.yaml`:

```yaml
keycloak_url: http://localhost:8080
kong_url: http://localhost:8000
default_realm: kong-realm
default_user: testuser
client_id: kong-client
admin_user: admin
```

Then use without specifying URLs:

```bash
kc-test token get --user testuser  # Uses config file values
```

---

## Deployment CLI (kc-deploy)

### Installation

```bash
cd tools/deployment-cli

# Install dependencies
go mod download

# Build binary
make build

# Or install to $GOPATH/bin
make install
```

### Basic Deployment

#### Initialize configuration

```bash
kc-deploy config init
```

#### Deploy Keycloak

```bash
kc-deploy deploy keycloak
```

#### Deploy Kong

```bash
kc-deploy deploy kong
```

#### Deploy full stack

```bash
kc-deploy deploy full --env dev
```

#### Deploy multi-Kong setup

```bash
kc-deploy deploy multi-kong
```

### Kong Instance Management

#### List Kong instances

```bash
kc-deploy kong list
```

#### Add a Kong instance

```bash
kc-deploy kong add \
  --name kong-api-v2 \
  --realm api-v2-realm \
  --port 8002
```

#### Remove a Kong instance

```bash
kc-deploy kong remove --name kong-api-v2
```

### Status and Monitoring

#### Check status of all components

```bash
kc-deploy status
```

#### Check status of specific component

```bash
kc-deploy status keycloak
kc-deploy status kong
kc-deploy status full
```

#### View logs

```bash
# Follow logs
kc-deploy logs keycloak --follow

# Show last 50 lines
kc-deploy logs kong --tail 50

# Specific service
kc-deploy logs keycloak keycloak --follow
```

#### Health check

```bash
kc-deploy health
```

### Stopping Services

#### Stop specific component

```bash
kc-deploy down keycloak
```

#### Stop all components

```bash
kc-deploy down all
```

#### Stop with volume removal

```bash
kc-deploy down keycloak --volumes
kc-deploy down all --volumes
```

### Configuration Management

#### Validate configuration

```bash
kc-deploy config validate
```

#### Show current configuration

```bash
kc-deploy config show
```

#### Initialize default configuration

```bash
kc-deploy config init
```

### Configuration File

Create `~/.kc-deploy.yaml`:

```yaml
project_root: /path/to/keycloak-congo
default_environment: dev
kong_instances:
  - name: kong-public
    realm: kong-realm
    port: 8000
  - name: kong-internal
    realm: internal-realm
    port: 9000
  - name: kong-api-v1
    realm: api-v1-realm
    port: 8001
```

### Environment Variables

```bash
# Override config file location
export KC_DEPLOY_CONFIG=/path/to/config.yaml

# Set default environment
export KC_DEPLOY_ENV=prod

# Enable verbose output
export KC_DEPLOY_VERBOSE=true

# Set project root
export KC_DEPLOY_PROJECT_ROOT=/path/to/project
```

---

## Complete Workflow Examples

### Testing Workflow

```bash
#!/bin/bash
# Complete testing workflow

# 1. Run comprehensive test suite
kc-test suite run --env dev --format json --output results.json

# 2. Generate HTML report
kc-test report generate --input results.json --format html --output report.html

# 3. Get admin token
kc-test token get --user admin --realm kong-realm

# 4. List all users
kc-test keycloak list-users --realm kong-realm --admin-user admin

# 5. Create test user
kc-test keycloak create-user \
  --realm kong-realm \
  --username testapi \
  --email testapi@example.com \
  --admin-user admin

# 6. Assign role
kc-test keycloak assign-role \
  --realm kong-realm \
  --username testapi \
  --role user \
  --admin-user admin

# 7. Test with new user
kc-test token get --user testapi --realm kong-realm

echo "✓ Testing workflow completed!"
```

### Deployment Workflow

```bash
#!/bin/bash
# Complete deployment workflow

# 1. Initialize configuration
kc-deploy config init

# 2. Validate setup
kc-deploy config validate

# 3. Deploy Keycloak
kc-deploy deploy keycloak
sleep 15  # Wait for Keycloak to be ready

# 4. Deploy Kong
kc-deploy deploy kong
sleep 10  # Wait for Kong to be ready

# 5. Check status
kc-deploy status

# 6. View logs to verify
kc-deploy logs keycloak --tail 20
kc-deploy logs kong --tail 20

echo "✓ Deployment workflow completed!"
```

### Multi-Instance Setup

```bash
#!/bin/bash
# Setup multiple Kong instances

# 1. Add Kong instances
kc-deploy kong add --name kong-v1 --realm realm-v1 --port 8001
kc-deploy kong add --name kong-v2 --realm realm-v2 --port 8002
kc-deploy kong add --name kong-v3 --realm realm-v3 --port 8003

# 2. List instances
kc-deploy kong list

# 3. Deploy multi-Kong
kc-deploy deploy multi-kong

# 4. Check status
kc-deploy status multi-kong

echo "✓ Multi-Kong setup completed!"
```

### CI/CD Integration

```bash
#!/bin/bash
# CI/CD pipeline example

set -e

echo "Starting CI/CD pipeline..."

# Deploy services
kc-deploy deploy full --env ci

# Wait for services
sleep 20

# Run tests
kc-test suite run \
  --env ci \
  --keycloak-url http://localhost:8080 \
  --kong-url http://localhost:8000 \
  --format json \
  --output ci-results.json

# Generate reports
kc-test report generate \
  --input ci-results.json \
  --format html \
  --output ci-report.html

# Check if tests passed
if [ $? -eq 0 ]; then
    echo "✓ All tests passed!"
    exit 0
else
    echo "✗ Tests failed!"
    kc-deploy logs kong --tail 100
    kc-deploy logs keycloak --tail 100
    exit 1
fi
```

---

## Troubleshooting

### Testing CLI Issues

**Token acquisition fails:**

```bash
# Check Keycloak is running
curl http://localhost:8080

# Verify realm exists
# Check user credentials
```

**API calls fail:**

```bash
# Check Kong is running
curl http://localhost:8000

# Verify routes are configured
# Check token is valid (not expired)
```

### Deployment CLI Issues

**Docker compose fails:**

```bash
# Verify Docker is running
docker ps

# Check compose files exist
kc-deploy config validate

# Check logs
kc-deploy logs keycloak
```

**Port conflicts:**

```bash
# Change ports in config
kc-deploy config show

# Or in ~/.kc-deploy.yaml
```

---

## Tips and Best Practices

1. **Use configuration files** to avoid typing URLs repeatedly
2. **Generate reports** for documentation and tracking
3. **Automate workflows** with shell scripts
4. **Monitor logs** regularly during development
5. **Validate configs** before deploying
6. **Use verbose mode** (`-v`) when debugging
7. **Stop services** with `--volumes` flag to clean up completely
8. **Create multiple Kong instances** for different API versions

---

## Additional Resources

- [Testing CLI README](testing-cli/README.md)
- [Deployment CLI README](deployment-cli/README.md)
- [Main Project Documentation](../README.md)
- [Architecture Documentation](../docs/architecture.md)
