"""API routes for backend demo"""

from fastapi import APIRouter, Header, HTTPException, Request
from typing import Optional
from src.api.auth import decode_jwt_payload, check_role, get_user_info

router = APIRouter(prefix="/api", tags=["API"])


@router.get("/public", tags=["Public"])
async def public_endpoint():
    """Public endpoint - no authentication required"""
    return {
        "message": "This is a public endpoint, accessible without authentication",
        "endpoint": "/api/public",
        "authentication": "none",
    }


@router.post("/public", tags=["Public"])
async def public_endpoint_post(request: Request):
    """Public POST endpoint"""
    try:
        body = await request.json()
    except:
        body = {}

    return {
        "message": "Public POST endpoint received your data",
        "received_data": body,
        "endpoint": "/api/public",
        "method": "POST",
    }


@router.get("/protected", tags=["Protected"])
async def protected_endpoint(
    request: Request, authorization: Optional[str] = Header(None)
):
    """Protected endpoint - requires valid JWT"""
    jwt_payload = decode_jwt_payload(authorization)

    return {
        "message": "This is a protected endpoint, accessible with valid JWT",
        "endpoint": "/api/protected",
        "authentication": "required",
        "user": get_user_info(jwt_payload),
        "token_info": {
            "issued_at": jwt_payload.get("iat"),
            "expires_at": jwt_payload.get("exp"),
            "issuer": jwt_payload.get("iss"),
        },
        "request_headers": {
            "x-kong-request-id": request.headers.get("x-kong-request-id"),
            "x-correlation-id": request.headers.get("x-correlation-id"),
        },
    }


@router.post("/protected", tags=["Protected"])
async def protected_endpoint_post(
    request: Request, authorization: Optional[str] = Header(None)
):
    """Protected POST endpoint - requires valid JWT"""
    jwt_payload = decode_jwt_payload(authorization)

    try:
        body = await request.json()
    except:
        body = {}

    return {
        "message": "Protected POST endpoint processed your request",
        "received_data": body,
        "endpoint": "/api/protected",
        "method": "POST",
        "user": jwt_payload.get("preferred_username", "unknown"),
    }


@router.get("/admin", tags=["Admin"])
async def admin_endpoint(request: Request, authorization: Optional[str] = Header(None)):
    """Admin endpoint - requires JWT with admin role"""
    jwt_payload = decode_jwt_payload(authorization)

    # Check if user has admin role
    if not check_role(jwt_payload, "admin"):
        raise HTTPException(status_code=403, detail="Forbidden: Admin role required")

    return {
        "message": "This is an admin endpoint, accessible only with admin role",
        "endpoint": "/api/admin",
        "authentication": "required",
        "authorization": "admin role",
        "user_info": {
            "username": jwt_payload.get("preferred_username", "unknown"),
            "email": jwt_payload.get("email", "unknown"),
            "roles": jwt_payload.get("realm_roles", []),
        },
    }


@router.get("/admin/users", tags=["Admin"])
async def admin_users_endpoint(authorization: Optional[str] = Header(None)):
    """Admin endpoint - list users (demo)"""
    jwt_payload = decode_jwt_payload(authorization)

    if not check_role(jwt_payload, "admin"):
        raise HTTPException(status_code=403, detail="Forbidden: Admin role required")

    # Mock user data
    return {
        "message": "Admin-only endpoint: User list",
        "users": [
            {"id": 1, "username": "admin", "roles": ["admin", "user"]},
            {"id": 2, "username": "testuser", "roles": ["user"]},
        ],
        "total": 2,
        "requester": jwt_payload.get("preferred_username", "unknown"),
    }
