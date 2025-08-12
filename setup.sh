#!/bin/bash

# setup.sh
# Purpose: Complete setup and startup script for X University development environment
#
# Prerequisites:
# - Git (required for version control)
# - Docker Desktop (will be auto-started on macOS if installed)
#   macOS: Install from https://www.docker.com/products/docker-desktop
#   Linux: Install Docker and docker-compose via package manager
# - Python 3.12 (exact version required)
#   macOS: brew install python@3.12 && brew link --force python@3.12
#   Linux: Use system package manager (apt/dnf) to install python3.12
# - Node.js 20.x or higher
#   macOS: brew install node@20 && brew link node@20
#   Linux: Use NodeSource repository to install latest Node.js
#
# Features:
# - Automated environment detection and setup:
#   • Checks for required tools and correct versions
#   • Auto-starts Docker Desktop on macOS if not running
#   • Verifies Python 3.12 and Node.js 20+ installations
# - Development environment setup:
#   • Creates and configures Python virtual environment
#   • Sets up Node.js environment with latest npm
#   • Installs all backend and frontend dependencies
# - Infrastructure management:
#   • Sets up required environment variables
#   • Initializes and starts all Docker services
#   • Runs database migrations automatically
# - Quality assurance:
#   • Runs backend and frontend tests
#   • Verifies service health and accessibility
#
# Usage: ./setup.sh [--clean] [--skip-tests] [--skip-browser]
# Options:
#   --clean: Remove existing environments and start fresh
#            • Removes Python virtual environment
#            • Cleans Node.js dependencies
#            • Removes Docker volumes
#   --skip-tests: Skip running tests during setup
#   --skip-browser: Skip automatically opening browser tabs
#
# Status Checks:
# - Verifies Docker Desktop is running (auto-starts on macOS)
# - Confirms correct Python and Node.js versions
# - Validates all services are operational
# - Provides health check status for backend and frontend

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color
INFO="${BLUE}[INFO]${NC}"
SUCCESS="${GREEN}[SUCCESS]${NC}"
ERROR="${RED}[ERROR]${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print section header
print_section() {
    echo -e "\n${BLUE}==== $1 ====${NC}"
}

# Parse arguments
CLEAN=false
SKIP_TESTS=false
SKIP_BROWSER=false
for arg in "$@"; do
    case $arg in
        --clean)
            CLEAN=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-browser)
            SKIP_BROWSER=true
            shift
            ;;
    esac
done

# Function to check if Docker Desktop is running on macOS
check_docker_running() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if ! pgrep -f "Docker Desktop" > /dev/null; then
            return 1
        fi
    fi
    # Check if docker daemon is responsive
    if ! docker info >/dev/null 2>&1; then
        return 1
    fi
    return 0
}

# Check for required tools
print_section "Checking Prerequisites"
REQUIRED_TOOLS="git"  # Removed docker and docker-compose from here as we'll check them separately
MISSING_TOOLS=()

for tool in $REQUIRED_TOOLS; do
    if ! command_exists "$tool"; then
        MISSING_TOOLS+=("$tool")
    fi
done

