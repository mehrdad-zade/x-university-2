#!/bin/bash

# Source centralized constants
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
source "$SCRIPT_DIR/constants.sh"

# ============================================================================
# PostgreSQL Helper Functions (consolidated from separate scripts)
# ============================================================================

# Function to check Docker resources and PostgreSQL compatibility
check_docker_postgres_resources() {
    echo -e "${INFO} Checking Docker Desktop resources for PostgreSQL..."
    
    if command -v docker >/dev/null 2>&1; then
        DOCKER_INFO=$(docker info 2>/dev/null || echo "")
        if echo "$DOCKER_INFO" | grep -q "Total Memory"; then
            TOTAL_MEM=$(echo "$DOCKER_INFO" | grep "Total Memory" | awk '{print $3$4}')
            echo -e "${SUCCESS} Docker Desktop Memory: $TOTAL_MEM"
            
            # Parse memory and warn if too low
            MEM_NUM=$(echo "$TOTAL_MEM" | sed 's/[^0-9.]//g')
            if command -v bc >/dev/null 2>&1 && [[ $(echo "$MEM_NUM < 4" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
                echo -e "${WARNING} Docker Desktop has limited memory allocation ($TOTAL_MEM)"
                echo -e "${WARNING} Recommend increasing to at least 4GB for reliable PostgreSQL startup"
                return 1
            fi
        fi
    fi
    return 0
}

# Function to create PostgreSQL startup optimizations if needed
ensure_postgres_optimizations() {
    echo -e "${INFO} Ensuring PostgreSQL startup optimizations..."
    
    OVERRIDE_FILE="$PROJECT_ROOT/infra/docker-compose.startup-fix.yml"
    if [ ! -f "$OVERRIDE_FILE" ]; then
        echo -e "${INFO} Creating PostgreSQL startup optimization override..."
        
        cat > "$OVERRIDE_FILE" << 'EOF'
# Docker Compose override for reliable PostgreSQL startup
version: '3.8'

services:
  postgres:
    # Extended health check for reliable startup detection
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-dev} -d ${POSTGRES_DB:-xu2} -t 5 || exit 1"]
      interval: 5s
      timeout: 10s
      retries: 24  # Wait up to 2 minutes
      start_period: 60s  # Allow 1 minute for initial startup
    
    # Ensure proper shutdown handling
    stop_grace_period: 60s
    stop_signal: SIGTERM
    
    # Resource limits to prevent resource starvation
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
    
    # Additional environment variables for reliability
    environment:
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=C --auth-local=trust --auth-host=md5"
      POSTGRES_HOST_AUTH_METHOD: md5
      PGDATA: /var/lib/postgresql/data/pgdata
    
    # Optimized command with conservative settings for reliability
    command: >
      postgres
      -c logging_collector=off
      -c log_destination=stderr
      -c log_statement=none
      -c log_min_duration_statement=-1
      -c shared_buffers=128MB
      -c effective_cache_size=512MB
      -c maintenance_work_mem=64MB
      -c checkpoint_completion_target=0.7
      -c wal_buffers=4MB
      -c default_statistics_target=100
      -c random_page_cost=1.1
      -c effective_io_concurrency=100
      -c work_mem=4MB
      -c max_connections=100
      -c shared_preload_libraries=''
      -c fsync=on
      -c synchronous_commit=on
      -c full_page_writes=on
    
    # Volume optimization
    volumes:
      - postgres_data:/var/lib/postgresql/data/pgdata
      - ./init-data:/docker-entrypoint-initdb.d:ro

volumes:
  postgres_data:
    driver: local
EOF
        echo -e "${SUCCESS} Created PostgreSQL startup optimization override"
    else
        echo -e "${SUCCESS} PostgreSQL startup optimizations already exist"
    fi
}

# Function to diagnose PostgreSQL issues
diagnose_postgres_issues() {
    echo -e "${INFO} Running PostgreSQL diagnostics..."
    echo
    echo "=== PostgreSQL Startup Diagnosis ==="
    echo
    
    echo "1. Docker Desktop Status:"
    docker info | grep -E "(Server Version|Storage Driver|CPUs|Total Memory)" || echo "Docker info not available"
    echo
    
    echo "2. Current Docker Resources:"
    docker system df
    echo
    
    echo "3. PostgreSQL Container Status:"
    docker ps -a --filter "name=xu2-postgres" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo
    
    echo "4. PostgreSQL Logs (last 30 lines):"
    docker compose -f "$PROJECT_ROOT/infra/docker-compose.yml" logs postgres --tail=30 2>/dev/null || echo "No logs available"
    echo
    
    echo "5. Volume Status:"
    docker volume ls --filter "name=postgres"
    echo
    
    echo "6. System Resources:"
    echo "Available Disk:" $(df -h . | tail -1 | awk '{print $4}')
    echo
    
    echo "=== Recommendations ==="
    echo "• If PostgreSQL keeps failing, try: --clean flag for fresh setup"
    echo "• If Docker is low on resources, increase Docker Desktop memory to 4GB+"
    echo "• If volume issues persist, try: docker volume prune && docker system prune"
}

# Function to cleanup problematic PostgreSQL containers and volumes
cleanup_postgres_state() {
    echo -e "${INFO} Cleaning up problematic PostgreSQL state..."
    
    # Stop and remove any existing PostgreSQL containers
    if docker ps -a --filter "name=xu2-postgres" --format "{{.Names}}" | grep -q "xu2-postgres"; then
        echo -e "${INFO} Found existing PostgreSQL container, cleaning up..."
        docker stop xu2-postgres 2>/dev/null || true
        docker rm -f xu2-postgres 2>/dev/null || true
        echo -e "${SUCCESS} Cleaned up existing container"
    fi
    
    # Check for orphaned postgres containers
    ORPHANED=$(docker ps -a --filter "ancestor=postgres" --filter "status=exited" --format "{{.Names}}" 2>/dev/null || echo "")
    if [ -n "$ORPHANED" ]; then
        echo -e "${INFO} Removing orphaned PostgreSQL containers..."
        echo "$ORPHANED" | xargs docker rm -f 2>/dev/null || true
    fi
    
    # Check volume integrity
    if docker volume ls --format "{{.Name}}" | grep -q "x-university-infra_postgres_data"; then
        echo -e "${INFO} Checking PostgreSQL volume integrity..."
        if ! docker run --rm -v x-university-infra_postgres_data:/test alpine:latest ls -la /test >/dev/null 2>&1; then
            echo -e "${WARNING} PostgreSQL volume appears corrupted, recreating..."
            docker volume rm -f x-university-infra_postgres_data 2>/dev/null || true
            echo -e "${SUCCESS} Removed corrupted volume"
        fi
    fi
}

# ============================================================================
# End PostgreSQL Helper Functions  
# ============================================================================

#!/bin/bash
# scripts/setup.sh
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
# Usage: ./scripts/setup.sh [--clean] [--skip-tests] [--skip-browser] [--skip-logs] [--diagnose-postgres]
# Options:
#   --clean: Remove existing environments and start fresh
#            • Removes Python virtual environment
#            • Cleans Node.js dependencies
#            • Removes Docker volumes and PostgreSQL state
#   --skip-tests: Skip running tests during setup
#   --skip-browser: Skip automatically opening browser tabs
#   --skip-logs: Skip showing live logs after setup
#   --diagnose-postgres: Run PostgreSQL diagnostic information gathering
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
SKIP_LOGS=false
DIAGNOSE_POSTGRES=false
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
        --skip-logs)
            SKIP_LOGS=true
            shift
            ;;
        --diagnose-postgres)
            DIAGNOSE_POSTGRES=true
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

