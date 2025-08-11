# x-university-2 — Dev spec

Status: 2025-08-10

## Quick Setup Guide

### Prerequisites

Required software versions:
- Python 3.12.x (3.13 not yet supported)
- Node.js >= 20.0 (tested with 23.6.1)
- Docker and Docker Compose
- Git

To check your versions:
```bash
python3 --version
node --version
docker --version
```

### Setup Instructions
```bash
# Make setup script executable (Required once)
chmod +x setup.sh

# Run complete setup
./setup.sh         # Regular setup
./setup.sh --clean # Clean setup (removes existing environments)
```

### Daily Development Commands (via Makefile)
```bash
make up      # Start all services
make down    # Stop all services
make logs    # View service logs
make test    # Run all tests
make fmt     # Format code
```

For more details about setup and services, see below.

## Technology Stack
- Backend: FastAPI (Python 3.12), SQLAlchemy 2, Alembic, Pydantic v2
- Auth: JWT access + refresh, bcrypt passwords
- DBs: PostgreSQL (relational), Neo4j (optional; for learning-path graph, not buildings)
- Frontend: React + TypeScript + Vite + Tailwind
- Payments: Stripe + PayPal (test mode)
- AI: OpenAI API for course and lesson material
- Containers: Docker Compose for local dev

Notes
- There is no physical-campus map. Neo4j is used for learning-path graphs only, and can be disabled.
- Run locally. Secrets via env vars. No key vaults or VPC needed for dev.

## Monorepo layout
```
x-university-2/
  backend/
  frontend/
  infra/
  sprints/   # these planning files (not required at runtime)
```

## Development Tools

### setup.sh
The setup script handles complete environment setup and service startup:
- Creates/activates Python virtual environment
- Sets up Node.js environment
- Installs all dependencies
- Configures environment variables
- Starts Docker services
- Runs migrations
- Executes tests

Options:
```bash
./setup.sh           # Regular setup
./setup.sh --clean   # Remove existing environments and start fresh
./setup.sh --skip-tests  # Skip running tests during setup
```

### Makefile
For daily development tasks:
```bash
make up          # Start services
make down        # Stop services
make logs        # View logs
make test        # Run tests
make fmt         # Format code
make lint        # Run linters
make migrate     # Run DB migrations
make seed        # Load seed data
```

### Available Services
After setup:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Neo4j (optional): http://localhost:7474

## Docker Compose (dev)
Example `infra/docker-compose.yml` summary:
- postgres:16 → 5432
- neo4j:5.x → 7474, 7687 (optional)
- backend (uvicorn reload) → 8000
- frontend (Vite dev) → 5173

## Env template
See `infra/.env.example`:
```
POSTGRES_USER=dev
POSTGRES_PASSWORD=devpass
POSTGRES_DB=xu2
DATABASE_URL=postgresql+psycopg://dev:devpass@postgres:5432/xu2

NEO4J_PASSWORD=devpass
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
ENABLE_NEO4J=false

API_PORT=8000
SECRET_KEY=change-me
ACCESS_TOKEN_EXPIRES_MINUTES=30
REFRESH_TOKEN_EXPIRES_DAYS=7

OPENAI_API_KEY=sk-...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...
```

## Coding standards
- Type-first: mypy on backend, TS strict on frontend
- Lint: ruff + black, eslint + prettier
- Tests: pytest (80%+ on backend routes), React Testing Library for key flows
- Migrations: Alembic only, never raw schema changes
- API: Pydantic schemas at edges, DTOs separate from ORM
- Logs: structlog JSON
- CI ready: format, lint, test

## High-level modules
- Auth
- Courses and lessons
- AI generation pipeline
- Progress tracking
- Payments
- Personal teacher chatbot
- Learning-path graph (optional, no buildings)

---

See `sprints/` for actionable work. 
