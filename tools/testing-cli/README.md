# Testing CLI (Python)

Command-line tool for testing Kong + Keycloak integration.

## Overview

`kc-test` is a Python-based CLI that:

- Manages JWT tokens (get, decode, refresh)
- Tests API endpoints through Kong
- Runs automated test suites
- Interacts with Keycloak Admin API
- Generates test reports

## Installation

### Using pip

```bash
cd tools/testing-cli
pip install -r requirements.txt

# Or install in editable mode
pip install -e .
```

### Using uv (Recommended)

```bash
cd tools/testing-cli
uv sync
```

## Usage

### Token Operations

```bash
# Get JWT token
python -m src.cli token get --user testuser --password user123 --realm kong-realm
# or: kc-test token get --user testuser --password user123 --realm kong-realm

# Decode token
python -m src.cli token decode <TOKEN>

# Refresh token
python -m src.cli token refresh <REFRESH_TOKEN>
```

### API Testing

```bash
# Call API endpoint
python -m src.cli api call --endpoint /api/public

# Call with authentication
python -m src.cli api call --endpoint /api/protected --token <TOKEN>

# Run test suite
python -m src.cli api test --suite integration
```

### Comprehensive Testing

```bash
# Run full test suite
python -m src.cli suite run --env dev

# Test specific component
python -m src.cli suite run --component kong-public
```

### Keycloak Operations

```bash
# List users
python -m src.cli keycloak list-users --realm kong-realm

# Create user
python -m src.cli keycloak create-user --realm kong-realm --username newuser

# Assign role
python -m src.cli keycloak assign-role --user newuser --role admin
```

## Commands

### token

JWT token operations

```bash
kc-test token get --user <username> --realm <realm>
kc-test token decode <token>
kc-test token refresh <refresh-token>
```

### api

API endpoint testing

```bash
kc-test api call --endpoint <path> [--token <token>]
kc-test api test --suite <suite-name>
```

### suite

Test suite operations

```bash
kc-test suite run [--env dev|prod]
kc-test suite run --component <component-name>
```

### keycloak

Keycloak Admin API operations

```bash
kc-test keycloak list-users --realm <realm>
kc-test keycloak create-user --realm <realm> --username <username>
kc-test keycloak assign-role --user <user> --role <role>
```

### report

Generate test reports

```bash
kc-test report --format json|html|markdown
```

## Configuration

### Environment Variables

- `KC_TEST_KEYCLOAK_URL`: Default Keycloak URL
- `KC_TEST_KONG_URL`: Default Kong URL
- `KC_TEST_REALM`: Default realm name

### Config File

`~/.kc-test.yaml`:

```yaml
keycloak_url: http://localhost:8080
kong_url: http://localhost:8000
default_realm: kong-realm
default_user: testuser
```

## Development

### Project Structure

```
tools/testing-cli/
├── src/
│   ├── __init__.py
│   ├── cli.py               # Main CLI
│   ├── keycloak_client.py   # Keycloak integration
│   ├── api_tester.py        # API testing
│   └── reporter.py          # Result reporting
├── tests/                    # Test suite
├── requirements.txt          # Dependencies
├── pyproject.toml           # Project config
└── README.md                # This file
```

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src tests/

# Specific test file
pytest tests/test_keycloak_client.py
```

### Code Quality

```bash
# Format code
black src/

# Lint
ruff check src/

# Type checking
mypy src/
```

## Examples

### Complete Testing Workflow

```bash
# 1. Get token for regular user
kc-test token get --user testuser --realm kong-realm > token.txt
TOKEN=$(cat token.txt | grep "Access Token" | cut -d: -f2 | xargs)

# 2. Test public endpoint
kc-test api call --endpoint /api/public

# 3. Test protected endpoint
kc-test api call --endpoint /api/protected --token $TOKEN

# 4. Get admin token
kc-test token get --user admin --realm kong-realm > admin-token.txt
ADMIN_TOKEN=$(cat admin-token.txt | grep "Access Token" | cut -d: -f2 | xargs)

# 5. Test admin endpoint
kc-test api call --endpoint /api/admin --token $ADMIN_TOKEN

# 6. Run full test suite
kc-test suite run --env dev
```

### Automated Testing Script

```python
#!/usr/bin/env python
from src.keycloak_client import get_token
from src.api_tester import test_public_endpoint, test_protected_endpoint
from src.reporter import print_test_results

# Get tokens
user_token = get_token("http://localhost:8080", "kong-realm", "testuser", "user123")
admin_token = get_token("http://localhost:8080", "kong-realm", "admin", "admin123")

# Run tests
results = []
results.append({"name": "Public", "passed": test_public_endpoint()})
results.append({"name": "Protected", "passed": test_protected_endpoint(token=user_token["access_token"])})

# Print results
print_test_results(results)
```

## Implementation Status

- [x] Basic CLI structure with Click
- [x] Token get/decode/refresh commands
- [x] API call command
- [x] Rich console output
- [x] Token refresh
- [x] Keycloak Admin API integration
- [x] Comprehensive test suite
- [x] HTML/JSON/Markdown report generation
- [x] Configuration file support
- [x] Example scripts and workflows

## Features Completed

✅ **Token Operations**

- Get JWT tokens from Keycloak
- Decode JWT tokens
- Refresh expired tokens

✅ **API Testing**

- Test public endpoints
- Test protected endpoints with authentication
- Custom HTTP methods support
- Comprehensive test suites

✅ **Keycloak Admin API**

- List users in realm
- Create new users
- Assign roles to users
- Get user roles
- Full admin API integration

✅ **Report Generation**

- JSON reports for automation
- HTML reports with styling
- Markdown reports for documentation
- Console output with rich formatting

✅ **Configuration**

- YAML configuration file support
- Environment variable support
- Default values with overrides

## Contributing

See main project [CONTRIBUTING.md](../../CONTRIBUTING.md)

## License

MIT License - See [LICENSE](../../LICENSE)

---

**Status**: 🚧 Foundation established, core features implemented