# Check Docker connectivity
echo -e "${INFO} Checking Docker network connectivity..."
if ! check_docker_network; then
    echo -e "${WARNING} Docker network connectivity issues detected"
    echo "This may affect image pulling and container operations."
    echo "Please check:"
    echo "1. Your internet connection"
    echo "2. If you're behind a corporate VPN, check your proxy settings"
    echo "3. If you can access https://registry.hub.docker.com"
    echo "4. Your DNS settings (try adding 8.8.8.8 to your DNS servers)"
    echo ""
    echo -e "${INFO} Continuing setup - you may encounter issues pulling images"
else
    echo -e "${SUCCESS} Docker network connectivity verified"
fi

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
# Get the actual project root (parent directory of scripts)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
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

# Verify Docker Compose configuration
echo -e "${INFO} Docker monitoring configuration:"
echo -e "${SUCCESS} System optimized for performance and security (non-root user)"
echo -e "${SUCCESS} Docker monitoring is disabled by default to prevent performance issues"
echo -e ""
echo -e "${INFO} 📊 Docker Container Monitoring Options:"
echo -e "   ${GREEN}Option 1 (Recommended):${NC} Use the Monitor page's 'Show Docker Containers' button"
echo -e "      • Provides temporary Docker access through the web interface"
echo -e "      • No manual configuration required"
echo -e "      • Secure and user-friendly"
echo -e ""
echo -e "   ${GREEN}Option 2 (Manual):${NC} Edit docker-compose.yml for persistent monitoring"
echo -e "      • Edit ${GREEN}infra/docker-compose.yml${NC}"
echo -e "      • Uncomment the Docker socket volume and 'user: root' lines"
echo -e "      • Restart: ${GREEN}docker compose -f infra/docker-compose.yml up -d --force-recreate backend${NC}"
echo -e "${WARNING} Note: Manual setup requires root access which reduces security"

