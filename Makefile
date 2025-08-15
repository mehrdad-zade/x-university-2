# X-University Development Environment Makefile
# Enhanced version with better development workflow support

.PHONY: help setup clean down logs test fmt check dev prod backup restore fix-postgres

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
help: ## Show this help message
	@echo "$(BLUE)X-University Development Environment$(NC)"
	@echo "=================================="
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(BLUE)Examples:$(NC)"
	@echo "  make setup        # Quick setup with existing data"
	@echo "  make fresh        # Complete fresh setup"
	@echo "  make dev          # Start development environment"
	@echo "  make health       # Check system health"

# PostgreSQL specific fixes
fix-postgres: ## Fix PostgreSQL startup issues and prevent exit code 126 errors
	@echo "$(GREEN)🔧 Fixing PostgreSQL startup issues...$(NC)"
	./scripts/setup.sh --diagnose-postgres

diagnose-postgres: ## Diagnose PostgreSQL startup problems
	@echo "$(BLUE)🔍 Running PostgreSQL diagnostics...$(NC)"
	./scripts/setup.sh --diagnose-postgres

test-postgres: ## Test PostgreSQL startup reliability (runs a clean setup)
	@echo "$(GREEN)🧪 Testing PostgreSQL startup reliability...$(NC)"
	./scripts/setup.sh --clean --skip-tests --skip-browser --skip-logs

# Enhanced setup commands
setup: ## Start the development environment (preserves existing data)
	@echo "$(GREEN)🚀 Starting X-University development environment...$(NC)"
	./scripts/setup.sh

clean-env: ## Clean all project resources (containers, images, volumes, local files)
	@echo "$(YELLOW)🧹 Cleaning X-University environment...$(NC)"
	./scripts/cleanup.sh

fresh: ## Complete fresh setup (clean + setup) with schema reset
	@echo "$(YELLOW)🧹 Cleaning X-University environment...$(NC)"
	./scripts/cleanup.sh || true
	@echo "$(GREEN)🚀 Starting fresh X-University development environment...$(NC)"
	./scripts/setup.sh --clean

# Docker service management
up: ## Start services in background
	@echo "$(GREEN)Starting services...$(NC)"
	docker compose -f infra/docker-compose.yml --env-file infra/.env up -d

down: ## Stop and remove all services
	@echo "$(YELLOW)Stopping services...$(NC)"
	docker compose -f infra/docker-compose.yml --env-file infra/.env down

restart: ## Restart all services
	@echo "$(YELLOW)Restarting services...$(NC)"
	docker compose -f infra/docker-compose.yml restart

ps: ## Show service status
	docker compose -f infra/docker-compose.yml ps

# Development helpers
dev: ## Start development environment with live reloading
	@echo "$(GREEN)Starting development environment...$(NC)"
	docker compose -f infra/docker-compose.yml --env-file infra/.env up

logs: ## View logs from all services
	docker compose -f infra/docker-compose.yml logs -f

logs-backend: ## View backend logs only
	docker compose -f infra/docker-compose.yml logs -f backend

logs-frontend: ## View frontend logs only
	docker compose -f infra/docker-compose.yml logs -f frontend

logs-db: ## View database logs only
	docker compose -f infra/docker-compose.yml logs -f postgres

# Enhanced status and health checks
status: ## Show status of all services
	@echo "$(BLUE)Service Status:$(NC)"
	@docker compose -f infra/docker-compose.yml ps
	@echo ""
	@echo "$(BLUE)Health Checks:$(NC)"
	@curl -s http://localhost:8000/health 2>/dev/null | grep -q healthy && echo "$(GREEN)✓$(NC) Backend: Healthy" || echo "$(RED)✗$(NC) Backend: Unhealthy"
	@curl -s http://localhost:5173 >/dev/null 2>&1 && echo "$(GREEN)✓$(NC) Frontend: Running" || echo "$(RED)✗$(NC) Frontend: Not responding"
	@docker compose -f infra/docker-compose.yml exec -T postgres pg_isready -U dev -d xu2 >/dev/null 2>&1 && echo "$(GREEN)✓$(NC) Database: Connected" || echo "$(RED)✗$(NC) Database: Not connected"

