# Deployment CLI (Go)

Command-line tool for deploying and managing Kong + Keycloak infrastructure.

## Overview

`kc-deploy` is a Go-based CLI that:

- Deploys individual components or full stack
- Manages multiple Kong instances
- Validates configurations
- Provides status and health checks
- Executes docker-compose programmatically

## Installation

### Build from Source

```bash
# Install dependencies
make deps

# Build binary
make build

# Install to $GOPATH/bin
make install
```

### Cross-Platform Build

```bash
# Build for all platforms
make build-all

# Build specific platform
make build-linux
make build-windows
make build-darwin
```

## Usage

### Deploy Components

```bash
# Deploy full stack
kc-deploy deploy full --env dev

# Deploy Keycloak only
kc-deploy deploy keycloak

# Deploy Kong instance
kc-deploy deploy kong --name kong-public --realm kong-realm
```

### Manage Kong Instances

```bash
# Add new Kong instance
kc-deploy kong add --name kong-api-v2 --realm api-v2-realm

# List Kong instances
kc-deploy kong list

# Remove Kong instance
kc-deploy kong remove --name kong-api-v2
```

### Configuration Management

```bash
# Validate configuration
kc-deploy config validate

# Generate template
kc-deploy config template --component kong --output config.yml

# Create new realm configuration
kc-deploy config realm create --name new-realm
```

### Status and Logs

```bash
# Check status
kc-deploy status

# Component status
kc-deploy status kong

# View logs
kc-deploy logs kong --follow

# Health check
kc-deploy health
```

## Commands

### deploy

Deploy components

```bash
kc-deploy deploy [component] [flags]
```

**Components**: keycloak, kong, full, multi-kong

**Flags**:

- `--env string`: Environment (dev/prod)
- `--config string`: Custom config file

### kong

Manage Kong instances

```bash
kc-deploy kong [subcommand]
```

**Subcommands**:

- `add`: Add new Kong instance
- `remove`: Remove Kong instance
- `list`: List all instances
- `update`: Update instance configuration

### config

Configuration management

```bash
kc-deploy config [subcommand]
```

**Subcommands**:

- `validate`: Validate configuration files
- `template`: Generate configuration template
- `realm`: Manage Keycloak realm configurations

### status

View component status

```bash
kc-deploy status [component]
```

### logs

View logs

```bash
kc-deploy logs [component] [flags]
```

**Flags**:

- `--follow, -f`: Follow log output

### down

Stop components

```bash
kc-deploy down [component|all]
```

## Configuration

### Config File

Default: `$HOME/.kc-deploy.yaml`

```yaml
# kc-deploy configuration
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

### Environment Variables

- `KC_DEPLOY_CONFIG`: Override config file path
- `KC_DEPLOY_ENV`: Default environment
- `KC_DEPLOY_VERBOSE`: Enable verbose output

## Development

### Project Structure

```
tools/deployment-cli/
├── cmd/                    # Cobra commands
│   ├── root.go            # Root command
│   ├── deploy.go          # Deploy command
│   ├── kong.go            # Kong management
│   ├── config.go          # Config management
│   └── status.go          # Status commands
├── pkg/                    # Packages
│   ├── config/            # Configuration handling
│   ├── docker/            # Docker Compose integration
│   ├── template/          # Template rendering
│   └── validate/          # Validation logic
├── main.go                # Entry point
├── go.mod                 # Dependencies
├── Makefile               # Build automation
└── README.md              # This file
```

### Adding Commands

1. Create new command file in `cmd/`
2. Implement command logic
3. Register in `root.go`
4. Update README

### Testing

```bash
# Run tests
make test

# Test specific package
go test ./pkg/config/...
```

## Implementation Status

- [x] Basic CLI structure with Cobra
- [x] Root command and help
- [x] Deploy command implementation (full, keycloak, kong, multi-kong)
- [x] Kong instance management (add, remove, list)
- [x] Configuration validation
- [x] Docker Compose integration
- [x] Status and health checks
- [x] Logs viewing
- [x] Down/stop commands
- [x] Configuration management
- [x] Example scripts and workflows

## Features Completed

✅ **Deployment Commands**

- Deploy Keycloak infrastructure
- Deploy Kong gateway
- Deploy full stack
- Deploy multi-Kong instances
- Environment-specific deployments

✅ **Kong Instance Management**

- Add new Kong instances
- Remove Kong instances
- List configured instances
- Per-instance configuration

✅ **Docker Compose Integration**

- Programmatic docker-compose execution
- Support for up, down, logs, status
- Service-specific operations
- Volume management

✅ **Monitoring & Management**

- Status checking for all components
- Log viewing with follow mode
- Health checks
- Service restart/stop

✅ **Configuration**

- YAML configuration files
- Configuration validation
- Project structure validation
- Default config generation

## Contributing

See main project [CONTRIBUTING.md](../../CONTRIBUTING.md)

## License

MIT License - See [LICENSE](../../LICENSE)

---

**Status**: 🚧 Foundation established, implementation in progress