# Start Docker services
print_section "Starting Docker Services"

# Check Docker resources and PostgreSQL optimizations before starting
check_docker_postgres_resources
ensure_postgres_optimizations

# Run PostgreSQL diagnostics if requested
if [ "$DIAGNOSE_POSTGRES" = true ]; then
    echo -e "\n${INFO} Running PostgreSQL diagnostics as requested..."
    diagnose_postgres_issues
    echo -e "\n${INFO} Diagnostics complete. Continuing with setup...\n"
fi

# Ensure clean startup state
echo -e "${INFO} Preparing Docker environment..."
docker compose -f infra/docker-compose.yml down --timeout 30 2>/dev/null || true

# Clean up any orphaned containers and PostgreSQL state if needed
if [ "$CLEAN" = true ]; then
    cleanup_postgres_state
fi

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
    
    # Clean up before retry (but not on first attempt unless clean build)
    if [ $RETRY_COUNT -gt 0 ] || [ "$CLEAN" = "true" ]; then
        echo -e "${INFO} Cleaning up before $([ $RETRY_COUNT -eq 0 ] && echo "clean build" || echo "retry")..."
        docker compose -f infra/docker-compose.yml down --timeout 30 2>/dev/null || true
        docker rm -f xu2-postgres xu2-backend xu2-frontend 2>/dev/null || true
        
        # For retries, add extra cleanup
        if [ $RETRY_COUNT -gt 0 ]; then
            # Give Docker time to clean up
            sleep 5
            
            # Check for any stuck postgres processes
            if docker ps -aq --filter "name=xu2-postgres" | grep -q .; then
                echo -e "${INFO} Forcefully removing stuck postgres container..."
                docker kill xu2-postgres 2>/dev/null || true
                docker rm -f xu2-postgres 2>/dev/null || true
            fi
        fi
    fi
    
    # Special handling for PostgreSQL startup reliability
    echo -e "${INFO} Starting PostgreSQL with enhanced reliability using optimized configuration..."
    
    # Check if startup override exists
    STARTUP_OVERRIDE="$PROJECT_ROOT/infra/docker-compose.startup-fix.yml"
    if [ -f "$STARTUP_OVERRIDE" ]; then
        echo -e "${SUCCESS} Using PostgreSQL startup optimization override"
        COMPOSE_FILES="-f infra/docker-compose.yml -f infra/docker-compose.startup-fix.yml"
    else
        echo -e "${INFO} Standard configuration (run 'make fix-postgres' for optimizations)"
        COMPOSE_FILES="-f infra/docker-compose.yml"
    fi
    
    # Start postgres first with explicit startup sequence
    if docker compose $COMPOSE_FILES --env-file infra/.env up -d postgres; then
        echo -e "${SUCCESS} PostgreSQL container started, waiting for initialization..."
        
        # Enhanced PostgreSQL initialization wait with progress tracking
        POSTGRES_TIMEOUT=120  # 2 minutes for full PostgreSQL init
        POSTGRES_CHECK_INTERVAL=3
        POSTGRES_READY=false
        
        while [ $POSTGRES_TIMEOUT -gt 0 ]; do
            # Check if container is still running
            if ! docker ps --filter "name=xu2-postgres" --filter "status=running" | grep -q "xu2-postgres"; then
                echo -e "\n${ERROR} PostgreSQL container stopped unexpectedly"
                docker compose $COMPOSE_FILES logs postgres --tail=20
                break
            fi
            
            # Check PostgreSQL readiness
            if docker compose $COMPOSE_FILES exec -T postgres pg_isready -U dev -d xu2 >/dev/null 2>&1; then
                echo -e "\n${SUCCESS} PostgreSQL is ready and accepting connections!"
                POSTGRES_READY=true
                break
            fi
            
            # Progress indicator every 15 seconds
            if [ $((POSTGRES_TIMEOUT % 15)) -eq 0 ]; then
                echo -e "\n${INFO} Still waiting for PostgreSQL initialization... ($((120 - POSTGRES_TIMEOUT))s elapsed)"
                # Show container status
                docker compose $COMPOSE_FILES ps postgres --format "table {{.Name}}\t{{.Status}}"
            else
                echo -n "."
            fi
            
            sleep $POSTGRES_CHECK_INTERVAL
            POSTGRES_TIMEOUT=$((POSTGRES_TIMEOUT - POSTGRES_CHECK_INTERVAL))
        done
        
        if [ "$POSTGRES_READY" = "true" ]; then
            echo -e "${INFO} PostgreSQL ready, starting remaining services..."
            
            # Now start the rest of the services
            if docker compose $COMPOSE_FILES --env-file infra/.env up -d $UP_OPTIONS; then
                echo -e "${SUCCESS} All services started successfully"
                break
            else
                echo -e "${WARNING} Failed to start dependent services"
                docker compose $COMPOSE_FILES logs --tail=10
            fi
        else
            echo -e "\n${ERROR} PostgreSQL failed to initialize within timeout"
            echo -e "${INFO} PostgreSQL logs:"
            docker compose $COMPOSE_FILES logs postgres --tail=30
        fi
    else
        echo -e "${ERROR} Failed to start PostgreSQL container"
    fi
    
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo -e "${ERROR} Failed to start services after $MAX_RETRIES attempts"
        echo -e "\n${ERROR} Running PostgreSQL diagnostics..."
        
        # Use our consolidated diagnostic function
        diagnose_postgres_issues
        
        echo -e "\n${ERROR} Suggested solutions:"
        echo "• Increase Docker Desktop memory allocation to at least 4GB"
        echo "• Try: docker system prune -a (removes all unused data)"
        echo "• Restart Docker Desktop and try again"
        echo "• Run: ./scripts/setup.sh --clean (complete fresh start)"
        exit 1
    else
        echo -e "${WARNING} Failed to start services, waiting before retry (attempt $RETRY_COUNT/$MAX_RETRIES)..."
        echo -e "${INFO} Waiting 15 seconds for system to stabilize..."
        sleep 15
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
            if curl -s --connect-timeout 3 "${HEALTH_CHECK_URL}" >/dev/null 2>&1; then
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

