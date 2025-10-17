# Architecture Overview

This document describes the modular architecture of the Kong + Keycloak system.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│  │ Web App │  │ Mobile  │  │ API     │  │ Service │           │
│  │         │  │   App   │  │ Client  │  │  Mesh   │           │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘           │
│       │            │            │            │                  │
└───────┼────────────┼────────────┼────────────┼──────────────────┘
        │            │            │            │
        └────────────┴────────────┴────────────┘
                     │
┌────────────────────┼────────────────────────────────────────────┐
│   Kong API Gateway Layer                                        │
│                    │                                            │
│  ┌─────────────────▼───────────┐  ┌──────────────────────────┐  │
│  │    Kong Public Instance     │  │  Kong Internal Instance  │  │
│  │    (kong-realm)             │  │  (internal-realm)        │  │
│  │                             │  │                          │  │
│  │  - JWT Validation           │  │  - JWT Validation        │  │
│  │  - Rate Limiting            │  │  - Rate Limiting         │  │
│  │  - CORS                     │  │  - Access Control        │  │
│  │  - Request Transform        │  │  - Service Routing       │  │
│  └─────────────┬───────────────┘  └─────────────┬────────────┘  │
│                │                                │               │
└────────────────┼────────────────────────────────┼───────────────┘
                 │                                │
                 │  JWT Verification              │
                 │  via JWKS                      │
                 │                                │
┌────────────────┼────────────────────────────────┼─────────────────┐
│   Keycloak Identity Layer                       │                 │
│                │                                │                 │
│  ┌─────────────▼────────────────────────────────▼──────────────┐ │
│  │                   Keycloak                                   │ │
│  │                                                              │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │ │
│  │  │  kong-realm  │  │internal-realm│  │   Other      │     │ │
│  │  │              │  │              │  │   Realms     │     │ │
│  │  │ Users:       │  │ Users:       │  │              │     │ │
│  │  │ - admin      │  │ - internal-  │  │              │     │ │
│  │  │ - testuser   │  │   admin      │  │              │     │ │
│  │  │              │  │              │  │              │     │ │
│  │  │ Client:      │  │ Client:      │  │              │     │ │
│  │  │ kong-client  │  │ kong-int-    │  │              │     │ │
│  │  │              │  │ client       │  │              │     │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │ │
│  │                                                              │ │
│  └──────────────────────────────┬───────────────────────────────┘ │
│                                 │                                 │
│  ┌──────────────────────────────▼───────────────────────────────┐ │
│  │                     PostgreSQL Database                      │ │
│  │  - Realm configurations                                      │ │
│  │  - User data                                                 │ │
│  │  - Sessions                                                  │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
                                 │
┌────────────────────────────────┼────────────────────────────────────┐
│   Backend Application Layer    │                                    │
│                                │                                    │
│  ┌─────────────────────────────▼──────────────────────────────┐   │
│  │                   Backend API Services                      │   │
│  │                                                             │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│  │  │  Public API  │  │ Protected    │  │   Admin      │    │   │
│  │  │  Endpoints   │  │   API        │  │   API        │    │   │
│  │  │              │  │  Endpoints   │  │  Endpoints   │    │   │
│  │  │ - No auth    │  │              │  │              │    │   │
│  │  │   required   │  │ - JWT claims │  │ - JWT claims │    │   │
│  │  │              │  │   extraction │  │   extraction │    │   │
│  │  │              │  │ - User info  │  │ - Role check │    │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│  │                                                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### Keycloak

**Role**: Identity and Access Management

- User authentication
- JWT token issuance
- Token refresh
- User/role management
- Multi-realm support
- JWKS endpoint for public key distribution

**Key Features**:

- PostgreSQL backend for persistence
- Automatic realm import
- Multiple realm support
- Brute force protection
- Configurable token lifetimes

### Kong Gateway

**Role**: API Gateway & Policy Enforcement

- Request routing
- JWT signature validation (via JWKS)
- Rate limiting
- CORS handling
- Request/response transformation
- Load balancing
- Circuit breaking

**Key Features**:

- DB-less mode (declarative configuration)
- Multi-instance support
- Per-instance realm binding
- Plugin ecosystem
- Health checks

### Backend Application

**Role**: Business Logic & Data

- API endpoint implementation
- JWT claims extraction (no verification needed)
- Role-based access control
- Business logic execution

**Key Features**:

- JWT-aware (extracts claims)
- Role checking
- Stateless design
- Horizontal scalability

## Request Flow

### 1. Token Acquisition

```
Client → Keycloak: POST /realms/{realm}/protocol/openid-connect/token
                   (username, password, client_id)

Keycloak → Client: {access_token, refresh_token, expires_in}
```

### 2. API Request (Protected Endpoint)

