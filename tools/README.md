# Kong + Keycloak CLI Tools

This directory contains two command-line tools for managing and testing the Kong + Keycloak integration:

1. **Testing CLI (Python)** - `kc-test` - For testing and validating the integration
2. **Deployment CLI (Go)** - `kc-deploy` - For deploying and managing infrastructure

## Quick Start

### Testing CLI

```bash
cd testing-cli

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .

# Run tests
kc-test suite run --env dev
```

### Deployment CLI

```bash
cd deployment-cli

# Build
make build

# Or install
make install

# Deploy services
kc-deploy deploy full
```

## Tools Overview

### 🧪 Testing CLI (kc-test)

A comprehensive Python-based CLI for testing Kong and Keycloak integration.

**Features:**

- JWT token operations (get, decode, refresh)
- API endpoint testing through Kong
- Keycloak Admin API integration
- Comprehensive test suites
- Multiple report formats (JSON, HTML, Markdown)
- Configuration file support

**Common Commands:**

```bash
# Get a token
kc-test token get --user testuser --realm kong-realm

# Test API endpoint
kc-test api call --endpoint /api/protected --token $TOKEN

# Run comprehensive tests
kc-test suite run --env dev

# Generate report
kc-test suite run --format html --output report.html

# Admin operations
kc-test keycloak list-users --realm kong-realm
kc-test keycloak create-user --username newuser --realm kong-realm
```

📖 **[Full Testing CLI Documentation](testing-cli/README.md)**

---

### 🚀 Deployment CLI (kc-deploy)

A powerful Go-based CLI for deploying and managing the Kong + Keycloak infrastructure.

**Features:**

- Deploy individual components or full stack
- Manage multiple Kong instances
- Configuration validation
- Status and health checks
- Log viewing and monitoring
- Docker Compose integration

**Common Commands:**

```bash
# Deploy services
kc-deploy deploy keycloak
kc-deploy deploy kong
kc-deploy deploy full

# Manage Kong instances
kc-deploy kong add --name kong-v2 --realm api-realm --port 8002
kc-deploy kong list

# Monitor services
kc-deploy status
kc-deploy logs kong --follow

# Stop services
kc-deploy down all
```

📖 **[Full Deployment CLI Documentation](deployment-cli/README.md)**

---

## Installation

### Prerequisites

**Testing CLI:**

- Python 3.12+
- uv (recommended) or pip

**Deployment CLI:**

- Go 1.21+
- Docker & Docker Compose
- Make (optional)

### Install Both Tools

```bash
# Testing CLI
cd testing-cli
uv sync  # or: pip install -e .

# Deployment CLI
cd deployment-cli
make install
```

## Usage Examples

See **[USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)** for comprehensive examples including:

- Complete testing workflows
- Deployment workflows
- Multi-instance Kong setup
- CI/CD integration
- Troubleshooting guides

## Project Structure

```
tools/
├── testing-cli/              # Python testing CLI
│   ├── src/
│   │   ├── cli.py           # Main CLI entry point
│   │   ├── keycloak_client.py  # Keycloak integration
│   │   ├── api_tester.py    # API testing utilities
│   │   ├── reporter.py      # Report generation
│   │   └── config.py        # Configuration handling
│   ├── examples/            # Example scripts
│   ├── tests/               # Test suite
│   ├── pyproject.toml       # Python project config
│   └── README.md            # Testing CLI docs
│
├── deployment-cli/          # Go deployment CLI
│   ├── cmd/                 # Cobra commands
│   │   ├── root.go         # Root command
│   │   ├── deploy.go       # Deploy commands
│   │   ├── kong.go         # Kong management
│   │   ├── status.go       # Status commands
│   │   ├── logs.go         # Log viewing
│   │   ├── down.go         # Stop commands
│   │   └── configcmd.go    # Config commands
│   ├── pkg/                 # Go packages
│   │   ├── docker/         # Docker Compose integration
│   │   ├── config/         # Configuration handling
│   │   └── validate/       # Validation logic
│   ├── examples/           # Example scripts
│   ├── go.mod              # Go module definition
│   ├── Makefile            # Build automation
│   └── README.md           # Deployment CLI docs
│
├── USAGE_EXAMPLES.md        # Comprehensive usage guide
└── README.md                # This file
```

## Configuration Files

### Testing CLI

`~/.kc-test.yaml`:

```yaml
keycloak_url: http://localhost:8080
kong_url: http://localhost:8000
default_realm: kong-realm
default_user: testuser
client_id: kong-client
admin_user: admin
```

### Deployment CLI

`~/.kc-deploy.yaml`:

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
```

## Development

### Testing CLI Development

```bash
cd testing-cli

# Run tests
pytest

# Format code
black src/

# Lint
ruff check src/

# Install dev dependencies
uv sync --dev
```

### Deployment CLI Development

```bash
cd deployment-cli

# Run tests
make test

# Build
make build

# Run linter
make lint

# Clean build artifacts
make clean
```

## Complete Workflow Example

Here's a complete workflow using both CLIs:

```bash
# 1. Deploy the infrastructure
kc-deploy config init
kc-deploy deploy full --env dev

# 2. Wait for services to be ready
sleep 20

# 3. Check status
kc-deploy status

# 4. Run comprehensive tests
kc-test suite run --env dev --format html --output test-report.html

# 5. Perform admin operations
kc-test keycloak create-user --username apiuser --realm kong-realm
kc-test keycloak assign-role --username apiuser --role admin

# 6. Test with new user
kc-test token get --user apiuser --realm kong-realm

# 7. Monitor logs
kc-deploy logs kong --tail 50

# 8. When done, stop services
kc-deploy down all
```

## CI/CD Integration

Both CLIs are designed for CI/CD integration:

```yaml
# Example GitHub Actions workflow
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      # Deploy services
      - name: Deploy services
        run: |
          kc-deploy deploy full --env ci
          sleep 20

      # Run tests
      - name: Run tests
        run: |
          kc-test suite run --env ci --format json --output results.json

      # Generate report
      - name: Generate report
        run: |
          kc-test report generate --input results.json --format html --output report.html

      # Upload artifacts
      - uses: actions/upload-artifact@v2
        with:
          name: test-report
          path: report.html

      # Cleanup
      - name: Cleanup
        if: always()
        run: kc-deploy down all --volumes
```

## Troubleshooting

### Testing CLI

**Issue: Cannot connect to Keycloak**

```bash
# Check Keycloak is running
curl http://localhost:8080

# Verify configuration
cat ~/.kc-test.yaml
```

**Issue: Token acquisition fails**

```bash
# Check user exists and credentials are correct
kc-test keycloak list-users --realm kong-realm
```

### Deployment CLI

**Issue: Docker compose fails**

```bash
# Verify Docker is running
docker ps

# Check compose files
kc-deploy config validate

# View logs
kc-deploy logs keycloak --tail 100
```

**Issue: Port already in use**

```bash
# Check what's using the port
sudo lsof -i :8000

# Modify port in config
kc-deploy kong add --name kong-custom --port 8888
```

## Environment Variables

### Testing CLI

- `KC_TEST_KEYCLOAK_URL`: Default Keycloak URL
- `KC_TEST_KONG_URL`: Default Kong URL
- `KC_TEST_REALM`: Default realm name

### Deployment CLI

- `KC_DEPLOY_CONFIG`: Override config file path
- `KC_DEPLOY_ENV`: Default environment
- `KC_DEPLOY_VERBOSE`: Enable verbose output
- `KC_DEPLOY_PROJECT_ROOT`: Override project root

## Contributing

### Adding New Commands

**Testing CLI:**

1. Add command to `src/cli.py`
2. Implement logic in appropriate module
3. Add tests
4. Update README

**Deployment CLI:**

1. Create new file in `cmd/`
2. Implement Cobra command
3. Register in `root.go`
4. Add tests
5. Update README

## Performance Tips

1. **Use configuration files** to avoid repeated URL specifications
2. **Run tests in parallel** when possible
3. **Cache tokens** for multiple API calls
4. **Use `--tail` flag** when viewing logs to limit output
5. **Enable verbose mode** only when debugging

## Security Considerations

1. **Never commit passwords** or tokens to version control
2. **Use environment variables** for sensitive data in CI/CD
3. **Rotate admin credentials** regularly
4. **Use HTTPS** in production environments
5. **Limit token lifetimes** appropriately

## Support

For issues, questions, or contributions:

- **Issues**: Create an issue in the main repository
- **Documentation**: See individual tool READMEs
- **Examples**: Check `examples/` directories and USAGE_EXAMPLES.md

## License

MIT License - See [LICENSE](../LICENSE)

---

**Status**: ✅ Both CLIs fully implemented and production-ready

**Last Updated**: October 2024
