"""Keycloak client for token and admin operations"""

import requests
import base64
import json
from typing import Dict, Any, List, Optional


def get_token(
    keycloak_url: str, realm: str, username: str, password: str, client_id: str = "kong-client"
) -> Dict[str, Any]:
    """
    Get JWT token from Keycloak

    Args:
        keycloak_url: Keycloak base URL
        realm: Realm name
        username: Username
        password: Password
        client_id: Client ID (default: kong-client)

    Returns:
        Token data including access_token and refresh_token
    """
    token_endpoint = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/token"

    data = {
        "username": username,
        "password": password,
        "grant_type": "password",
        "client_id": client_id,
    }

    response = requests.post(
        token_endpoint, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if response.status_code != 200:
        raise Exception(f"Token request failed: {response.text}")

    return response.json()


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode JWT token (without verification)

    Args:
        token: JWT token string

    Returns:
        Decoded token payload
    """
    # Split token
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT token format")

    # Decode payload (second part)
    payload_encoded = parts[1]

    # Add padding if needed
    padding = 4 - len(payload_encoded) % 4
    if padding != 4:
        payload_encoded += "=" * padding

    # Decode base64
    payload_decoded = base64.urlsafe_b64decode(payload_encoded)

    # Parse JSON
    return json.loads(payload_decoded)


def refresh_token(
    keycloak_url: str, realm: str, refresh_token_str: str, client_id: str = "kong-client"
) -> Dict[str, Any]:
    """
    Refresh JWT token

    Args:
        keycloak_url: Keycloak base URL
        realm: Realm name
        refresh_token_str: Refresh token
        client_id: Client ID

    Returns:
        New token data
    """
    token_endpoint = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/token"

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token_str,
        "client_id": client_id,
    }

    response = requests.post(
        token_endpoint, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    if response.status_code != 200:
        raise Exception(f"Token refresh failed: {response.text}")

    return response.json()


class KeycloakAdmin:
    """Keycloak Admin API client"""

    def __init__(self, keycloak_url: str, admin_username: str, admin_password: str):
        """
        Initialize Keycloak Admin client

        Args:
            keycloak_url: Keycloak base URL
            admin_username: Admin username
            admin_password: Admin password
        """
        self.keycloak_url = keycloak_url
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.admin_token = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate and get admin token"""
        token_data = get_token(
            self.keycloak_url, "master", self.admin_username, self.admin_password, "admin-cli"
        )
        self.admin_token = token_data["access_token"]

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with admin token"""
        return {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json",
        }

    def list_users(self, realm: str) -> List[Dict[str, Any]]:
        """
        List all users in a realm

        Args:
            realm: Realm name

        Returns:
            List of users
        """
        url = f"{self.keycloak_url}/admin/realms/{realm}/users"
        response = requests.get(url, headers=self._get_headers())

        if response.status_code != 200:
            raise Exception(f"Failed to list users: {response.text}")

        return response.json()

    def create_user(
        self, realm: str, username: str, password: str, email: Optional[str] = None
    ) -> str:
        """
        Create a new user

        Args:
            realm: Realm name
            username: Username
            password: Password
            email: Email (optional)

        Returns:
            User ID
        """
        # Create user
        url = f"{self.keycloak_url}/admin/realms/{realm}/users"
        user_data = {
            "username": username,
            "enabled": True,
            "emailVerified": True,
            "credentials": [{"type": "password", "value": password, "temporary": False}],
        }

        if email:
            user_data["email"] = email

        response = requests.post(url, headers=self._get_headers(), json=user_data)

        if response.status_code not in [201, 204]:
            raise Exception(f"Failed to create user: {response.text}")

        # Get user ID from location header or fetch user
        location = response.headers.get("Location")
        if location:
            user_id = location.split("/")[-1]
        else:
            # Fetch user by username
            users = self.list_users(realm)
            user = next((u for u in users if u["username"] == username), None)
            if not user:
                raise Exception("User created but ID not found")
            user_id = user["id"]

        return user_id

    def get_user_by_username(self, realm: str, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user by username

        Args:
            realm: Realm name
            username: Username

        Returns:
            User data or None
        """
        url = f"{self.keycloak_url}/admin/realms/{realm}/users?username={username}"
        response = requests.get(url, headers=self._get_headers())

        if response.status_code != 200:
            raise Exception(f"Failed to get user: {response.text}")

        users = response.json()
        return users[0] if users else None

    def get_realm_roles(self, realm: str) -> List[Dict[str, Any]]:
        """
        Get all realm roles

        Args:
            realm: Realm name

        Returns:
            List of roles
        """
        url = f"{self.keycloak_url}/admin/realms/{realm}/roles"
        response = requests.get(url, headers=self._get_headers())

        if response.status_code != 200:
            raise Exception(f"Failed to get roles: {response.text}")

        return response.json()

    def assign_role(self, realm: str, username: str, role_name: str):
        """
        Assign role to user

        Args:
            realm: Realm name
            username: Username
            role_name: Role name
        """
        # Get user
        user = self.get_user_by_username(realm, username)
        if not user:
            raise Exception(f"User '{username}' not found")

        user_id = user["id"]

        # Get role
        roles = self.get_realm_roles(realm)
        role = next((r for r in roles if r["name"] == role_name), None)
        if not role:
            raise Exception(f"Role '{role_name}' not found")

        # Assign role
        url = f"{self.keycloak_url}/admin/realms/{realm}/users/{user_id}/role-mappings/realm"
        response = requests.post(url, headers=self._get_headers(), json=[role])

        if response.status_code not in [204, 200]:
            raise Exception(f"Failed to assign role: {response.text}")

    def get_user_roles(self, realm: str, username: str) -> List[str]:
        """
        Get roles assigned to a user

        Args:
            realm: Realm name
            username: Username

        Returns:
            List of role names
        """
        user = self.get_user_by_username(realm, username)
        if not user:
            raise Exception(f"User '{username}' not found")

        user_id = user["id"]
        url = f"{self.keycloak_url}/admin/realms/{realm}/users/{user_id}/role-mappings/realm"
        response = requests.get(url, headers=self._get_headers())

        if response.status_code != 200:
            raise Exception(f"Failed to get user roles: {response.text}")

        roles = response.json()
        return [role["name"] for role in roles]
