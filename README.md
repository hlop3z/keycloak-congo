# Kong + Keycloak Modular Architecture

Production-ready, modular system where Kong API Gateway instances connect to Keycloak realms for JWT validation, with independent, scalable components and CLI automation.

## 🎯 Overview

This project provides:

- ✅ **Modular Components**: Keycloak, Kong, and Backend can be deployed independently
- ✅ **Multi-Kong Support**: Run multiple Kong instances with different Keycloak realms
- ✅ **CLI Automation**: Go deployment CLI and Python testing CLI (no shell scripts!)
- ✅ **Configuration as Code**: All settings in version-controlled files
- ✅ **Production-Ready**: Security, monitoring, and HA considerations built-in

## 🚀 Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Go 1.21+ (for building deployment CLI)
- Python 3.12+ (for testing CLI)

### Deploy Full Stack

```bash
# Copy environment configuration
cp compose/environments/dev.env.example compose/environments/dev.env

# Deploy all components
docker-compose -f compose/docker-compose.full.yml \
  --env-file compose/environments/dev.env up -d

# Verify services
docker-compose -f compose/docker-compose.full.yml ps
```

### Test the Setup

```bash
# Test public endpoint
curl http://localhost:8000/api/public

# Get JWT token from Keycloak
curl -X POST 'http://localhost:8080/realms/kong-realm/protocol/openid-connect/token' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=testuser' \
  -d 'password=user123' \
  -d 'grant_type=password' \
  -d 'client_id=kong-client'

# Test protected endpoint with token
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/api/protected
```

## 📁 Project Structure

```
keycloak-congo/
├── infrastructure/              # Core infrastructure components
│   ├── keycloak/               # Keycloak + PostgreSQL (standalone)
│   └── kong/                   # Kong Gateway (standalone, multi-instance)
├── applications/                # Application services
│   └── backend-demo/           # FastAPI demo (standalone)
├── compose/                     # Composition layer
│   ├── docker-compose.full.yml              # All components
│   ├── docker-compose.multi-kong.yml        # Multi-Kong setup
│   └── environments/                        # Environment configs
├── tools/                       # Automation tools
│   ├── deployment-cli/         # Go CLI for deployment
│   └── testing-cli/            # Python CLI for testing
├── docs/                        # Documentation
└── .__examples__/              # Example configurations
    └── demo/                   # Working demo from Phase 1
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Kong Network                         │
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │ Kong Public  │────────▶│   Backend    │             │
│  │ (kong-realm) │         │     API      │             │
│  └──────┬───────┘         └──────────────┘             │
│         │                                                │
│  ┌──────────────┐                                       │
│  │ Kong Internal│                                       │
│  │ (internal-r) │                                       │
│  └──────┬───────┘                                       │
│         │                                                │
└─────────┼────────────────────────────────────────────────┘
          │
          │ JWT Validation (JWKS)
          │
┌─────────┼────────────────────────────────────────────────┐
│         │         Keycloak Network                       │
│         │                                                │
│  ┌──────▼───────┐         ┌──────────────┐             │
│  │   Keycloak   │────────▶│  PostgreSQL  │             │
│  │   (Realms)   │         │   Database   │             │
│  └──────────────┘         └──────────────┘             │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

## 🔧 Components

### Infrastructure

#### [Keycloak](infrastructure/keycloak/)

Identity and Access Management with PostgreSQL

- Pre-configured realms (kong-realm, internal-realm)
- Automatic realm import on startup
- Standalone deployment capability
- **Deploy**: `cd infrastructure/keycloak && docker-compose up -d`

#### [Kong](infrastructure/kong/)

API Gateway in DB-less mode

- Template-based configuration
- Multi-instance support
- Per-instance realm binding
- **Deploy**: `cd infrastructure/kong && docker-compose up -d`

### Applications

#### [Backend Demo](applications/backend-demo/)

FastAPI application with JWT integration

- JWT claims extraction
- Role-based access control
- Standalone deployment
- **Deploy**: `cd applications/backend-demo && docker-compose up -d`

### Composition

#### [Full Stack](compose/docker-compose.full.yml)

All components together

**Deploy**:

```bash
docker-compose -f compose/docker-compose.full.yml \
  --env-file compose/environments/dev.env up -d
```

#### [Multi-Kong](compose/docker-compose.multi-kong.yml)

Multiple Kong instances with different realms

**Deploy**:

```bash
docker-compose -f compose/docker-compose.multi-kong.yml \
  --env-file compose/environments/dev.env up -d
```

## 🛠️ CLI Tools

### Deployment CLI (Go)

```bash
# Build
cd tools/deployment-cli
make build

