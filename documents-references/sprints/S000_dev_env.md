# Sprint 0 — Dev environment and scaffolding

## Goals
Monorepo, local Docker, hot reload, migrations, tests.

## Deliverables
- Repo layout
```
x-university-2/
  backend/app/{api,core,db,services,schemas,workers}/
  backend/alembic/
  backend/tests/
  frontend/src/{components,lib,pages,routes,styles}/
  infra/{docker-compose.yml,.env.example,README.md}
  sprints/
```

- Backend deps: fastapi, uvicorn[standard], pydantic, python-jose[cryptography], passlib[bcrypt], psycopg, SQLAlchemy 2, alembic, httpx, structlog, neo4j, pytest, pytest-asyncio, mypy, ruff.
- Frontend deps: react, react-dom, typescript, vite, react-router-dom, tailwindcss, postcss, autoprefixer, axios, zod, jotai or zustand.
- Makefile targets: up, down, logs, migrate, seed, fmt, test.

## Acceptance criteria
- `docker compose up` brings API 8000 and web 5173. Postgres reachable. Neo4j optional.
- `GET /health` returns 200.