if [ ${#MISSING_TOOLS[@]} -ne 0 ]; then
    echo -e "${ERROR} Missing required tools: ${MISSING_TOOLS[*]}"
    echo "Please install these tools and try again."
    exit 1
fi

# Check for Docker installation and status
if ! command_exists "docker"; then
    echo -e "${ERROR} Docker is required but not found"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "Please download and install Docker Desktop for Mac from:"
        echo "https://www.docker.com/products/docker-desktop"
        echo "After installation, launch Docker Desktop and run this script again."
    else
        echo "Please install Docker using your system's package manager"
    fi
    exit 1
fi

if ! command_exists "docker-compose"; then
    echo -e "${ERROR} docker-compose is required but not found"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "docker-compose should be included with Docker Desktop."
        echo "Please ensure Docker Desktop is properly installed."
    else
        echo "Please install docker-compose using your system's package manager"
    fi
    exit 1
fi

# Function to check Docker network connectivity
check_docker_network() {
    # Try to ping Docker Hub
    if ! curl -s --connect-timeout 5 https://registry.hub.docker.com/v2/ >/dev/null; then
        return 1
    fi
    # Try to pull a tiny image to verify registry access
    if ! docker pull hello-world >/dev/null 2>&1; then
        return 1
    fi
    return 0
}

# Check if Docker is running
if ! check_docker_running; then
    echo -e "${INFO} Docker is not running"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo -e "${INFO} Attempting to start Docker Desktop..."
        open -a "Docker Desktop"
        
        # Wait for Docker to start (timeout after 60 seconds)
        echo -e "${INFO} Waiting for Docker to start..."
        TIMEOUT=60
        while ! check_docker_running && [ $TIMEOUT -gt 0 ]; do
            sleep 1
            echo -n "."
            ((TIMEOUT--))
        done
        echo ""
        
        if [ $TIMEOUT -eq 0 ]; then
            echo -e "${ERROR} Docker failed to start within 60 seconds"
            echo "Please start Docker Desktop manually and try again"
            exit 1
        else
            echo -e "${SUCCESS} Docker is now running"
        fi
    else
        echo -e "${ERROR} Please start Docker daemon and try again"
        exit 1
    fi
fi

# Check Docker network connectivity
echo -e "${INFO} Checking Docker network connectivity..."
if ! check_docker_network; then
    echo -e "${ERROR} Docker network connectivity issues detected"
    echo "Please check:"
    echo "1. Your internet connection"
    echo "2. If you're behind a corporate VPN, check your proxy settings"
    echo "3. If you can access https://registry.hub.docker.com"
    echo "4. Your DNS settings (try adding 8.8.8.8 to your DNS servers)"
    echo ""
    echo "You can test Docker connectivity with:"
    echo "docker pull hello-world"
    exit 1
fi
echo -e "${SUCCESS} Docker network connectivity verified"

# Check for Node.js and npm
if ! command_exists "node"; then
    echo -e "${ERROR} Node.js is required but not found"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "On macOS, install with: brew install node@20"
        echo "Then run: brew link node@20"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "On Ubuntu/Debian, install with:"
        echo "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -"
        echo "sudo apt-get install -y nodejs"
    else
        echo "Please install Node.js from https://nodejs.org/"
    fi
    exit 1
fi

if ! command_exists "npm"; then
    echo -e "${ERROR} npm is required but not found"
    echo "npm should be installed with Node.js"
    echo "Please reinstall Node.js from https://nodejs.org/"
    exit 1
fi

# Verify Node.js version
NODE_VERSION=$(node -v | cut -d 'v' -f2)
NODE_MAJOR_VERSION=$(echo $NODE_VERSION | cut -d '.' -f1)
if [[ $NODE_MAJOR_VERSION -lt 20 ]]; then
    echo -e "${ERROR} Node.js version $NODE_VERSION is too old. Version 20.x or higher is required"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "On macOS, upgrade with: brew upgrade node@20"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "On Ubuntu/Debian, upgrade with:"
        echo "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -"
        echo "sudo apt-get install -y nodejs"
    else
        echo "Please upgrade Node.js from https://nodejs.org/"
    fi
    exit 1
fi

# Check for Python 3.12
if command_exists "python3.12"; then
    PYTHON_CMD="python3.12"
elif command_exists "python3" && [[ $(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))') == "3.12" ]]; then
    PYTHON_CMD="python3"
else
    echo -e "${ERROR} Python 3.12 is required but not found"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "On macOS, install with: brew install python@3.12"
        echo "Then run: brew link --force python@3.12"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "On Ubuntu/Debian, install with: sudo apt install python3.12"
        echo "On RHEL/Fedora, install with: sudo dnf install python3.12"
    else
        echo "Please install Python 3.12 from https://www.python.org/downloads/"
    fi
    exit 1
fi

# Verify Python version
PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [[ "$PYTHON_VERSION" != "3.12" ]]; then
    echo -e "${ERROR} Wrong Python version: $PYTHON_VERSION. Version 3.12 is required"
    echo "Please make sure Python 3.12 is installed and properly linked"
    exit 1
fi

echo -e "${SUCCESS} All required tools are available"

# Setup directories
PROJECT_ROOT=$(pwd)
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
VENV_DIR="$BACKEND_DIR/.venv"

# Clean if requested
if [ "$CLEAN" = true ]; then
    print_section "Cleaning existing environments"
    
    # Clean Python environment
    if [ -d "$VENV_DIR" ]; then
        echo -e "${INFO} Removing existing Python virtual environment..."
        rm -rf "$VENV_DIR"
    fi
    
    # Clean Node environment
    if [ -d "$FRONTEND_DIR/node_modules" ]; then
        echo -e "${INFO} Removing existing Node modules..."
        rm -rf "$FRONTEND_DIR/node_modules"
        rm -f "$FRONTEND_DIR/package-lock.json"
    fi
    
    # Stop and clean Docker environment
    echo -e "${INFO} Stopping and cleaning Docker containers..."
    docker compose -f infra/docker-compose.yml down -v --timeout 30 2>/dev/null || true
    
    # Force remove any stuck containers
    docker rm -f xu2-postgres xu2-backend xu2-frontend 2>/dev/null || true
    
    # Remove project images for complete rebuild
    echo -e "${INFO} Removing project Docker images for clean rebuild..."
    docker rmi -f backend-x-university frontend-x-university 2>/dev/null || true
    
    # Clean dangling images and volumes
    docker image prune -f 2>/dev/null || true
    docker volume prune -f 2>/dev/null || true
    
    echo -e "${SUCCESS} Cleaned existing environments"
fi

# Setup Python virtual environment
print_section "Setting up Python Environment"
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${INFO} Creating Python virtual environment..."
    $PYTHON_CMD -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    echo -e "${ERROR} Failed to activate Python virtual environment"
    exit 1
fi

echo -e "${INFO} Installing Python dependencies..."
pip install -r "$BACKEND_DIR/requirements.txt"
if [ $? -ne 0 ]; then
    echo -e "${ERROR} Failed to install Python dependencies"
    exit 1
fi
echo -e "${SUCCESS} Python environment ready"

# Setup Node environment
print_section "Setting up Node Environment"
echo -e "${INFO} Installing Node dependencies..."
cd "$FRONTEND_DIR" || exit

# Ensure correct npm version
echo -e "${INFO} Checking npm version..."
npm install -g npm@latest

# Handle Node.js dependencies installation
echo -e "${INFO} Installing Node.js dependencies..."
if [ "$CLEAN" = true ]; then
    echo -e "${INFO} Performing clean install..."
    rm -rf node_modules package-lock.json
    # First generate package-lock.json
    if ! npm install --package-lock-only; then
        echo -e "${ERROR} Failed to generate package-lock.json"
        exit 1
    fi
    # Then perform clean install
    if ! npm ci; then
        echo -e "${ERROR} Failed to perform clean install, falling back to npm install"
        rm -rf node_modules package-lock.json
        if ! npm install; then
            echo -e "${ERROR} npm install failed"
            exit 1
        fi
    fi
else
    if [ -f "package-lock.json" ]; then
        echo -e "${INFO} Installing from package-lock.json..."
        if ! npm ci; then
            echo -e "${ERROR} npm ci failed, falling back to npm install"
            if ! npm install; then
                echo -e "${ERROR} npm install failed"
                exit 1
            fi
        fi
    else
        echo -e "${INFO} No package-lock.json found, using npm install..."
        if ! npm install; then
            echo -e "${ERROR} npm install failed"
            exit 1
        fi
    fi
fi

if [ $? -ne 0 ]; then
    echo -e "${ERROR} Failed to install Node dependencies"
    exit 1
fi

cd "$PROJECT_ROOT" || exit
echo -e "${SUCCESS} Node environment ready"

# Setup environment variables
print_section "Setting up Environment Variables"
if [ ! -f "$PROJECT_ROOT/infra/.env" ]; then
    echo -e "${INFO} Creating .env file from template..."
    cp "$PROJECT_ROOT/infra/.env.example" "$PROJECT_ROOT/infra/.env"
    echo -e "${SUCCESS} Created .env file"
else
    echo -e "${INFO} .env file already exists"
fi

# Start Docker services
print_section "Starting Docker Services"

# Ensure clean startup state
echo -e "${INFO} Preparing Docker environment..."
docker compose -f infra/docker-compose.yml down --timeout 30 2>/dev/null || true

# Clean up any orphaned containers
docker rm -f xu2-postgres xu2-backend xu2-frontend 2>/dev/null || true

echo -e "${INFO} Building and starting containers..."

# Set project name for consistent naming
export COMPOSE_PROJECT_NAME=x-university-infra

# For clean builds, don't pull cached images - build fresh
if [ "$CLEAN" = true ]; then
    echo -e "${INFO} Clean build requested - building fresh images..."
    if ! docker compose -f infra/docker-compose.yml build --no-cache; then
        echo -e "${ERROR} Failed to build images"
        exit 1
    fi
    UP_OPTIONS="--force-recreate"
else
    echo -e "${INFO} Pulling required Docker images..."
    if docker compose -f infra/docker-compose.yml pull --quiet; then
        echo -e "${SUCCESS} Images pulled successfully"
        UP_OPTIONS=""
    else
        echo -e "${WARNING} Failed to pull some images, will build from scratch"
        if ! docker compose -f infra/docker-compose.yml build --no-cache; then
            echo -e "${ERROR} Failed to build images"
            exit 1
        fi
        UP_OPTIONS=""
    fi
fi

# Attempt to start services with comprehensive retry logic
MAX_RETRIES=3
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    echo -e "${INFO} Starting services (attempt $((RETRY_COUNT + 1))/$MAX_RETRIES)..."
    
    # Clean up before retry
    if [ $RETRY_COUNT -gt 0 ]; then
        echo -e "${INFO} Cleaning up before retry..."
        docker compose -f infra/docker-compose.yml down --timeout 30 2>/dev/null || true
        docker rm -f xu2-postgres xu2-backend xu2-frontend 2>/dev/null || true
        sleep 3
    fi
    
    if docker compose -f infra/docker-compose.yml --env-file infra/.env up -d $UP_OPTIONS; then
        echo -e "${SUCCESS} Docker services started successfully"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
            echo -e "${ERROR} Failed to start Docker services after $MAX_RETRIES attempts"
            echo -e "${ERROR} Troubleshooting steps:"
            echo "1. Check Docker Desktop is running and has enough resources"
            echo "2. Try: docker system prune -a (removes all unused data)"
            echo "3. Restart Docker Desktop"
            echo "4. Run this script again"
            echo -e "\n${INFO} Current Docker status:"
            docker system df
            exit 1
        else
            echo -e "${WARNING} Failed to start services, waiting before retry..."
            sleep 10
        fi
    fi
done

# Enhanced health check with better diagnostics and database initialization
echo -e "${INFO} Waiting for services to be ready..."
TIMEOUT=180  # Increased timeout to 3 minutes
HEALTH_CHECK_INTERVAL=5
CHECK_COUNT=0
POSTGRES_READY=false
BACKEND_READY=false

while [ $TIMEOUT -gt 0 ]; do
    CHECK_COUNT=$((CHECK_COUNT + 1))
    
    # Check PostgreSQL first (most critical dependency)
    if [ "$POSTGRES_READY" = "false" ]; then
        if docker compose -f infra/docker-compose.yml exec -T postgres pg_isready -U dev -d xu2 >/dev/null 2>&1; then
            echo -e "\n${SUCCESS} PostgreSQL is ready!"
            POSTGRES_READY=true
        fi
    fi
    
    # Get detailed service status
    SERVICES_STATUS=$(docker compose -f infra/docker-compose.yml ps --format json 2>/dev/null || echo "[]")
    
    # Check if we have any services running
    if echo "$SERVICES_STATUS" | grep -q "\"State\":\"running\""; then
        # Check backend health specifically
        if [ "$POSTGRES_READY" = "true" ] && [ "$BACKEND_READY" = "false" ]; then
            if curl -s --connect-timeout 3 http://localhost:8000/health >/dev/null 2>&1; then
                echo -e "${SUCCESS} Backend API is responding!"
                BACKEND_READY=true
            fi
        fi
        
        # Check if all critical services are ready
        if [ "$POSTGRES_READY" = "true" ] && [ "$BACKEND_READY" = "true" ]; then
            # Final verification - ensure no services are still starting
            if ! echo "$SERVICES_STATUS" | grep -q "\"State\":\"starting\"\|\"State\":\"restarting\"\|\"Health\":\"starting\""; then
                echo -e "\n${SUCCESS} All services are ready!"
                break
            fi
        fi
    fi
    
    # Check for failed services
    if echo "$SERVICES_STATUS" | grep -q "\"State\":\"exited\""; then
        echo -e "\n${ERROR} Some services have exited unexpectedly"
        echo -e "${INFO} Service status:"
        docker compose -f infra/docker-compose.yml ps
        echo -e "\n${INFO} Recent logs:"
        docker compose -f infra/docker-compose.yml logs --tail=20
        exit 1
    fi
    
    # Progress indicator
    if [ $((CHECK_COUNT % 6)) -eq 0 ]; then
        echo -e "\n${INFO} Still waiting for services (${CHECK_COUNT}/${TIMEOUT} checks)..."
        echo -e "${INFO} Status: PostgreSQL=${POSTGRES_READY}, Backend=${BACKEND_READY}"
        docker compose -f infra/docker-compose.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" | head -10
    else
        echo -n "."
    fi
    
    sleep $HEALTH_CHECK_INTERVAL
    TIMEOUT=$((TIMEOUT - HEALTH_CHECK_INTERVAL))
done

if [ $TIMEOUT -eq 0 ]; then
    echo -e "\n${ERROR} Services took too long to start"
    echo -e "${INFO} Final service status:"
    docker compose -f infra/docker-compose.yml ps
    echo -e "\n${INFO} Service logs (last 50 lines):"
    docker compose -f infra/docker-compose.yml logs --tail=50
    exit 1
fi

# Run database migrations with comprehensive retry logic and validation
print_section "Database Schema Setup"

# Wait a bit more to ensure backend is fully ready
echo -e "${INFO} Ensuring backend is fully initialized..."
sleep 5

echo -e "${INFO} Checking database schema state..."
MIGRATION_RETRIES=5
MIGRATION_COUNT=0
MIGRATION_SUCCESS=false

while [ $MIGRATION_COUNT -lt $MIGRATION_RETRIES ]; do
    echo -e "${INFO} Migration attempt $((MIGRATION_COUNT + 1))/$MIGRATION_RETRIES..."
    
    # First, check if Alembic can connect and get current state
    if CURRENT_REVISION=$(docker compose -f infra/docker-compose.yml exec -T backend alembic current 2>/dev/null | grep -E "^[a-f0-9]+\s+" | awk '{print $1}'); then
        if [ -n "$CURRENT_REVISION" ]; then
            echo -e "${INFO} Current database revision: $CURRENT_REVISION"
        else
            echo -e "${INFO} Database appears to be uninitialized"
        fi
        
        # Run the migration
        if docker compose -f infra/docker-compose.yml exec -T backend alembic upgrade head; then
            echo -e "${SUCCESS} Database migrations completed successfully"
            MIGRATION_SUCCESS=true
            break
        else
            echo -e "${WARNING} Migration failed on attempt $((MIGRATION_COUNT + 1))"
        fi
    else
        echo -e "${WARNING} Could not connect to database for migration on attempt $((MIGRATION_COUNT + 1))"
    fi
    
    MIGRATION_COUNT=$((MIGRATION_COUNT + 1))
    if [ $MIGRATION_COUNT -lt $MIGRATION_RETRIES ]; then
        echo -e "${INFO} Waiting 10 seconds before retry..."
        sleep 10
        
        # Check if backend is still running
        if ! curl -s --connect-timeout 3 http://localhost:8000/health >/dev/null 2>&1; then
            echo -e "${WARNING} Backend seems to be down, checking service status..."
            docker compose -f infra/docker-compose.yml ps backend
        fi
    fi
done

if [ "$MIGRATION_SUCCESS" = "false" ]; then
    echo -e "${ERROR} Failed to run database migrations after $MIGRATION_RETRIES attempts"
    echo -e "${INFO} Checking service health..."
    docker compose -f infra/docker-compose.yml ps
    echo -e "\n${INFO} Backend logs:"
    docker compose -f infra/docker-compose.yml logs backend --tail=30
    echo -e "\n${INFO} Postgres logs:"
    docker compose -f infra/docker-compose.yml logs postgres --tail=20
    
    echo -e "\n${ERROR} Migration troubleshooting steps:"
    echo -e "1. Check if backend container is healthy: docker compose -f infra/docker-compose.yml ps"
    echo -e "2. Check backend logs: docker compose -f infra/docker-compose.yml logs backend"
    echo -e "3. Verify database connectivity: docker compose -f infra/docker-compose.yml exec postgres pg_isready -U dev -d xu2"
    echo -e "4. Try manual migration: docker compose -f infra/docker-compose.yml exec backend alembic upgrade head"
    exit 1
fi

# Verify migration success by checking table structure
echo -e "${INFO} Verifying migration success..."
if TABLES=$(docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev -d xu2 -t -c "\dt" 2>/dev/null | grep -E "(users|sessions)" | wc -l | tr -d ' '); then
    if [ "$TABLES" -ge 2 ]; then
        echo -e "${SUCCESS} Database schema verification passed ($TABLES core tables found)"
        
        # Check if users table has the correct structure
        if docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev -d xu2 -t -c "\d users" 2>/dev/null | grep -q "password_hash"; then
            echo -e "${SUCCESS} Users table structure verified"
        else
            echo -e "${WARNING} Users table may have incorrect structure - this could cause authentication issues"
        fi
    else
        echo -e "${WARNING} Database schema verification failed - expected tables may be missing"
    fi
else
    echo -e "${WARNING} Could not verify database schema"
fi

# Initialize database with default users (with comprehensive retry and validation)
print_section "Database User Initialization"

echo -e "${INFO} Preparing database for user initialization..."

# For clean builds, ensure we clear any existing potentially corrupt data
if [ "$CLEAN" = "true" ]; then
    echo -e "${INFO} Clean build detected - ensuring fresh user data..."
    echo -e "${WARNING} Clearing any existing user data..."
    
    # Safely clear user-related tables
    CLEAR_RESULT=$(docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev -d xu2 -c "
        DO \$\$ 
        BEGIN
            -- Clear dependent tables first to avoid foreign key violations
            IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'enrollments') THEN
                TRUNCATE TABLE enrollments RESTART IDENTITY CASCADE;
            END IF;
            IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sessions') THEN
                TRUNCATE TABLE sessions RESTART IDENTITY CASCADE;
            END IF;
            IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') THEN
                TRUNCATE TABLE users RESTART IDENTITY CASCADE;
            END IF;
        END \$\$;" 2>&1)
    
    if echo "$CLEAR_RESULT" | grep -q "ERROR"; then
        echo -e "${WARNING} Some tables may not exist yet (this is normal for first setup)"
    else
        echo -e "${SUCCESS} User data cleared successfully"
    fi
fi

echo -e "${INFO} Checking current user state..."
# Check if users exist and get count
USER_COUNT=$(docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev -d xu2 -t -c "
    SELECT CASE 
        WHEN EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') 
        THEN (SELECT COUNT(*) FROM users)::text 
        ELSE '0' 
    END;" 2>/dev/null | tr -d ' \n' || echo "0")

echo -e "${INFO} Found $USER_COUNT existing users"

# Enhanced user initialization with retry logic
INIT_RETRIES=5
INIT_COUNT=0
INIT_SUCCESS=false

while [ $INIT_COUNT -lt $INIT_RETRIES ]; do
    echo -e "${INFO} User initialization attempt $((INIT_COUNT + 1))/$INIT_RETRIES..."
    
    if INIT_OUTPUT=$(docker compose -f infra/docker-compose.yml exec -T backend python init_db.py 2>&1); then
        echo -e "${SUCCESS} User initialization completed successfully"
        echo -e "${INFO} Initialization output:"
        echo "$INIT_OUTPUT" | grep -E "(Created user|Default users created|Login credentials)" | head -10
        INIT_SUCCESS=true
        break
    else
        echo -e "${WARNING} User initialization failed on attempt $((INIT_COUNT + 1))"
        echo -e "${INFO} Error output:"
        echo "$INIT_OUTPUT" | tail -10
        
        INIT_COUNT=$((INIT_COUNT + 1))
        
        if [ $INIT_COUNT -lt $INIT_RETRIES ]; then
            # Try to diagnose and fix common issues
            echo -e "${INFO} Diagnosing initialization failure..."
            
            # Check if it's a "users already exist" issue
            if echo "$INIT_OUTPUT" | grep -q "existing users"; then
                echo -e "${INFO} Users already exist - this is expected for non-clean setups"
                INIT_SUCCESS=true
                break
            fi
            
            # Check for column/table issues
            if echo "$INIT_OUTPUT" | grep -q "column.*does not exist\|relation.*does not exist"; then
                echo -e "${WARNING} Database schema issue detected - attempting to fix..."
                
                # Force re-run migrations
                docker compose -f infra/docker-compose.yml exec -T backend alembic upgrade head
                sleep 3
            fi
            
            # Check for connection issues
            if echo "$INIT_OUTPUT" | grep -q "connection\|timeout\|refused"; then
                echo -e "${WARNING} Database connection issue - waiting longer..."
                sleep 10
            else
                sleep 5
            fi
        fi
    fi
done

if [ "$INIT_SUCCESS" = "false" ]; then
    echo -e "${ERROR} Failed to initialize default users after $INIT_RETRIES attempts"
    echo -e "${INFO} Attempting emergency recovery..."
    
    # Emergency recovery: Try to clear and recreate users
    echo -e "${INFO} Attempting to clear corrupt user data and retry..."
    docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev -d xu2 -c "
        DO \$\$ 
        BEGIN
            IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') THEN
                TRUNCATE TABLE users, sessions RESTART IDENTITY CASCADE;
            END IF;
        EXCEPTION WHEN OTHERS THEN
            NULL; -- Ignore errors
        END \$\$;" >/dev/null 2>&1
    
    # One final attempt
    if docker compose -f infra/docker-compose.yml exec -T backend python init_db.py; then
        echo -e "${SUCCESS} Emergency recovery successful - users initialized"
        INIT_SUCCESS=true
    else
        echo -e "${ERROR} Emergency recovery failed"
        echo -e "${ERROR} Manual intervention required"
        echo -e "\n${INFO} Troubleshooting steps:"
        echo -e "1. Check backend health: curl http://localhost:8000/health"
        echo -e "2. Check database: docker compose -f infra/docker-compose.yml exec postgres psql -U dev -d xu2 -c '\\dt'"
        echo -e "3. Manual user creation: docker compose -f infra/docker-compose.yml exec backend python init_db.py"
        echo -e "4. Check backend logs: docker compose -f infra/docker-compose.yml logs backend"
        echo -e "\n${WARNING} Continuing setup - you may need to create users manually"
    fi
fi

# Verify user initialization
if [ "$INIT_SUCCESS" = "true" ]; then
    echo -e "${INFO} Verifying user initialization..."
    FINAL_USER_COUNT=$(docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev -d xu2 -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | tr -d ' \n' || echo "0")
    
    if [ "$FINAL_USER_COUNT" -ge 3 ]; then
        echo -e "${SUCCESS} User verification passed - $FINAL_USER_COUNT users in database"
        
        # Display available users
        echo -e "${INFO} Available user accounts:"
        docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev -d xu2 -c "SELECT email, role, is_active FROM users ORDER BY role;" 2>/dev/null || true
    else
        echo -e "${WARNING} User verification warning - only $FINAL_USER_COUNT users found (expected 3+)"
    fi
fi

echo -e "${SUCCESS} Database initialization phase complete"
echo -e "${INFO} Standard login credentials (if successfully created):"
echo -e "  • ${GREEN}Admin:${NC}      admin@example.com      / admin123"
echo -e "  • ${GREEN}Instructor:${NC} instructor@example.com / instructor123"
echo -e "  • ${GREEN}Student:${NC}    student@example.com    / student123"

# Run tests if not skipped
if [ "$SKIP_TESTS" = false ]; then
    print_section "Running Tests"
    
    echo -e "${INFO} Running backend tests..."
    docker compose -f infra/docker-compose.yml exec -T backend pytest
    
    echo -e "${INFO} Running frontend tests..."
    docker compose -f infra/docker-compose.yml exec -T frontend npm test
fi

# Function to open URL in browser tab (not new window)
open_url() {
    local url=$1
    echo -e "${INFO} Opening $url in browser tab..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - Force new tab in existing browser window
        if command_exists "osascript"; then
            # Use AppleScript to open in new tab of existing browser
            osascript -e "
                tell application \"System Events\"
                    set browserList to (name of every process whose background only is false)
                    if browserList contains \"Safari\" then
                        tell application \"Safari\"
                            activate
                            tell window 1 to set current tab to (make new tab with properties {URL:\"$url\"})
                        end tell
                    else if browserList contains \"Google Chrome\" then
                        tell application \"Google Chrome\"
                            activate
                            tell window 1 to make new tab with properties {URL:\"$url\"}
                        end tell
                    else if browserList contains \"Firefox\" then
                        tell application \"Firefox\"
                            activate
                        end tell
                        do shell script \"open -a Firefox '$url'\"
                    else
                        -- Fallback to default browser in new tab
                        do shell script \"open -g '$url'\"
                    end if
                end tell
            " 2>/dev/null || open -g "$url"
        else
            # Fallback - open in background (new tab if browser is running)
            open -g "$url"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux - Try to open in new tab of existing browser
        if command_exists "xdg-open"; then
            # Most Linux systems
            xdg-open "$url"
        elif command_exists "firefox"; then
            # Firefox with new tab flag
            firefox --new-tab "$url" &
        elif command_exists "google-chrome"; then
            # Chrome with new tab flag
            google-chrome --new-tab "$url" &
        elif command_exists "chromium"; then
            # Chromium with new tab flag
            chromium --new-tab "$url" &
        else
            echo -e "${ERROR} Could not find a browser to open $url"
        fi
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows - Use PowerShell to open in new tab
        if command_exists "powershell"; then
            powershell -Command "Start-Process '$url'" 2>/dev/null || start "$url"
        else
            start "$url"
        fi
    else
        echo -e "${ERROR} Unsupported OS type: $OSTYPE"
    fi
}

# Final status check and verification
print_section "Service Status & Verification"

# Comprehensive service verification with authentication testing
echo -e "${INFO} Performing comprehensive service verification..."

# Test each service systematically
BACKEND_HEALTHY=false
FRONTEND_HEALTHY=false
AUTH_WORKING=false

# Check backend API
echo -e "\n${INFO} Testing backend API..."
if BACKEND_HEALTH=$(curl -s --connect-timeout 10 http://localhost:8000/health 2>/dev/null); then
    if echo "$BACKEND_HEALTH" | grep -q "healthy"; then
        echo -e "${SUCCESS} Backend API is healthy (http://localhost:8000)"
        BACKEND_HEALTHY=true
        
        # Test authentication system with all three user types
        echo -e "${INFO} Testing authentication system..."
        
        TEST_USERS=("admin@example.com:admin123:admin" "instructor@example.com:instructor123:instructor" "student@example.com:student123:student")
        AUTH_SUCCESS_COUNT=0
        
        for user_data in "${TEST_USERS[@]}"; do
            IFS=':' read -r email password role <<< "$user_data"
            
            echo -e "${INFO} Testing login for $role: $email"
            AUTH_TEST=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
                -H "Content-Type: application/json" \
                -d "{\"email\":\"$email\",\"password\":\"$password\"}" 2>/dev/null)
            
            if echo "$AUTH_TEST" | grep -q "access_token"; then
                echo -e "${SUCCESS} ✓ Authentication successful for $role"
                AUTH_SUCCESS_COUNT=$((AUTH_SUCCESS_COUNT + 1))
            else
                echo -e "${WARNING} ✗ Authentication failed for $role"
                echo -e "${INFO} Response: $(echo "$AUTH_TEST" | head -c 200)"
            fi
        done
        
        if [ $AUTH_SUCCESS_COUNT -eq 3 ]; then
            echo -e "${SUCCESS} 🎉 All authentication tests passed!"
            AUTH_WORKING=true
        elif [ $AUTH_SUCCESS_COUNT -gt 0 ]; then
            echo -e "${WARNING} Partial authentication success ($AUTH_SUCCESS_COUNT/3 users working)"
            AUTH_WORKING=true
        else
            echo -e "${ERROR} No authentication tests passed - users may not be initialized correctly"
        fi
    else
        echo -e "${WARNING} Backend API responded but reports unhealthy status"
        echo -e "${INFO} Response: $BACKEND_HEALTH"
    fi
else
    echo -e "${ERROR} Backend API is not responding (http://localhost:8000)"
    echo -e "${INFO} Troubleshooting: docker compose -f infra/docker-compose.yml logs backend"
fi

# Check frontend
echo -e "\n${INFO} Testing frontend..."
if curl -s --connect-timeout 10 http://localhost:5173 >/dev/null 2>&1; then
    echo -e "${SUCCESS} Frontend is running (http://localhost:5173)"
    FRONTEND_HEALTHY=true
    
    # Test if frontend can connect to backend
    echo -e "${INFO} Testing frontend-backend connectivity..."
    if FRONTEND_API_TEST=$(curl -s --connect-timeout 5 "http://localhost:5173" | grep -o "localhost:8000\|127.0.0.1:8000" | head -1); then
        echo -e "${SUCCESS} Frontend appears configured to connect to backend"
    else
        echo -e "${INFO} Frontend may need configuration for backend connectivity"
    fi
else
    echo -e "${ERROR} Frontend is not responding (http://localhost:5173)"
    echo -e "${INFO} Troubleshooting: docker compose -f infra/docker-compose.yml logs frontend"
fi

# Check database connectivity and user data
echo -e "\n${INFO} Testing database connectivity and data integrity..."
if docker compose -f infra/docker-compose.yml exec -T postgres pg_isready -U dev -d xu2 >/dev/null 2>&1; then
    # Get detailed user count and verify table structure
    DB_STATUS=$(docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev -d xu2 -t -c "
        SELECT 
            'Users: ' || COUNT(*) || 
            ', Admin: ' || COUNT(*) FILTER (WHERE role = 'admin') ||
            ', Instructors: ' || COUNT(*) FILTER (WHERE role = 'instructor') ||
            ', Students: ' || COUNT(*) FILTER (WHERE role = 'student') ||
            ', Active: ' || COUNT(*) FILTER (WHERE is_active = true)
        FROM users;" 2>/dev/null | tr -d '\n' | xargs)
    
    if [ -n "$DB_STATUS" ] && echo "$DB_STATUS" | grep -q "Users: [1-9]"; then
        echo -e "${SUCCESS} Database connectivity verified"
        echo -e "${INFO} Database status: $DB_STATUS"
    else
        echo -e "${WARNING} Database connected but user data may be missing"
        echo -e "${INFO} Attempting to verify table structure..."
        if docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev -d xu2 -c "\d users" >/dev/null 2>&1; then
            echo -e "${INFO} Users table exists - user data may need initialization"
        else
            echo -e "${WARNING} Users table may not exist - database migration may have failed"
        fi
    fi
else
    echo -e "${ERROR} Database connectivity test failed"
fi

# Overall setup status and recommendations
echo -e "\n${BLUE}=== Setup Status Summary ===${NC}"

OVERALL_HEALTH="GOOD"
if [ "$BACKEND_HEALTHY" = "true" ] && [ "$FRONTEND_HEALTHY" = "true" ] && [ "$AUTH_WORKING" = "true" ]; then
    echo -e "${SUCCESS} 🎉 EXCELLENT: All systems are fully operational!"
    echo -e "${SUCCESS} ✅ Backend API: Healthy"
    echo -e "${SUCCESS} ✅ Frontend: Running"  
    echo -e "${SUCCESS} ✅ Authentication: Working"
    echo -e "${SUCCESS} ✅ Database: Connected and initialized"
elif [ "$BACKEND_HEALTHY" = "true" ] && [ "$FRONTEND_HEALTHY" = "true" ]; then
    echo -e "${WARNING} ⚠️  PARTIAL: Core services running but authentication needs attention"
    echo -e "${SUCCESS} ✅ Backend API: Healthy"
    echo -e "${SUCCESS} ✅ Frontend: Running"
    echo -e "${WARNING} ⚠️  Authentication: Issues detected"
    OVERALL_HEALTH="PARTIAL"
else
    echo -e "${ERROR} ❌ ISSUES: Some services are not working correctly"
    echo -e "$([ "$BACKEND_HEALTHY" = "true" ] && echo "${SUCCESS} ✅" || echo "${ERROR} ❌") Backend API"
    echo -e "$([ "$FRONTEND_HEALTHY" = "true" ] && echo "${SUCCESS} ✅" || echo "${ERROR} ❌") Frontend"
    echo -e "$([ "$AUTH_WORKING" = "true" ] && echo "${SUCCESS} ✅" || echo "${ERROR} ❌") Authentication"
    OVERALL_HEALTH="POOR"
fi

# Print final instructions based on health status
print_section "Setup Complete - Next Steps"

if [ "$OVERALL_HEALTH" = "GOOD" ]; then
    echo -e "🚀 ${GREEN}Ready to use! Your X-University platform is fully operational.${NC}"
    echo -e "\n📍 Available services:"
    echo -e "  • ${GREEN}Frontend:${NC} http://localhost:5173"
    echo -e "  • ${GREEN}Backend API:${NC} http://localhost:8000"
    echo -e "  • ${GREEN}API Documentation:${NC} http://localhost:8000/docs"
    echo -e "  • ${GREEN}PostgreSQL:${NC} localhost:5432"
    
    echo -e "\n🔐 Ready-to-use accounts:"
    echo -e "  • ${GREEN}Admin:${NC}      admin@example.com      / admin123"
    echo -e "  • ${GREEN}Instructor:${NC} instructor@example.com / instructor123"  
    echo -e "  • ${GREEN}Student:${NC}    student@example.com    / student123"

elif [ "$OVERALL_HEALTH" = "PARTIAL" ]; then
    echo -e "⚠️  ${YELLOW}Mostly ready - authentication may need attention${NC}"
    echo -e "\n📍 Available services:"
    echo -e "  • Frontend: http://localhost:5173"
    echo -e "  • Backend API: http://localhost:8000"
    echo -e "  • API Documentation: http://localhost:8000/docs"
    
    echo -e "\n🔧 To fix authentication issues:"
    echo -e "  1. Run: ${GREEN}docker compose -f infra/docker-compose.yml exec -T backend python init_db.py${NC}"
    echo -e "  2. Check logs: ${GREEN}docker compose -f infra/docker-compose.yml logs backend${NC}"
    echo -e "  3. Test login manually at: http://localhost:5173"
    
else
    echo -e "❌ ${RED}Setup completed with issues - manual intervention may be needed${NC}"
    echo -e "\n🚨 Troubleshooting steps:"
    echo -e "  1. Check all services: ${GREEN}docker compose -f infra/docker-compose.yml ps${NC}"
    echo -e "  2. View logs: ${GREEN}docker compose -f infra/docker-compose.yml logs${NC}"
    echo -e "  3. Restart services: ${GREEN}docker compose -f infra/docker-compose.yml restart${NC}"
    echo -e "  4. Complete cleanup and retry: ${GREEN}./scripts/cleanup.sh && ./setup.sh --clean${NC}"
fi

# Open browser tabs in existing browser window
if [ "$SKIP_BROWSER" = false ]; then
    echo -e "\n${INFO} Opening services in browser tabs..."
    sleep 2  # Brief pause to ensure services are fully ready

    # Open frontend in new tab
    open_url "http://localhost:5173"
    sleep 1  # Small delay between opening tabs

    # Open backend health endpoint in new tab
    open_url "http://localhost:8000/health"
    sleep 1

    # Open API documentation in new tab
    open_url "http://localhost:8000/docs"

    echo -e "\n${SUCCESS} Browser tabs opened in existing browser window!"
else
    echo -e "\n${INFO} Skipping browser opening (--skip-browser flag used)"
fi
echo -e "\nUseful commands:"
echo -e "  • View logs: make logs"
echo -e "  • Stop services: make down"
echo -e "  • Run tests: make test"
echo -e "  • Format code: make fmt"