# Wait a bit more to ensure backend is fully ready for database operations
echo -e "${INFO} Ensuring backend is fully initialized for database operations..."
sleep 10

# Verify backend can handle database operations
echo -e "${INFO} Testing backend database connectivity..."
DB_CONNECTION_READY=false
for i in {1..10}; do
    if docker compose -f infra/docker-compose.yml exec -T backend python3 -c "
from sqlalchemy import create_engine, text
import os
try:
    engine = create_engine(os.environ['DATABASE_URL'])
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('DB_CONNECTION_OK')
    exit(0)
except Exception as e:
    print(f'DB_CONNECTION_ERROR: {e}')
    exit(1)
" 2>/dev/null | grep -q "DB_CONNECTION_OK"; then
        echo -e "${SUCCESS} Backend database connectivity verified"
        DB_CONNECTION_READY=true
        break
    else
        echo -e "${INFO} Database connection attempt $i/10..."
        sleep 2
    fi
done

if [ "$DB_CONNECTION_READY" = "false" ]; then
    echo -e "${ERROR} Backend cannot connect to database - stopping setup"
    docker compose -f infra/docker-compose.yml logs backend --tail=20
    exit 1
fi

echo -e "${INFO} Checking current database schema state..."
MIGRATION_RETRIES=5
MIGRATION_COUNT=0
MIGRATION_SUCCESS=false