health: ## Run comprehensive health check including authentication
	@echo "$(BLUE)🔍 Running comprehensive health check...$(NC)"
	@echo ""
	@echo "$(GREEN)Backend API Health:$(NC)"
	@curl -s http://localhost:8000/health 2>/dev/null && echo "" || echo "$(RED)❌ Backend API failed$(NC)"
	@echo ""
	@echo "$(GREEN)Authentication Test:$(NC)"
	@AUTH_RESULT=$$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
		-H "Content-Type: application/json" \
		-d '{"email":"student@example.com","password":"password123"}' 2>/dev/null) && \
		if echo "$$AUTH_RESULT" | grep -q "access_token"; then \
			echo "$(GREEN)✅ Authentication working$(NC)"; \
		else \
			echo "$(RED)❌ Authentication failed$(NC)"; \
			echo "Response: $$AUTH_RESULT"; \
		fi
	@echo ""
	@echo "$(GREEN)Database User Count:$(NC)"
	@USER_COUNT=$$(docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev -d xu2 -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | tr -d ' \n') && \
		echo "$(GREEN)✅ Users in database: $$USER_COUNT$(NC)" || echo "$(RED)❌ Database query failed$(NC)"

# Database management (enhanced)
migrate: ## Run database migrations
	@echo "$(GREEN)Running database migrations...$(NC)"
	docker compose -f infra/docker-compose.yml exec backend alembic upgrade head

db-init: ## Initialize database with default users
	@echo "$(GREEN)Initializing database with default users...$(NC)"
	docker compose -f infra/docker-compose.yml exec backend alembic upgrade head
	docker compose -f infra/docker-compose.yml exec backend python init_db.py

seed: ## Seed database (if seeds exist)
	@echo "$(GREEN)Seeding database...$(NC)"
	docker compose -f infra/docker-compose.yml exec backend python -m app.db.seeds

db-shell: ## Open database shell
	docker compose -f infra/docker-compose.yml exec postgres psql -U dev -d xu2

db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(RED)⚠️  WARNING: This will destroy all database data!$(NC)"
	@echo "$(YELLOW)Are you sure? Type 'yes' to continue:$(NC)"
	@read confirm && [ "$$confirm" = "yes" ] || (echo "Cancelled." && exit 1)
	@echo "$(YELLOW)Resetting database...$(NC)"
	docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev -d xu2 -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" >/dev/null 2>&1
	$(MAKE) db-init
	@echo "$(GREEN)✅ Database reset complete$(NC)"

# Code quality (enhanced)
fmt: fmt-backend fmt-frontend ## Format all code

fmt-backend: ## Format backend code
	@echo "$(GREEN)Formatting backend code...$(NC)"
	docker compose -f infra/docker-compose.yml exec backend ruff format . || echo "$(YELLOW)ruff format not available$(NC)"

fmt-frontend: ## Format frontend code
	@echo "$(GREEN)Formatting frontend code...$(NC)"
	docker compose -f infra/docker-compose.yml exec frontend npm run format || echo "$(YELLOW)npm format not available$(NC)"

lint: lint-backend lint-frontend ## Lint all code

lint-backend: ## Lint backend code
	@echo "$(GREEN)Linting backend code...$(NC)"
	docker compose -f infra/docker-compose.yml exec backend ruff check . || echo "$(YELLOW)ruff check not available$(NC)"
	docker compose -f infra/docker-compose.yml exec backend mypy . || echo "$(YELLOW)mypy not available$(NC)"

lint-frontend: ## Lint frontend code
	@echo "$(GREEN)Linting frontend code...$(NC)"
	docker compose -f infra/docker-compose.yml exec frontend npm run lint || echo "$(YELLOW)npm lint not available$(NC)"
	docker compose -f infra/docker-compose.yml exec frontend npm run type-check || echo "$(YELLOW)npm type-check not available$(NC)"

check: lint test ## Run all code quality checks

# Testing (enhanced)
test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	@echo "$(GREEN)Running backend tests...$(NC)"
	docker compose -f infra/docker-compose.yml exec backend pytest

test-frontend: ## Run frontend tests  
	@echo "$(GREEN)Running frontend tests...$(NC)"
	docker compose -f infra/docker-compose.yml exec frontend npm run test:run

test-frontend-watch: ## Run frontend tests in watch mode
	@echo "$(GREEN)Running frontend tests in watch mode...$(NC)"
	docker compose -f infra/docker-compose.yml exec frontend npm test

# Container shell access
shell-backend: ## Open shell in backend container
	docker compose -f infra/docker-compose.yml exec backend bash

shell-frontend: ## Open shell in frontend container
	docker compose -f infra/docker-compose.yml exec frontend sh

shell-db: ## Open shell in database container
	docker compose -f infra/docker-compose.yml exec postgres bash

