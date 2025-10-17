# CLI Reference

Command reference for deployment and testing CLIs.

## Deployment CLI (kc-deploy)

### Installation

```bash
cd tools/deployment-cli
make build
```

### Commands

```bash
# Deploy
kc-deploy deploy full --env dev
kc-deploy deploy keycloak

# Kong management
kc-deploy kong add --name kong-api-v2 --realm api-v2-realm
kc-deploy kong list

# Status
kc-deploy status
kc-deploy health
```

See [tools/deployment-cli/README.md](../tools/deployment-cli/README.md) for details.

## Testing CLI (kc-test)

### Installation

```bash
cd tools/testing-cli
pip install -r requirements.txt
```

### Commands

```bash
# Token operations
python -m src.cli token get --user testuser --realm kong-realm
python -m src.cli token decode <TOKEN>

# API testing
python -m src.cli api call --endpoint /api/protected --token <TOKEN>
python -m src.cli suite run --env dev
```

See [tools/testing-cli/README.md](../tools/testing-cli/README.md) for details.

---

**Status**: 📝 Placeholder - Expand as CLIs are implemented
