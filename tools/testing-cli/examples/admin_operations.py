#!/usr/bin/env python
"""
Example script demonstrating Keycloak Admin API operations
"""

from src.keycloak_client import KeycloakAdmin, get_token

# Configuration
KEYCLOAK_URL = "http://localhost:8080"
REALM = "kong-realm"
ADMIN_USER = "admin"
ADMIN_PASSWORD = "admin"  # Change this!


def main():
    print("=== Keycloak Admin Operations Example ===\n")

    # Initialize admin client
    print("1. Authenticating as admin...")
    admin = KeycloakAdmin(KEYCLOAK_URL, ADMIN_USER, ADMIN_PASSWORD)
    print("   ✓ Admin authenticated\n")

    # List existing users
    print("2. Listing users in realm...")
    users = admin.list_users(REALM)
    print(f"   Found {len(users)} users:")
    for user in users[:5]:  # Show first 5
        print(f"   - {user['username']} ({user.get('email', 'no email')})")
    print()

    # Create a new test user
    print("3. Creating test user...")
    try:
        user_id = admin.create_user(
            realm=REALM, username="apitest", password="apitest123", email="apitest@example.com"
        )
        print(f"   ✓ User created with ID: {user_id}\n")
    except Exception as e:
        print(f"   Note: {e} (user may already exist)\n")

    # Get roles
    print("4. Listing realm roles...")
    roles = admin.get_realm_roles(REALM)
    print(f"   Found {len(roles)} roles:")
    for role in roles[:5]:  # Show first 5
        print(f"   - {role['name']}")
    print()

    # Assign role to user
    print("5. Assigning 'user' role to apitest...")
    try:
        admin.assign_role(REALM, "apitest", "user")
        print("   ✓ Role assigned\n")
    except Exception as e:
        print(f"   Error: {e}\n")

    # Get user roles
    print("6. Getting roles for apitest...")
    try:
        user_roles = admin.get_user_roles(REALM, "apitest")
        print(f"   User has roles: {', '.join(user_roles)}\n")
    except Exception as e:
        print(f"   Error: {e}\n")

    # Test getting token for new user
    print("7. Testing token acquisition for new user...")
    try:
        token_data = get_token(KEYCLOAK_URL, REALM, "apitest", "apitest123")
        print("   ✓ Token acquired successfully")
        print(f"   Token expires in: {token_data['expires_in']} seconds\n")
    except Exception as e:
        print(f"   Error: {e}\n")

    print("=== Admin operations completed ===")


if __name__ == "__main__":
    main()