# Backup and restore
backup: ## Create backup of database
	@echo "$(GREEN)Creating database backup...$(NC)"
	@mkdir -p backups
	@BACKUP_FILE="backups/xu2-backup-$$(date +%Y%m%d_%H%M%S).sql" && \
	docker compose -f infra/docker-compose.yml exec -T postgres pg_dump -U dev xu2 > $$BACKUP_FILE && \
	echo "$(GREEN)✅ Backup created: $$BACKUP_FILE$(NC)"

restore: ## Restore database from backup (requires BACKUP_FILE variable)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "$(RED)❌ Error: Please specify BACKUP_FILE=path/to/backup.sql$(NC)"; \
		echo "Example: make restore BACKUP_FILE=backups/xu2-backup-20250812_120000.sql"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Restoring database from $(BACKUP_FILE)...$(NC)"
	docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev xu2 < $(BACKUP_FILE)
	@echo "$(GREEN)✅ Database restored successfully$(NC)"

# Quick workflows
quick-test: ## Quick test after changes (restart backend only)
	@echo "$(YELLOW)Quick testing workflow...$(NC)"
	docker compose -f infra/docker-compose.yml restart backend
	@sleep 5
	$(MAKE) test-backend

quick-restart: ## Quick restart of main services
	@echo "$(YELLOW)Quick restart of main services...$(NC)"
	docker compose -f infra/docker-compose.yml restart backend frontend

# Development URLs
open: ## Open application URLs in browser
	@echo "$(GREEN)Opening application in browser...$(NC)"
	@if command -v open >/dev/null 2>&1; then \
		open http://localhost:5173; \
		sleep 1; \
		open http://localhost:8000/docs; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open http://localhost:5173 & \
		sleep 1; \
		xdg-open http://localhost:8000/docs & \
	else \
		echo "$(YELLOW)Please open these URLs manually:$(NC)"; \
		echo "  Frontend: http://localhost:5173"; \
		echo "  API Docs: http://localhost:8000/docs"; \
	fi

# Enhanced cleanup
clean: ## Clean containers, Python cache, and Node modules
	@echo "$(YELLOW)Cleaning development environment...$(NC)"
	docker compose -f infra/docker-compose.yml down -v
	@echo "$(YELLOW)Removing cache files...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Basic cleanup complete$(NC)"

# System information
info: ## Show system and project information
	@echo "$(BLUE)🎓 X-University Project Information$(NC)"
	@echo "==============================="
	@echo "Project: X-University Learning Platform"
	@echo "Frontend: React + TypeScript + Vite"
	@echo "Backend: Python + FastAPI"
	@echo "Database: PostgreSQL"
	@echo ""
	@echo "$(BLUE)🌐 Service URLs:$(NC)"
	@echo "Frontend:        http://localhost:5173"
	@echo "Backend API:     http://localhost:8000"
	@echo "API Docs:        http://localhost:8000/docs"
	@echo "Database:        localhost:5432"
	@echo ""
	@echo "$(BLUE)👥 Default Accounts:$(NC)"
	@echo "Admin:           admin@example.com / password123"
	@echo "Instructor:      instructor@example.com / password123"
	@echo "Student:         student@example.com / password123"
	@echo ""
	@echo "$(BLUE)🐳 Docker Status:$(NC)"
	@docker system df 2>/dev/null || echo "Docker not available"

# Troubleshooting
troubleshoot: ## Show troubleshooting guide
	@echo "$(BLUE)🔧 X-University Troubleshooting Guide$(NC)"
	@echo "===================================="
	@echo ""
	@echo "$(YELLOW)📋 Common Issues & Solutions:$(NC)"
	@echo ""
	@echo "$(GREEN)1. Services won't start:$(NC)"
	@echo "   make down && make fresh"
	@echo ""
	@echo "$(GREEN)2. Authentication not working:$(NC)"
	@echo "   make db-init"
	@echo "   make health  # Check if users exist"
	@echo ""
	@echo "$(GREEN)3. Database connection issues:$(NC)"
	@echo "   make logs-db"
	@echo "   make db-reset  # ⚠️  WARNING: destroys data"
	@echo ""
	@echo "$(GREEN)4. Backend API errors:$(NC)"
	@echo "   make logs-backend"
	@echo "   make quick-restart"
	@echo ""
	@echo "$(GREEN)5. Frontend not loading:$(NC)"
	@echo "   make logs-frontend"
	@echo "   docker compose -f infra/docker-compose.yml restart frontend"
	@echo ""
	@echo "$(GREEN)6. Complete reset (nuclear option):$(NC)"
	@echo "   ./scripts/cleanup.sh && ./scripts/setup.sh --clean"
	@echo ""
	@echo "$(BLUE)📊 Current Status:$(NC)"
	@$(MAKE) status