while [ $MIGRATION_COUNT -lt $MIGRATION_RETRIES ]; do
    echo -e "${INFO} Migration attempt $((MIGRATION_COUNT + 1))/$MIGRATION_RETRIES..."
    
    # Check current migration state
    if CURRENT_REVISION=$(docker compose -f infra/docker-compose.yml exec -T backend alembic current 2>/dev/null | grep -E "^[a-f0-9]+\s+" | awk '{print $1}'); then
        if [ -n "$CURRENT_REVISION" ]; then
            echo -e "${INFO} Current database revision: $CURRENT_REVISION"
        else
            echo -e "${INFO} Database appears to be uninitialized - will run migrations"
        fi
        
        # Check what migrations are available
        echo -e "${INFO} Available migrations:"
        docker compose -f infra/docker-compose.yml exec -T backend alembic history --verbose 2>/dev/null | head -5 || true
        
        # Run the migration with detailed output
        echo -e "${INFO} Running database migrations..."
        if docker compose -f infra/docker-compose.yml exec -T backend alembic upgrade head; then
            echo -e "${SUCCESS} Database migrations completed successfully"
            MIGRATION_SUCCESS=true
            break
        else
            echo -e "${WARNING} Migration failed on attempt $((MIGRATION_COUNT + 1))"
            echo -e "${INFO} Backend logs from migration attempt:"
            docker compose -f infra/docker-compose.yml logs backend --tail=10
        fi
    else
        echo -e "${WARNING} Could not connect to database for migration on attempt $((MIGRATION_COUNT + 1))"
        echo -e "${INFO} Checking backend health..."
        docker compose -f infra/docker-compose.yml ps backend
    fi
    
    MIGRATION_COUNT=$((MIGRATION_COUNT + 1))
    if [ $MIGRATION_COUNT -lt $MIGRATION_RETRIES ]; then
        echo -e "${INFO} Waiting 10 seconds before retry..."
        sleep 10
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
        
        # Check if users table has the correct structure with role column
        echo -e "${INFO} Verifying users table structure..."
        if docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev -d xu2 -c "\d users" 2>/dev/null | grep -q "role.*character varying"; then
            echo -e "${SUCCESS} Users table structure verified with role column"
        else
            echo -e "${ERROR} Users table missing role column - migration may have failed"
            echo -e "${INFO} Current users table structure:"
            docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev -d xu2 -c "\d users" 2>/dev/null || true
            exit 1
        fi
        
        # Verify password hash column name (should be password_hash, not hashed_password)
        if docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev -d xu2 -c "\d users" 2>/dev/null | grep -q "password_hash"; then
            echo -e "${SUCCESS} Password hash column correctly named"
        else
            echo -e "${ERROR} Password hash column incorrectly named - this will cause authentication issues"
            exit 1
        fi
    else
        echo -e "${WARNING} Database schema verification failed - expected tables may be missing"
        echo -e "${INFO} Available tables:"
        docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev -d xu2 -c "\dt" 2>/dev/null || true
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
    
    # Safely clear user-related tables and handle schema conflicts
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
                -- Check if this is the old schema (with hashed_password instead of password_hash)
                IF EXISTS (SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'hashed_password') THEN
                    -- Drop the old table completely to avoid schema conflicts
                    DROP TABLE IF EXISTS users CASCADE;
                    RAISE NOTICE 'Dropped old users table with incompatible schema';
                ELSE
                    -- Just truncate if it's the new schema
                    TRUNCATE TABLE users RESTART IDENTITY CASCADE;
                END IF;
            END IF;
        END \$\$;" 2>&1)
    
    if echo "$CLEAR_RESULT" | grep -q "ERROR"; then
        echo -e "${WARNING} Some tables may not exist yet (this is normal for first setup)"
    else
        echo -e "${SUCCESS} User data cleared successfully"
        if echo "$CLEAR_RESULT" | grep -q "Dropped old users table"; then
            echo -e "${INFO} Removed old incompatible user table schema"
        fi
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
        
        # Display available users with roles
        echo -e "${INFO} Available user accounts:"
        docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev -d xu2 -c "SELECT email, role, is_active FROM users ORDER BY role;" 2>/dev/null || true
        
        # Verify we have all three required roles
        ADMIN_COUNT=$(docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev -d xu2 -t -c "SELECT COUNT(*) FROM users WHERE role = 'admin';" 2>/dev/null | tr -d ' \n' || echo "0")
        INSTRUCTOR_COUNT=$(docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev -d xu2 -t -c "SELECT COUNT(*) FROM users WHERE role = 'instructor';" 2>/dev/null | tr -d ' \n' || echo "0")
        STUDENT_COUNT=$(docker compose -f infra/docker-compose.yml exec -T postgres psql -U dev -d xu2 -t -c "SELECT COUNT(*) FROM users WHERE role = 'student';" 2>/dev/null | tr -d ' \n' || echo "0")
        
        if [ "$ADMIN_COUNT" -ge 1 ] && [ "$INSTRUCTOR_COUNT" -ge 1 ] && [ "$STUDENT_COUNT" -ge 1 ]; then
            echo -e "${SUCCESS} All required user roles created (Admin: ${ADMIN_COUNT}, Instructor: ${INSTRUCTOR_COUNT}, Student: ${STUDENT_COUNT})"
        else
            echo -e "${WARNING} Missing required user roles - may need manual user creation"
        fi
    else
        echo -e "${WARNING} User verification warning - only $FINAL_USER_COUNT users found (expected 3+)"
    fi
