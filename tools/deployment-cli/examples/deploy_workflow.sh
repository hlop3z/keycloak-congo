#!/bin/bash
# Example deployment workflow using kc-deploy CLI

set -e

echo "=== Kong + Keycloak Deployment Workflow ==="

# Initialize configuration
echo -e "\n1. Initializing configuration..."
kc-deploy config init
echo "   ✓ Configuration initialized"

# Validate configuration and project structure
echo -e "\n2. Validating configuration..."
kc-deploy config validate
echo "   ✓ Configuration valid"

# Show current configuration
echo -e "\n3. Current configuration:"
kc-deploy config show

# Deploy Keycloak first
echo -e "\n4. Deploying Keycloak..."
kc-deploy deploy keycloak

# Wait for Keycloak to be ready
echo -e "\n5. Waiting for Keycloak to be ready..."
sleep 10

# Check Keycloak status
echo -e "\n6. Checking Keycloak status..."
kc-deploy status keycloak

# Deploy Kong
echo -e "\n7. Deploying Kong..."
kc-deploy deploy kong

# Wait for Kong to be ready
echo -e "\n8. Waiting for Kong to be ready..."
sleep 5

# Check all services status
echo -e "\n9. Checking all services status..."
kc-deploy status

# View logs
echo -e "\n10. Viewing recent logs..."
kc-deploy logs keycloak --tail 20

echo -e "\n✓ Deployment workflow completed successfully!"
echo "   Services are running and ready for testing"

