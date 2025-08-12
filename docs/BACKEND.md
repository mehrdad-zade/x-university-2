# X University Backend

## Requirements
- Python 3.12 (3.13 not yet supported by some dependencies)
- pip (latest version recommended)

Note: Python 3.13 is too new and not yet supported by all dependencies. Please use Python 3.12 for now.

## Technology Stack
- FastAPI
- SQLAlchemy 2.0 (async)
- Alembic migrations
- PostgreSQL 16
- Neo4j 5.x (optional)
- JWT authentication
- OpenAI integration
- Stripe/PayPal payments

## Project Structure
```
backend/
├── alembic/          # Database migrations
├── app/
│   ├── api/          # API routes and endpoints
│   ├── core/         # Core functionality and config
│   ├── db/           # Database models and setup
│   ├── schemas/      # Pydantic models
│   ├── services/     # Business logic
│   └── workers/      # Background tasks
└── tests/            # Test suite
```

## Development
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run tests:
```bash
pytest
```

3. Format code:
```bash
ruff format .
```

4. Type checking:
```bash
mypy .
```

## API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
