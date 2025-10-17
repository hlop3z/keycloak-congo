# Quick Start Guide

Get up and running with both CLIs in minutes!

## Prerequisites

- **Python 3.12+** and **uv** (or pip) for Testing CLI
- **Go 1.21+** for Deployment CLI
- **Docker** and **Docker Compose**

## Installation

### 1. Install Testing CLI

```bash
cd tools/testing-cli

# Using uv (recommended)
uv sync

# Or using pip
pip install -e .

# Verify installation
python -m src.cli --help
```

### 2. Install Deployment CLI

```bash
cd tools/deployment-cli

# Build the binary
make build

# Or install to $GOPATH/bin
make install

# Verify installation
kc-deploy --help
```

## Your First Deployment

### Step 1: Initialize Configuration

```bash
# Create default configuration
kc-deploy config init

# Verify it looks good
kc-deploy config show
```

### Step 2: Deploy Services

```bash
# Deploy the full stack (Keycloak + Kong)
kc-deploy deploy full --env dev

# This will take a minute or two...
```

### Step 3: Wait for Services

```bash
# Wait 20 seconds for services to initialize
sleep 20

# Check status
kc-deploy status
```

## Your First Test

### Step 1: Run Comprehensive Tests

```bash
# Run the test suite
cd tools/testing-cli

python -m src.cli suite run \
  --env dev \
  --keycloak-url http://localhost:8080 \
  --kong-url http://localhost:8000
```

### Step 2: Generate a Report

```bash
# Generate an HTML report
python -m src.cli suite run \
  --env dev \
  --format html \
  --output test-report.html

# Open it in your browser
open test-report.html  # macOS
# or
xdg-open test-report.html  # Linux
# or just open the file in Windows
```

### Step 3: Try Token Operations

```bash
# Get a token (will prompt for password)
python -m src.cli token get --user admin --realm master

# The default admin password is usually "admin"
```

## Common Tasks

### Deploy Individual Components

```bash
# Just Keycloak
kc-deploy deploy keycloak

# Just Kong
kc-deploy deploy kong

# Multi-Kong setup
kc-deploy deploy multi-kong
```

### Test Specific Endpoints

```bash
# Test a public endpoint
python -m src.cli api call --endpoint /api/public

# Test with authentication
TOKEN="your-token-here"
python -m src.cli api call --endpoint /api/protected --token "$TOKEN"
```

### Manage Kong Instances

```bash
# List configured instances
kc-deploy kong list

# Add a new instance
kc-deploy kong add --name kong-v2 --realm api-realm --port 8002

# Remove an instance
kc-deploy kong remove --name kong-v2
```

### View Logs

```bash
# Follow Keycloak logs
kc-deploy logs keycloak --follow

# Last 50 lines from Kong
kc-deploy logs kong --tail 50
```

### Stop Services

```bash
# Stop everything
kc-deploy down all

# Stop with volume cleanup
kc-deploy down all --volumes

# Stop just Kong
kc-deploy down kong
```

## Configuration Files

### Testing CLI Config

Create `~/.kc-test.yaml`:

```yaml
keycloak_url: http://localhost:8080
kong_url: http://localhost:8000
default_realm: kong-realm
default_user: testuser
admin_user: admin
```

### Deployment CLI Config

Create `~/.kc-deploy.yaml`:

```yaml
project_root: /path/to/keycloak-congo
default_environment: dev
kong_instances:
  - name: kong-public
    realm: kong-realm
    port: 8000
```

## Complete Workflow Example

Here's a complete workflow from deployment to testing:

```bash
#!/bin/bash
set -e

echo "🚀 Starting Kong + Keycloak Workflow..."

# 1. Initialize and deploy
cd tools/deployment-cli
kc-deploy config init
kc-deploy deploy full --env dev

# 2. Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 25

# 3. Check status
echo "📊 Checking status..."
kc-deploy status

# 4. Run tests
echo "🧪 Running tests..."
cd ../testing-cli
python -m src.cli suite run --env dev

# 5. Generate report
echo "📝 Generating report..."
python -m src.cli suite run \
  --env dev \
  --format html \
  --output ~/test-report.html

echo "✅ Workflow complete!"
echo "   Report: ~/test-report.html"
```

Save this as `workflow.sh`, make it executable (`chmod +x workflow.sh`), and run it!

## Troubleshooting

### Services Won't Start

```bash
# Check Docker is running
docker ps

# Check for port conflicts
sudo lsof -i :8000  # Kong
sudo lsof -i :8080  # Keycloak

# View detailed logs
kc-deploy logs keycloak
kc-deploy logs kong
```

### Tests Fail

```bash
# Verify services are running
kc-deploy status

# Check URLs are correct
curl http://localhost:8080  # Keycloak
curl http://localhost:8000  # Kong

# Try with explicit URLs
python -m src.cli suite run \
  --keycloak-url http://localhost:8080 \
  --kong-url http://localhost:8000
```

### Can't Get Token

```bash
# List users to verify they exist
python -m src.cli keycloak list-users \
  --realm master \
  --admin-user admin

# Check Keycloak logs
kc-deploy logs keycloak --tail 50
```

## Next Steps

1. **Read the full documentation**
   - [tools/README.md](README.md) - Overview
   - [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Detailed examples
2. **Try the example scripts**

   - `testing-cli/examples/test_workflow.sh`
   - `testing-cli/examples/admin_operations.py`
   - `deployment-cli/examples/deploy_workflow.sh`

3. **Customize for your needs**

   - Create your config files
   - Add your own Kong instances
   - Build custom test suites

4. **Integrate with CI/CD**
   - Use in GitHub Actions
   - Jenkins pipelines
   - GitLab CI

## Getting Help

- **Documentation**: Check the README files
- **Examples**: Look at the example scripts
- **Issues**: Create an issue in the repository
- **Verbose Mode**: Use `-v` flag for detailed output

## Quick Reference

### Most Used Testing Commands

```bash
# Get token
kc-test token get --user <user> --realm <realm>

# Test endpoint
kc-test api call --endpoint <path>

# Run suite
kc-test suite run --env dev

# Generate report
kc-test suite run --format html --output report.html

# List users
kc-test keycloak list-users --realm <realm>

# Create user
kc-test keycloak create-user --username <user> --realm <realm>
```

### Most Used Deployment Commands

```bash
# Deploy
kc-deploy deploy full

# Status
kc-deploy status

# Logs
kc-deploy logs <component> -f

# Stop
kc-deploy down all

# Validate
kc-deploy config validate

# Kong instances
kc-deploy kong list
kc-deploy kong add --name <name> --realm <realm> --port <port>
```

---

**Happy Testing and Deploying! 🎉**

For more detailed information, see [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
