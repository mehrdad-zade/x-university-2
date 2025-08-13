# Setup and Installation Guide

Complete guide for setting up the X University 2.0 development environment.

## 🚀 Quick Start

### Fresh Setup (Recommended)
```bash
# Complete fresh setup - removes everything and rebuilds
make fresh
# OR
./scripts/cleanup.sh && ./scripts/setup.sh --clean
```

### Existing Environment Setup
```bash
# Preserves existing data
make setup
# OR  
./scripts/setup.sh
```

### Single Command Setup
```bash
# Standard setup with all features
./scripts/setup.sh                    

# Available options
./scripts/setup.sh --clean           # Clean install (removes existing environments)
./scripts/setup.sh --skip-tests      # Skip test execution during setup
./scripts/setup.sh --skip-browser    # Don't auto-open browser tabs
```

## Prerequisites

### Required Software

| Software | Version | Installation |
|----------|---------|-------------|
| **Python** | 3.12.x (exact version required) | [Download](https://www.python.org/downloads/) |
| **Node.js** | ≥ 20.0 (tested with 23.6.1) | [Download](https://nodejs.org/) |
| **Docker Desktop** | Latest stable | [Download](https://www.docker.com/products/docker-desktop) |
| **Git** | Latest | [Download](https://git-scm.com/) |

### Platform-Specific Installation

#### macOS (Recommended: Homebrew)
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required tools
brew install python@3.12 node@20 git
brew link --force python@3.12
brew link node@20

# Install Docker Desktop manually from https://www.docker.com/products/docker-desktop
```

#### Ubuntu/Debian Linux
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo apt install docker.io docker-compose-plugin git
```

#### RHEL/Fedora/CentOS
```bash
sudo dnf install python3.12 python3.12-pip python3.12-devel
curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -
sudo dnf install nodejs docker docker-compose git
```

### Version Verification
```bash
# Check versions (must match requirements)
python3.12 --version  # Must be 3.12.x
node --version         # Must be ≥ 20.0
docker --version
git --version
```

## Development Commands

### Service Management
```bash
make up              # Start all services
make down            # Stop all services
make restart         # Restart all services
make quick-restart   # Restart just backend/frontend
make logs            # View all service logs
make logs-backend    # Backend logs only
make logs-frontend   # Frontend logs only
```

### Development Tasks
```bash
make test            # Run all tests (backend + frontend)
make test-backend    # Run only backend tests
make test-frontend   # Run only frontend tests
make fmt             # Format all code (Python + JavaScript/TypeScript)
make lint            # Run linters
make migrate         # Run database migrations
make seed            # Load seed data
```

### Database Management
```bash
make db-init         # Initialize with default users
make db-reset        # ⚠️  Destroys all data!
```

### Health Checks
```bash
make health          # Comprehensive health check (includes auth test)
make status          # Show service status
```

## Services After Setup

Once setup completes successfully, you'll have access to:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Main user interface |
| **Backend API** | http://localhost:8000 | Core application services |
| **API Documentation** | http://localhost:8000/docs | Interactive Swagger/OpenAPI interface |
| **Health Check** | http://localhost:8000/health | Service health monitoring |
| **PostgreSQL** | localhost:5432 | Primary database (credentials in .env) |
| **Neo4j Browser** | http://localhost:7474 | Graph database (if enabled) |

## Default Login Credentials

Test the authentication system with these development credentials:

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@example.com | password123 |
| **Instructor** | instructor@example.com | password123 |
| **Student** | student@example.com | password123 |

> **Note**: These are development-only credentials. In production, create secure admin accounts through the API.

## Troubleshooting

### Common Issues and Solutions

#### Authentication fails / "401 Unauthorized"
```bash
make db-init         # Recreate default users
make health          # Verify authentication works
```

#### Services won't start / Container conflicts
```bash
make fresh           # Nuclear option - complete reset
```

#### Database connection problems
```bash
make logs-db         # Check database logs
make db-reset        # Last resort (destroys data)
```

#### Backend API not responding
```bash
make logs-backend    # Check backend logs
make quick-restart   # Restart main services
```

### Debug Commands
```bash
make troubleshoot    # Troubleshooting guide
make info            # Project information
docker ps            # Check container status
```

## Development Workflow

### Daily Development Process
1. **Start working**: `make setup` or `make fresh` (first time)
2. **Check health**: `make health` 
3. **Make changes**: Edit code (hot reload enabled)
4. **Test changes**: `make test` or `make quick-test`
5. **View logs**: `make logs-backend` or `make logs-frontend`
6. **Restart if needed**: `make quick-restart`
7. **Full reset if broken**: `make fresh`

### Code Quality Standards

#### Backend (Python/FastAPI)
- **Type Safety**: Full mypy support with strict type checking
- **Code Quality**: `ruff` for linting, `black` for formatting
- **Testing**: `pytest` with async support, minimum 80% coverage
- **Database**: Alembic-only migrations, never raw schema changes
- **API Design**: Pydantic schemas at boundaries, separate DTOs from ORM models

#### Frontend (React/TypeScript)
- **Type Safety**: TypeScript strict mode enabled
- **Code Quality**: ESLint + Prettier for consistent formatting
- **Testing**: React Testing Library for component tests
- **State Management**: React Query for server state, Zustand for client state
- **Styling**: TailwindCSS utility classes

## Environment Features

### Automated Setup Benefits
The setup script automatically:
- ✅ Verifies and installs prerequisites (with platform-specific instructions)
- ✅ Sets up isolated Python virtual environment with dependencies
- ✅ Configures Node.js environment and installs frontend dependencies
- ✅ Launches Docker services (PostgreSQL, optional Neo4j)
- ✅ Executes database migrations and initializes authentication
- ✅ Runs comprehensive test suites (backend API + frontend components)
- ✅ Opens browser tabs in existing window (no new windows!)

### Hot Reload Support
- **Backend**: FastAPI auto-reloads on Python file changes
- **Frontend**: Vite provides instant hot module replacement
- **Database**: Persistent data across container restarts

### Testing Integration
```bash
make test              # All tests
make health            # Authentication test
make quick-test        # Fast backend tests only
```

## Complete Command Reference

```bash
make help              # Show all available commands
make setup             # Standard setup
make fresh             # Complete fresh setup
make status            # Show service status
make health            # Comprehensive health check
make info              # Project information
make troubleshoot      # Troubleshooting guide
make open              # Open URLs in browser
```

## Important Notes

- **Always use `make fresh`** for a guaranteed clean setup
- **Check `make health`** to verify authentication is working
- **Use `make troubleshoot`** when things go wrong
- **Database password changes require `make db-init`**
- **Container naming conflicts are resolved by `make fresh`**
- **Python 3.13**: Not yet supported due to dependency compatibility
- **Docker Desktop**: Must be running before executing setup script
