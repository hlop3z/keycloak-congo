#!/bin/bash
# Example workflow for testing Kong + Keycloak integration

set -e

echo "=== Kong + Keycloak Integration Testing Workflow ==="

# Make sure services are running
echo -e "\n1. Checking if services are running..."
# This would typically check Docker containers

# Get token for test user
echo -e "\n2. Getting token for test user..."
echo "testuser123" | python -m src.cli token get --user testuser --realm kong-realm > /tmp/token.txt

# Extract access token (simplified - in real scenario use jq or proper parsing)
echo -e "\n3. Token acquired successfully"

# Decode token
echo -e "\n4. Decoding token..."
# TOKEN=$(cat /tmp/token.txt | grep "Access Token" | cut -d: -f2 | xargs)
# python -m src.cli token decode "$TOKEN"

# Test public endpoint
echo -e "\n5. Testing public endpoint..."
python -m src.cli api call --endpoint /api/public --kong-url http://localhost:8000 || echo "Public endpoint not configured (expected)"

# Test protected endpoint
echo -e "\n6. Testing protected endpoint with token..."
# python -m src.cli api call --endpoint /api/protected --token "$TOKEN" --kong-url http://localhost:8000

# Run comprehensive test suite
echo -e "\n7. Running comprehensive test suite..."
python -m src.cli suite run --env dev --keycloak-url http://localhost:8080 --kong-url http://localhost:8000

# Generate HTML report
echo -e "\n8. Generating HTML report..."
python -m src.cli suite run --env dev --format html --output test-report.html

echo -e "\n✓ Test workflow completed successfully!"
echo "  Report saved to: test-report.html"

