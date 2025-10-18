#!/bin/bash

set -e

echo "Testing Kong + Keycloak integration..."

echo "Getting token..."
TOKEN=$(PYTHONUTF8=1 uv run kc-test token get --user admin --password admin123 --realm kong-realm \
  | awk '/Access Token:/{flag=1; next}/Refresh Token:/{flag=0}flag' | tr -d '\n')
echo "Token: $TOKEN"


echo "Testing public endpoint..."
uv run kc-test api call --endpoint "api/public"

echo "Testing protected endpoint..."
uv run kc-test api call --endpoint "api/protected" --token $TOKEN

