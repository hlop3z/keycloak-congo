#!/bin/bash
# Example multi-Kong instance setup

set -e

echo "=== Multi-Kong Instance Setup ==="

# Add additional Kong instances to configuration
echo -e "\n1. Adding Kong instances to configuration..."

kc-deploy kong add \
  --name kong-api-v1 \
  --realm api-v1-realm \
  --port 8001

kc-deploy kong add \
  --name kong-api-v2 \
  --realm api-v2-realm \
  --port 8002

echo "   ✓ Kong instances added"

# List configured instances
echo -e "\n2. Configured Kong instances:"
kc-deploy kong list

# Deploy multi-Kong setup
echo -e "\n3. Deploying multi-Kong setup..."
kc-deploy deploy multi-kong

# Wait for services
echo -e "\n4. Waiting for services to be ready..."
sleep 10

# Check status
echo -e "\n5. Checking multi-Kong status..."
kc-deploy status multi-kong

echo -e "\n✓ Multi-Kong setup completed!"
echo "   You now have multiple Kong instances running"