```
Client → Kong: GET /api/protected
             Header: Authorization: Bearer <JWT>

Kong → Keycloak (JWKS): Fetch public key for signature verification
                        (cached after first request)

Kong: Validate JWT signature
      ✓ Signature valid
      ✓ Token not expired
      ✓ Issuer matches

Kong → Backend: GET /api/protected
                Header: Authorization: Bearer <JWT>
                Header: X-Kong-Request-Id: <id>

Backend: Extract claims from JWT (no verification)
         Check roles if needed
         Execute business logic

Backend → Kong → Client: Response
```

### 3. API Request (Public Endpoint)

```
Client → Kong: GET /api/public
               (no Authorization header)

Kong → Backend: GET /api/public
                Header: X-Kong-Request-Id: <id>

Backend: Execute public logic

Backend → Kong → Client: Response
```

## Security Model

### JWT Validation

1. **Kong validates** JWT signature using Keycloak's public key (JWKS)
2. **Kong checks** expiration and standard claims
3. **Kong forwards** request to backend only if valid
4. **Backend extracts** claims from validated token (safe, no verification needed)

### Defense in Depth

- **Network isolation**: Separate networks for Keycloak-internal and Kong-Backend
- **Least privilege**: Non-root container users
- **Secret management**: Environment variables, not hardcoded
- **Rate limiting**: Prevent abuse
- **CORS**: Control client access

## Scalability Patterns

### Horizontal Scaling

**Kong**:

```
Load Balancer
   ├─ Kong Instance 1 (same config)
   ├─ Kong Instance 2 (same config)
   └─ Kong Instance 3 (same config)
```

**Backend**:

```
Kong
   ├─ Backend Instance 1
   ├─ Backend Instance 2
   └─ Backend Instance 3
```

**Keycloak** (HA setup):

```
Load Balancer
   ├─ Keycloak Instance 1 ─┐
   ├─ Keycloak Instance 2 ─┼─ PostgreSQL (replicated)
   └─ Keycloak Instance 3 ─┘
```

### Multi-Tenant Architecture

**Pattern 1: Realm per Tenant**

```
├─ Kong Public (tenant-a-realm) → Tenant A Backend
├─ Kong Public (tenant-b-realm) → Tenant B Backend
└─ Kong Public (tenant-c-realm) → Tenant C Backend
```

**Pattern 2: Instance per Tenant**

```
├─ Kong Tenant A (tenant-a-realm) → Tenant A Backend
├─ Kong Tenant B (tenant-b-realm) → Tenant B Backend
└─ Kong Tenant C (tenant-c-realm) → Tenant C Backend
```

## Network Topology

### Development

```
keycloak-network:
  - postgres
  - keycloak

kong-network:
  - kong
  - backend
  - keycloak (for JWKS access)
```

### Production (Recommended)

```
keycloak-internal:
  - postgres
  - keycloak

keycloak-external:
  - keycloak (external facing)

kong-backend:
  - kong
  - backend

kong-keycloak:
  - kong (for JWKS access)
  - keycloak
```

## Data Flow

### Authentication Data

1. **User credentials** → Keycloak (encrypted)
2. **User data** → PostgreSQL (hashed passwords)
3. **JWT** → Client (signed, not encrypted)
4. **JWT** → Kong (validated, forwarded)
5. **JWT claims** → Backend (extracted, trusted)

### Configuration Data

1. **Realm configs** → Volume mount → Keycloak import
2. **Kong declarative config** → Volume mount → Kong load
3. **Environment variables** → Docker Compose → Containers

## Key Design Decisions

### Why DB-less Kong?

- **Simplicity**: No database to manage
- **Speed**: Faster startup
- **Scalability**: True stateless
- **GitOps**: Configuration as code

### Why JWT Validation at Kong?

- **Security**: Centralized validation
- **Performance**: Backend doesn't need to verify
- **Separation**: Auth logic separate from business logic
- **Reusability**: Multiple backends can trust Kong

### Why No Kong Consumers?

- **Flexibility**: Any valid Keycloak user works
- **Simplicity**: No pre-configuration needed
- **Scalability**: New users don't require Kong updates
- **Dynamic**: Users managed entirely in Keycloak

## Monitoring & Observability

### Metrics

- Kong: Prometheus plugin
- Keycloak: Built-in metrics endpoint
- Backend: Custom metrics

### Logging

- Kong: Access logs, error logs
- Keycloak: Event logs
- Backend: Application logs
- Centralization: ELK/Loki/CloudWatch

### Tracing

- Correlation IDs across all components
- Kong request ID propagation
- Distributed tracing (Jaeger/Zipkin)

## References

- [Kong Architecture](https://docs.konghq.com/gateway/latest/production/deployment-topologies/)
- [Keycloak Architecture](https://www.keycloak.org/docs/latest/server_admin/#_architecture)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)

---

**Last Updated**: 2025-10-17  
**Version**: 2.0.0 (Modular Architecture)
