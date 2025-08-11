# X University Infrastructure

## Overview
This directory contains Docker Compose configuration and environment setup for running X University locally.

## Services
- PostgreSQL 16 (Main Database)
- Neo4j 5.x (Optional - Learning Path Graphs)
- FastAPI Backend
- React Frontend

## Getting Started

1. Copy environment template:
```bash
cp .env.example .env
```

2. Configure environment variables in `.env`

3. Start all services:
```bash
make up
```

4. Initialize database:
```bash
make migrate
```

## Development Commands

### Docker Control
- `make up` - Start all services
- `make down` - Stop all services
- `make logs` - View service logs
- `make ps` - List running services

### Database
- `make migrate` - Run database migrations
- `make seed` - Load seed data (if available)

### Code Quality
- `make fmt` - Format code (backend + frontend)
- `make lint` - Run linters
- `make test` - Run all tests

### Service URLs
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Neo4j Browser: http://localhost:7474 (when enabled)

## Architecture Notes
- Backend and frontend use hot-reload for development
- PostgreSQL data persisted in Docker volume
- Neo4j is optional and can be disabled in `.env`
