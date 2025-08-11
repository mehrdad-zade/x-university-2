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
# Usage: ./setup.sh [--clean] [--skip-tests]
# Options:
#   --clean: Remove existing environments and start fresh
#            • Removes Python virtual environment
#            • Cleans Node.js dependencies
#            • Removes Docker volumes
#   --skip-tests: Skip running tests during setup
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
    rm -rf "$VENV_DIR"
    rm -rf "$FRONTEND_DIR/node_modules"
    docker compose -f infra/docker-compose.yml down -v
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
echo -e "${INFO} Building and starting containers..."

# Try to pull images first
echo -e "${INFO} Pulling required Docker images..."
export COMPOSE_PROJECT_NAME=x-university-infra
if ! docker compose -f infra/docker-compose.yml pull --quiet; then
    echo -e "${WARNING} Failed to pull some images, will attempt to build from cache"
fi

# Attempt to start services with retries
MAX_RETRIES=3
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if docker compose -f infra/docker-compose.yml --env-file infra/.env up -d --build; then
        echo -e "${SUCCESS} Docker services started successfully"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
            echo -e "${ERROR} Failed to start Docker services after $MAX_RETRIES attempts"
            echo "Try running: docker system prune -a"
            echo "Then run this script again"
            exit 1
        else
            echo -e "${WARNING} Failed to start services, retrying ($RETRY_COUNT/$MAX_RETRIES)..."
            docker compose -f infra/docker-compose.yml down
            sleep 5
        fi
    fi
done

# Wait for services to be ready with health check
echo -e "${INFO} Waiting for services to be ready..."
TIMEOUT=120  # Increased timeout to 120 seconds
HEALTH_CHECK_INTERVAL=5  # Check every 5 seconds instead of every second
while [ $TIMEOUT -gt 0 ]; do
    SERVICES_STATUS=$(docker compose -f infra/docker-compose.yml ps --format json)
    if echo "$SERVICES_STATUS" | grep -q "\"State\":\"running\""; then
        if ! echo "$SERVICES_STATUS" | grep -q "\"State\":\"starting\"\|\"Health\":\"unhealthy\""; then
            echo -e "\n${SUCCESS} All services are ready"
            break
        fi
    fi
    if echo "$SERVICES_STATUS" | grep -q "\"State\":\"exited\"\|\"Health\":\"unhealthy\""; then
        echo -e "${ERROR} Some services failed to start properly"
        echo "Check the logs with: docker compose -f infra/docker-compose.yml logs"
        exit 1
    fi
    echo -n "."
    sleep $HEALTH_CHECK_INTERVAL
    TIMEOUT=$((TIMEOUT - HEALTH_CHECK_INTERVAL))
done

if [ $TIMEOUT -eq 0 ]; then
    echo -e "${ERROR} Services took too long to start"
    echo "Check the logs with: docker compose -f infra/docker-compose.yml logs"
    exit 1
fi

# Run database migrations
print_section "Running Database Migrations"
echo -e "${INFO} Applying database migrations..."
docker compose -f infra/docker-compose.yml exec -T backend alembic upgrade head
if [ $? -ne 0 ]; then
    echo -e "${ERROR} Failed to run database migrations"
    exit 1
fi
echo -e "${SUCCESS} Database migrations complete"

# Run tests if not skipped
if [ "$SKIP_TESTS" = false ]; then
    print_section "Running Tests"
    
    echo -e "${INFO} Running backend tests..."
    docker compose -f infra/docker-compose.yml exec -T backend pytest
    
    echo -e "${INFO} Running frontend tests..."
    docker compose -f infra/docker-compose.yml exec -T frontend npm test
fi

# Final status check
print_section "Service Status"
BACKEND_HEALTH=$(curl -s http://localhost:8000/health)
if [[ $BACKEND_HEALTH == *"healthy"* ]]; then
    echo -e "${SUCCESS} Backend API is running (http://localhost:8000)"
else
    echo -e "${ERROR} Backend API is not responding"
fi

# Check frontend
if curl -s http://localhost:5173 > /dev/null; then
    echo -e "${SUCCESS} Frontend is running (http://localhost:5173)"
else
    echo -e "${ERROR} Frontend is not responding"
fi

# Print final instructions
print_section "Setup Complete"
echo -e "Available services:"
echo -e "  • Frontend: http://localhost:5173"
echo -e "  • Backend API: http://localhost:8000"
echo -e "  • API Documentation: http://localhost:8000/docs"
echo -e "  • PostgreSQL: localhost:5432"
echo -e "  • Neo4j Browser: http://localhost:7474 (if enabled)"
echo -e "\nUseful commands:"
echo -e "  • View logs: make logs"
echo -e "  • Stop services: make down"
echo -e "  • Run tests: make test"
echo -e "  • Format code: make fmt"