# Deploy components
./kc-deploy keycloak
./kc-deploy kong --name kong-public --realm kong-realm
./kc-deploy full --env dev

# Manage Kong instances
./kc-deploy kong add --name kong-api-v2 --realm api-v2-realm
./kc-deploy kong list
```

### Testing CLI (Python)

```bash
# Setup
cd tools/testing-cli
pip install -r requirements.txt

# Get JWT tokens
python -m src.cli token get --user testuser --realm kong-realm

# Test APIs
python -m src.cli api test --endpoint /api/protected
python -m src.cli suite run --env dev

# Keycloak operations
python -m src.cli keycloak create-user --realm kong-realm --username newuser
```

## 📖 Documentation

- [Architecture](docs/architecture.md) - System design and components
- [Deployment Guide](docs/deployment-guide.md) - Detailed deployment instructions
- [Multi-Kong Setup](docs/multi-kong-setup.md) - Multiple Kong instances
- [CLI Reference](docs/cli-reference.md) - Complete CLI commands
- [Production Guide](docs/PRODUCTION.md) - Production deployment (from demo)

## 🔐 Pre-configured Users

Default users for testing (change in production!):

| Realm          | Username       | Password          | Roles                         |
| -------------- | -------------- | ----------------- | ----------------------------- |
| kong-realm     | admin          | admin123          | admin, user                   |
| kong-realm     | testuser       | user123           | user                          |
| internal-realm | internal-admin | internal-admin123 | internal-admin, internal-user |

## ⚙️ Configuration

### Environment Variables

Each component has its own `.env.example` file:

- `infrastructure/keycloak/.env.example`
- `infrastructure/kong/.env.example`
- `applications/backend-demo/.env.example`
- `compose/environments/dev.env.example`
- `compose/environments/prod.env.example`

### Secrets Management

- **Development**: Use `.env` files
- **Production**: Use external secrets management (Vault, AWS Secrets Manager)

## 🚦 Service Endpoints

| Service       | Port | URL                   | Description        |
| ------------- | ---- | --------------------- | ------------------ |
| Keycloak      | 8080 | http://localhost:8080 | Admin Console      |
| Kong Public   | 8000 | http://localhost:8000 | Public API Gateway |
| Kong Admin    | 8001 | http://localhost:8001 | Admin API          |
| Kong Internal | 9000 | http://localhost:9000 | Internal Gateway   |
| Backend       | -    | Via Kong              | FastAPI App        |

## 🧪 Testing

```bash
# Manual testing
curl http://localhost:8000/api/public
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/api/protected

# Automated testing (Python CLI)
cd tools/testing-cli
python -m src.cli suite run --env dev
```

## 🎯 Use Cases

### Single Kong Instance

Use `docker-compose.full.yml` for:

- Simple API gateway
- Single authentication realm
- Development/testing

### Multiple Kong Instances

Use `docker-compose.multi-kong.yml` for:

- Multi-tenancy (realm per tenant)
- API versioning (v1, v2 on different instances)
- Environment separation (public/internal APIs)
- Service mesh patterns

### Custom Composition

Create your own composition:

1. Reference component compose files
2. Define networking
3. Set environment variables
4. Deploy with `docker-compose`

## 🔄 Migration from Demo

Migrating from `.__examples__/demo/`:

```bash
# The working demo is preserved in .__examples__/demo/
# New modular structure is in infrastructure/, applications/, compose/

# To migrate:
# 1. Review component READMEs
# 2. Copy configurations to new structure
# 3. Use composition layer for deployment
```

## 📊 Success Metrics

- ✅ Deploy individual components in < 30 seconds
- ✅ Add new Kong instance via CLI in < 1 minute
- ✅ Run full test suite in < 2 minutes
- ✅ Zero manual configuration steps
- ✅ Cross-platform CLI (Windows, Linux, macOS)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Open a GitHub issue
- **Documentation**: See `docs/` directory
- **Component Help**: Check component-specific READMEs
- **Examples**: Review `.__examples__/` directory

## 🎉 Key Features

- **No Shell Scripts**: All automation via Go/Python CLIs
- **Truly Modular**: Each component works standalone
- **Dynamic Scaling**: Add Kong instances on-demand
- **Configuration as Code**: Version-controlled configs
- **Production Ready**: Security, HA, monitoring built-in
- **Well Documented**: Comprehensive docs for all components

---

**Status**: ✅ Production-ready modular architecture  
**Demo**: Preserved in `.__examples__/demo/` (fully tested and working)  
**Version**: 2.0.0 (Modular Architecture)