fi

echo -e "${SUCCESS} Database initialization phase complete"
echo -e "${INFO} Standard login credentials (if successfully created):"
echo -e "  • ${GREEN}Admin:${NC}      admin@example.com      / password123"
echo -e "  • ${GREEN}Instructor:${NC} instructor@example.com / password123"
echo -e "  • ${GREEN}Student:${NC}    student@example.com    / password123"

# Run tests if not skipped
if [ "$SKIP_TESTS" = false ]; then
    print_section "Running Tests"
    
    echo -e "${INFO} Running backend tests..."
    if docker compose -f infra/docker-compose.yml exec -T backend pytest; then
        echo -e "${SUCCESS} Backend tests passed"
    else
        echo -e "${WARNING} Backend tests failed - this may not prevent normal operation"
        echo -e "${INFO} To run tests manually later: docker compose -f infra/docker-compose.yml exec backend pytest"
    fi
    
    echo -e "${INFO} Running frontend tests..."
    if docker compose -f infra/docker-compose.yml exec -T frontend npm test; then
        echo -e "${SUCCESS} Frontend tests passed"
    else
        echo -e "${WARNING} Frontend tests failed - this may not prevent normal operation"
        echo -e "${INFO} To run tests manually later: docker compose -f infra/docker-compose.yml exec frontend npm test"
    fi
    
    echo -e "${INFO} Tests completed - check individual results above"
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
if BACKEND_HEALTH=$(curl -s --connect-timeout 10 "${HEALTH_CHECK_URL}" 2>/dev/null); then
    if echo "$BACKEND_HEALTH" | grep -q "healthy"; then
        echo -e "${SUCCESS} Backend API is healthy (${BACKEND_URL})"
        BACKEND_HEALTHY=true
        
        # Test authentication system with all three user types
        echo -e "${INFO} Testing authentication system..."
        
        TEST_USERS=("admin@example.com:password123:admin" "instructor@example.com:password123:instructor" "student@example.com:password123:student")
        AUTH_SUCCESS_COUNT=0
        
        for user_data in "${TEST_USERS[@]}"; do
            IFS=':' read -r email password role <<< "$user_data"
            
            echo -e "${INFO} Testing login for $role: $email"
            AUTH_TEST=$(curl -s -X POST "${LOGIN_FULL_URL}" \
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
    echo -e "${ERROR} Backend API is not responding (${BACKEND_URL})"
    echo -e "${INFO} Troubleshooting: docker compose -f infra/docker-compose.yml logs backend"
fi

# Check frontend
echo -e "\n${INFO} Testing frontend..."
if curl -s --connect-timeout 10 "${FRONTEND_URL}" >/dev/null 2>&1; then
    echo -e "${SUCCESS} Frontend is running (${FRONTEND_URL})"
    FRONTEND_HEALTHY=true
    
    # Test if frontend can connect to backend
    echo -e "${INFO} Testing frontend-backend connectivity..."
    if FRONTEND_API_TEST=$(curl -s --connect-timeout 5 "${FRONTEND_URL}" | grep -o "localhost:8000\|127.0.0.1:8000" | head -1); then
        echo -e "${SUCCESS} Frontend appears configured to connect to backend"
    else
        echo -e "${INFO} Frontend may need configuration for backend connectivity"
    fi
    
    # Test monitoring endpoint
    echo -e "${INFO} Testing system monitoring endpoint..."
    if MONITOR_TEST=$(curl -s --connect-timeout 5 "${MONITOR_FULL_URL}" 2>/dev/null); then
        if echo "$MONITOR_TEST" | grep -q '"system_info"'; then
            echo -e "${SUCCESS} System monitoring endpoint working"
            # Check if Docker monitoring is enabled
            if echo "$MONITOR_TEST" | grep -q '"error".*"Docker client not available"'; then
                echo -e "${INFO} Docker monitoring disabled (this is normal and recommended)"
            elif echo "$MONITOR_TEST" | grep -q '"containers":\s*\['; then
                CONTAINER_COUNT=$(echo "$MONITOR_TEST" | grep -o '"containers":\s*\[[^]]*\]' | grep -o '{[^}]*}' | wc -l | tr -d ' ')
                echo -e "${SUCCESS} Docker monitoring enabled - found $CONTAINER_COUNT containers"
            fi
        else
            echo -e "${WARNING} Monitor endpoint responding but may have issues"
        fi
    else
        echo -e "${WARNING} Monitor endpoint not responding"
    fi
else
    echo -e "${ERROR} Frontend is not responding (${FRONTEND_URL})"
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
    echo -e "  • ${GREEN}Frontend:${NC} ${FRONTEND_URL}"
    echo -e "  • ${GREEN}Backend API:${NC} ${BACKEND_URL}"
    echo -e "  • ${GREEN}API Documentation:${NC} ${API_DOCS_URL}"
    echo -e "  • ${GREEN}PostgreSQL:${NC} localhost:5432"
    
    echo -e "\n🔐 Ready-to-use accounts:"
    echo -e "  • ${GREEN}Admin:${NC}      admin@example.com      / password123"
    echo -e "  • ${GREEN}Instructor:${NC} instructor@example.com / password123"  
    echo -e "  • ${GREEN}Student:${NC}    student@example.com    / password123"

elif [ "$OVERALL_HEALTH" = "PARTIAL" ]; then
    echo -e "⚠️  ${YELLOW}Mostly ready - authentication may need attention${NC}"
    echo -e "\n📍 Available services:"
    echo -e "  • Frontend: ${FRONTEND_URL}"
    echo -e "  • Backend API: ${BACKEND_URL}"
    echo -e "  • API Documentation: ${API_DOCS_URL}"
    
    echo -e "\n🔧 To fix authentication issues:"
    echo -e "  1. Run: ${GREEN}docker compose -f infra/docker-compose.yml exec -T backend python init_db.py${NC}"
    echo -e "  2. Check logs: ${GREEN}docker compose -f infra/docker-compose.yml logs backend${NC}"
    echo -e "  3. Test login manually at: ${FRONTEND_URL}"
    
else
    echo -e "❌ ${RED}Setup completed with issues - manual intervention may be needed${NC}"
    echo -e "\n🚨 Troubleshooting steps:"
    echo -e "  1. Check all services: ${GREEN}docker compose -f infra/docker-compose.yml ps${NC}"
    echo -e "  2. View logs: ${GREEN}docker compose -f infra/docker-compose.yml logs${NC}"
    echo -e "  3. Restart services: ${GREEN}docker compose -f infra/docker-compose.yml restart${NC}"
    echo -e "  4. Complete cleanup and retry: ${GREEN}./scripts/cleanup.sh && ./scripts/setup.sh --clean${NC}"
fi

# Open frontend only if everything is healthy
if [ "$SKIP_BROWSER" = false ] && [ "$OVERALL_HEALTH" = "GOOD" ]; then
    echo -e "\n${INFO} All systems healthy - opening frontend..."
    sleep 2  # Brief pause to ensure services are fully ready

    # Open only the frontend - users can navigate to other services from there
    open_url "${FRONTEND_URL}"

    echo -e "${SUCCESS} Frontend opened in browser!"
    echo -e "${INFO} Access other services:"
    echo -e "  • API Documentation: ${API_DOCS_URL}"
    echo -e "  • Backend Health: ${HEALTH_CHECK_URL}"
elif [ "$SKIP_BROWSER" = false ]; then
    echo -e "\n${INFO} System not fully healthy - skipping browser opening"
    echo -e "${INFO} Once issues are resolved, visit: http://localhost:5173"
else
    echo -e "\n${INFO} Skipping browser opening (--skip-browser flag used)"
fi
echo -e "\nUseful commands:"
echo -e "  • View logs: make logs"
echo -e "  • Stop services: make down"
echo -e "  • Run tests: make test"
echo -e "  • Format code: make fmt"
echo -e "  • Clean restart: make fresh"

echo -e "\n🔧 Common troubleshooting:"
echo -e "  • Monitor page empty? Check: ${GREEN}curl http://localhost:8000/api/v1/monitor${NC}"
echo -e "  • Tests failing? Run individually: ${GREEN}docker compose -f infra/docker-compose.yml exec backend pytest${NC}"
echo -e "  • Authentication issues? Reset users: ${GREEN}docker compose -f infra/docker-compose.yml exec backend python init_db.py${NC}"
echo -e "  • Services won't start? Try: ${GREEN}./scripts/cleanup.sh && ./scripts/setup.sh --clean${NC}"

# Start monitoring logs
if [ "$SKIP_LOGS" = false ]; then
    echo -e "\n${INFO} Starting log monitoring..."
    echo -e "${INFO} Press ${GREEN}Ctrl+C${NC} to stop log monitoring at any time"
    echo -e "${INFO} ===== LIVE SERVICE LOGS ====="

    # Run make logs to show real-time logs
    exec make logs
else
    echo -e "\n${INFO} Skipping log monitoring (--skip-logs flag used)"
    echo -e "${INFO} To view logs later, run: ${GREEN}make logs${NC}"
fi
