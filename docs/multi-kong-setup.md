# Multi-Kong Instance Setup

Guide for deploying and managing multiple Kong instances with different Keycloak realms.

## Overview

Multiple Kong instances allow you to:

- Separate public and internal APIs
- Implement multi-tenancy (realm per tenant)
- Version APIs (v1, v2 on different instances)
- Scale independently
- Apply different policies per instance

## Quick Start

```bash
# Deploy pre-configured multi-Kong setup
make deploy-multi-kong

# Verify
curl http://localhost:8000/api/public  # Kong Public
curl http://localhost:9000/internal/api # Kong Internal (requires token)
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│                Keycloak                          │
│  ┌──────────────┐  ┌──────────────┐            │
│  │  kong-realm  │  │internal-realm│            │
│  │              │  │              │            │
│  │ - testuser   │  │ - internal-  │            │
│  │ - admin      │  │   admin      │            │
│  └──────────────┘  └──────────────┘            │
└────────┬─────────────────┬────────────────────────┘
         │                 │
    ┌────┴─────┐      ┌───┴──────┐
    │          │      │          │
┌───▼──────────▼───┐ ┌▼──────────▼───┐
│  Kong Public     │ │ Kong Internal  │
│  Port: 8000      │ │ Port: 9000     │
│  Realm: kong     │ │ Realm: internal│
└──────────────────┘ └────────────────┘
```

## Use Cases

See [deployment-guide.md](deployment-guide.md) for implementation details.

---

**Status**: 📝 Placeholder - Expand as needed
