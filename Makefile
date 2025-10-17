.PHONY: help build clean test deploy-dev deploy-prod stop logs status

# Default target
help:
	@echo "Kong + Keycloak Modular Architecture - Make Commands"
	@echo ""
	@echo "Development:"
	@echo "  make deploy-dev        - Deploy full stack (development)"
	@echo "  make deploy-multi-kong - Deploy multiple Kong instances"
	@echo "  make stop              - Stop all services"
	@echo "  make clean             - Stop and remove all data"
	@echo ""
	@echo "Status & Logs:"
	@echo "  make status            - Show service status"
	@echo "  make logs              - View all logs"
	@echo "  make logs-kong         - View Kong logs"
	@echo "  make logs-keycloak     - View Keycloak logs"
	@echo "  make logs-backend      - View backend logs"
	@echo ""
	@echo "Testing:"
	@echo "  make test              - Run test suite"
	@echo "  make test-endpoints    - Test API endpoints"
	@echo ""
	@echo "CLI Tools:"
	@echo "  make build-cli         - Build deployment CLI"
	@echo "  make setup-test-cli    - Setup testing CLI"
	@echo ""
	@echo "Production:"
	@echo "  make deploy-prod       - Deploy full stack (production)"

# Development deployment
deploy-dev:
	@echo "Deploying full stack (development)..."
	@cp compose/environments/dev.env.example compose/environments/dev.env || true
	docker-compose -f compose/docker-compose.full.yml \
		--env-file compose/environments/dev.env up -d
	@echo ""
	@echo "✓ Deployment complete!"
	@echo "  Keycloak: http://localhost:8080 (admin/admin)"
	@echo "  Kong Proxy: http://localhost:8000"
	@echo "  Kong Admin: http://localhost:8001"

deploy-multi-kong:
	@echo "Deploying multi-Kong setup..."
	@cp compose/environments/dev.env.example compose/environments/dev.env || true
	docker-compose -f compose/docker-compose.multi-kong.yml \
		--env-file compose/environments/dev.env up -d
	@echo ""
	@echo "✓ Deployment complete!"
	@echo "  Keycloak: http://localhost:8080"
	@echo "  Kong Public: http://localhost:8000"
	@echo "  Kong Internal: http://localhost:9000"

# Production deployment
deploy-prod:
	@echo "⚠️  WARNING: Deploying to production!"
	@echo "Make sure you've updated compose/environments/prod.env with secure passwords!"
	@read -p "Continue? (y/N): " confirm && [ $$confirm = "y" ] || exit 1
	docker-compose -f compose/docker-compose.full.yml \
		--env-file compose/environments/prod.env up -d

# Stop services
stop:
	@echo "Stopping services..."
	docker-compose -f compose/docker-compose.full.yml down
	docker-compose -f compose/docker-compose.multi-kong.yml down
	@echo "✓ Services stopped"

# Clean everything (including volumes)
clean:
	@echo "⚠️  WARNING: This will remove all data (including PostgreSQL database)!"
	@read -p "Continue? (y/N): " confirm && [ $$confirm = "y" ] || exit 1
	docker-compose -f compose/docker-compose.full.yml down -v
	docker-compose -f compose/docker-compose.multi-kong.yml down -v
	@echo "✓ Cleanup complete"

# Status
status:
	@echo "=== Service Status ==="
	@docker-compose -f compose/docker-compose.full.yml ps 2>/dev/null || \
		docker-compose -f compose/docker-compose.multi-kong.yml ps 2>/dev/null || \
		echo "No services running"

# Logs
logs:
	docker-compose -f compose/docker-compose.full.yml logs -f

logs-kong:
	docker-compose -f compose/docker-compose.full.yml logs -f kong

logs-keycloak:
	docker-compose -f compose/docker-compose.full.yml logs -f keycloak

logs-backend:
	docker-compose -f compose/docker-compose.full.yml logs -f backend

# Testing
test:
	@echo "Running test suite..."
	cd tools/testing-cli && python -m pytest tests/ -v

test-endpoints:
	@echo "Testing API endpoints..."
	@echo "Public endpoint:"
	@curl -s http://localhost:8000/api/public | jq . || echo "Kong not available"
	@echo ""
	@echo "Get token and test protected endpoint with: make test-protected"

test-protected:
	@echo "Testing protected endpoint (requires token)..."
	@echo "First, get a token:"
	@cd tools/testing-cli && python -m src.cli token get --user testuser --realm kong-realm

# Build CLI tools
build-cli:
	@echo "Building deployment CLI..."
	cd tools/deployment-cli && make build
	@echo "✓ CLI built: tools/deployment-cli/kc-deploy"

setup-test-cli:
	@echo "Setting up testing CLI..."
	cd tools/testing-cli && pip install -r requirements.txt
	@echo "✓ Testing CLI ready"

# Component-specific deployments
deploy-keycloak:
	@echo "Deploying Keycloak standalone..."
	cd infrastructure/keycloak && \
		cp .env.example .env && \
		docker-compose up -d

deploy-kong:
	@echo "Deploying Kong standalone..."
	cd infrastructure/kong && \
		cp .env.example .env && \
		docker-compose up -d

deploy-backend:
	@echo "Deploying Backend standalone..."
	cd applications/backend-demo && \
		cp .env.example .env && \
		docker-compose up -d

# Health checks
health:
	@echo "Checking service health..."
	@echo -n "Keycloak: "
	@curl -s http://localhost:8080/health/ready > /dev/null && echo "✓ Healthy" || echo "✗ Unhealthy"
	@echo -n "Kong: "
	@curl -s http://localhost:8001/status > /dev/null && echo "✓ Healthy" || echo "✗ Unhealthy"
	@echo -n "Backend (via Kong): "
	@curl -s http://localhost:8000/api/public > /dev/null && echo "✓ Healthy" || echo "✗ Unhealthy"

# Quick demo
demo:
	@echo "🚀 Quick Demo Setup"
	@echo ""
	@$(MAKE) deploy-dev
	@echo ""
	@echo "Waiting for services to be ready..."
	@sleep 30
	@$(MAKE) health
	@echo ""
	@echo "✓ Demo ready! Try these commands:"
	@echo "  make test-endpoints     - Test public endpoint"
	@echo "  make logs              - View logs"
	@echo "  make status            - Check status"

