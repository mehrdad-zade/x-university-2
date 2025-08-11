.PHONY: up down ps logs migrate seed fmt lint test clean

# Docker commands
up:
	docker compose -f infra/docker-compose.yml --env-file infra/.env up -d --build

down:
	docker compose -f infra/docker-compose.yml --env-file infra/.env down

ps:
	docker compose -f infra/docker-compose.yml ps

logs:
	docker compose -f infra/docker-compose.yml logs -f

# Database commands
migrate:
	docker compose -f infra/docker-compose.yml exec backend alembic upgrade head

seed:
	docker compose -f infra/docker-compose.yml exec backend python -m app.db.seeds

# Code quality
fmt: fmt-backend fmt-frontend

fmt-backend:
	docker compose -f infra/docker-compose.yml exec backend ruff format .
	docker compose -f infra/docker-compose.yml exec backend black .

fmt-frontend:
	docker compose -f infra/docker-compose.yml exec frontend npm run format

lint: lint-backend lint-frontend

lint-backend:
	docker compose -f infra/docker-compose.yml exec backend ruff check .
	docker compose -f infra/docker-compose.yml exec backend mypy .

lint-frontend:
	docker compose -f infra/docker-compose.yml exec frontend npm run lint
	docker compose -f infra/docker-compose.yml exec frontend npm run type-check

# Testing
test: test-backend test-frontend

test-backend:
	docker compose -f infra/docker-compose.yml exec backend pytest

test-frontend:
	docker compose -f infra/docker-compose.yml exec frontend npm test

# Cleanup
clean:
	docker compose -f infra/docker-compose.yml down -v
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name "node_modules" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
