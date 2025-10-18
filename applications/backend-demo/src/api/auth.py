"""
JWT authentication utilities

Note: This module DOES NOT verify JWT signatures.
Kong has already validated the JWT signature before forwarding the request.
We safely extract claims from the validated token.
"""

import base64
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def decode_jwt_payload(authorization: Optional[str]) -> Dict[str, Any]:
    """
    Decode JWT payload without verification.

    This is safe because Kong has already verified the signature.
    We're just extracting claims from the validated token.

    Args:
        authorization: Authorization header value

    Returns:
        Dictionary of JWT claims
    """
    if not authorization:
        return {}

    try:
        # Extract token from "Bearer <token>"
        token = authorization.split(" ")[1] if " " in authorization else authorization

        # Decode JWT payload (second part of the token)
        payload_encoded = token.split(".")[1]

        # Add padding if needed (base64 requires length to be multiple of 4)
        padding = 4 - len(payload_encoded) % 4
        if padding != 4:
            payload_encoded += "=" * padding

        # Decode base64
        payload_decoded = base64.urlsafe_b64decode(payload_encoded)

        # Parse JSON
        return json.loads(payload_decoded)

    except Exception as e:
        logger.warning(f"Failed to decode JWT: {e}")
        return {}


def check_role(jwt_payload: Dict[str, Any], required_role: str) -> bool:
    """
    Check if user has required role.

    Args:
        jwt_payload: Decoded JWT claims
        required_role: Role to check for

    Returns:
        True if user has the role, False otherwise
    """
    roles = jwt_payload.get("realm_roles", [])
    return required_role in roles


def get_user_info(jwt_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract user information from JWT payload.

    Args:
        jwt_payload: Decoded JWT claims

    Returns:
        Dictionary with user information
    """
    return {
        "id": jwt_payload.get("sub"),
        "roles": jwt_payload.get("realm_roles", []),
        "username": jwt_payload.get("preferred_username"),
        "email": jwt_payload.get("email"),
        "first_name": jwt_payload.get("given_name"),
        "last_name": jwt_payload.get("family_name"),
        "email_verified": jwt_payload.get("email_verified", False),
    }
