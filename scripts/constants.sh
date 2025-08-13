#!/bin/bash
# =============================================================================
# Centralized Constants for X-University Scripts
# 
# This file loads configuration from the centralized dev.config.json
# and provides shell-friendly access to common development values.
# 
# Usage: source this file in other scripts
#   source "$(dirname "${BASH_SOURCE[0]}")/constants.sh"
# =============================================================================

# Get the script directory and config path
readonly SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
readonly CONFIG_FILE="$SCRIPT_DIR/../infra/dev.config.json"

# Check if jq is available for JSON parsing
if ! command -v jq &> /dev/null; then
    echo "Warning: jq not found. Using fallback values for constants."
    JQ_AVAILABLE=false
else
    JQ_AVAILABLE=true
fi

# Function to safely read JSON value with fallback
read_json_value() {
    local path="$1"
    local fallback="$2"
    
    if [ "$JQ_AVAILABLE" = true ] && [ -f "$CONFIG_FILE" ]; then
        jq -r "$path // \"$fallback\"" "$CONFIG_FILE" 2>/dev/null || echo "$fallback"
    else
        echo "$fallback"
    fi
}

# =============================================================================
# URLS & ENDPOINTS (loaded from config)
# =============================================================================
readonly FRONTEND_URL=$(read_json_value '.urls.frontend' 'http://localhost:5173')
readonly BACKEND_URL=$(read_json_value '.urls.backend' 'http://localhost:8000')
readonly API_BASE_URL=$(read_json_value '.urls.api_base' 'http://localhost:8000/api/v1')
readonly HEALTH_CHECK_URL=$(read_json_value '.urls.health_check' 'http://localhost:8000/health')
readonly API_DOCS_URL=$(read_json_value '.urls.api_docs' 'http://localhost:8000/docs')
readonly LOGIN_ENDPOINT=$(read_json_value '.endpoints.auth.login' '/api/v1/auth/login')
readonly MONITOR_ENDPOINT=$(read_json_value '.endpoints.monitor.base' '/api/v1/monitor')
readonly DB_PERFORMANCE_ENDPOINT=$(read_json_value '.endpoints.monitor.database' '/api/v1/monitor/database/performance')

# Build full URLs for endpoints
readonly LOGIN_FULL_URL="${BACKEND_URL}${LOGIN_ENDPOINT}"
readonly MONITOR_FULL_URL="${BACKEND_URL}${MONITOR_ENDPOINT}"

# =============================================================================
# USER CREDENTIALS (Development Only) - loaded from config
# =============================================================================
readonly DEV_PASSWORD=$(read_json_value '.credentials.default_password' 'password123')
readonly ADMIN_EMAIL=$(read_json_value '.credentials.users.admin.email' 'admin@example.com')
readonly INSTRUCTOR_EMAIL=$(read_json_value '.credentials.users.instructor.email' 'instructor@example.com')
readonly STUDENT_EMAIL=$(read_json_value '.credentials.users.student.email' 'student@example.com')

# Test users array format: "email:password:role"
readonly -a TEST_USERS=(
    "${ADMIN_EMAIL}:${DEV_PASSWORD}:admin"
    "${INSTRUCTOR_EMAIL}:${DEV_PASSWORD}:instructor"
    "${STUDENT_EMAIL}:${DEV_PASSWORD}:student"
)

# =============================================================================
# MESSAGES & LOG STRINGS (loaded from config)
# =============================================================================

# Setup Messages - loaded from config
readonly MSG_CHECKING_PREREQS=$(read_json_value '.messages.setup.checking_prereqs' 'Checking Prerequisites')
readonly MSG_DOCKER_STARTING=$(read_json_value '.messages.setup.docker_starting' 'Attempting to start Docker Desktop...')
readonly MSG_SERVICES_STARTING=$(read_json_value '.messages.setup.services_starting' 'Starting Docker Services')
readonly MSG_DATABASE_SETUP=$(read_json_value '.messages.setup.database_setup' 'Initializing database with default users...')
readonly MSG_SETUP_COMPLETE=$(read_json_value '.messages.setup.setup_complete' 'Setup Complete - Next Steps')

# Status Messages - loaded from config  
readonly MSG_BACKEND_HEALTHY=$(read_json_value '.messages.status.backend_healthy' 'Backend: Healthy')
readonly MSG_BACKEND_UNHEALTHY=$(read_json_value '.messages.status.backend_unhealthy' 'Backend: Unhealthy')
readonly MSG_FRONTEND_RUNNING=$(read_json_value '.messages.status.frontend_running' 'Frontend: Running')
readonly MSG_DATABASE_CONNECTED=$(read_json_value '.messages.status.database_connected' 'Database: Connected')

# Database Messages - loaded from config
readonly MSG_DB_CONNECTION_SUCCESS=$(read_json_value '.messages.database.connection_success' 'Database connection established')
readonly MSG_DB_MIGRATION_SUCCESS=$(read_json_value '.messages.database.migration_success' 'Database migrations completed successfully')
readonly MSG_DB_USERS_CREATED=$(read_json_value '.messages.database.users_created' 'Default users created successfully')
readonly MSG_DB_USERS_EXIST=$(read_json_value '.messages.database.users_exist' 'Found existing users, skipping initialization')

# Static messages not in config
readonly MSG_PYTHON_ENV_SETUP="Setting up Python Environment"
readonly MSG_NODE_ENV_SETUP="Setting up Node Environment"
readonly MSG_ENV_VARS_SETUP="Setting up Environment Variables"
readonly MSG_CLEANUP_ENV="Cleaning existing environments"
readonly MSG_DOCKER_TIMEOUT="Docker failed to start within 60 seconds"
readonly MSG_AUTH_WORKING="Authentication working"
readonly MSG_AUTH_FAILED="Authentication failed"

# =============================================================================
# DATABASE CONFIGURATION (loaded from config)
# =============================================================================
readonly DB_NAME=$(read_json_value '.database.name' 'xu2')
readonly DB_TEST_NAME=$(read_json_value '.database.test_name' 'xu2_test')
readonly DB_USER=$(read_json_value '.database.user' 'dev')
readonly DB_PASSWORD=$(read_json_value '.database.password' 'devpass123')
readonly DB_HOST=$(read_json_value '.database.host' 'localhost')
readonly DB_PORT=$(read_json_value '.database.port' '5432')

# =============================================================================
# DOCKER CONFIGURATION (loaded from config)
# =============================================================================
readonly POSTGRES_CONTAINER=$(read_json_value '.docker.containers.postgres' 'xu2-postgres')
readonly BACKEND_CONTAINER=$(read_json_value '.docker.containers.backend' 'xu2-backend')
readonly FRONTEND_CONTAINER=$(read_json_value '.docker.containers.frontend' 'xu2-frontend')
readonly PROJECT_NAME=$(read_json_value '.docker.project_name' 'x-university-infra')
readonly DOCKER_COMPOSE_FILE=$(read_json_value '.docker.compose_file' 'infra/docker-compose.yml')

# =============================================================================
# FILE PATHS
# =============================================================================
readonly ENV_FILE="infra/.env"
readonly ENV_EXAMPLE_FILE="infra/.env.example"
readonly BACKEND_DIR="backend"
readonly FRONTEND_DIR="frontend"
readonly SCRIPTS_DIR="scripts"
readonly INIT_DB_SCRIPT="backend/init_db.py"

# =============================================================================
# TIMEOUTS & INTERVALS (loaded from config)
# =============================================================================
readonly DOCKER_START_TIMEOUT=$(read_json_value '.timeouts.docker_start' '60')
readonly SERVICE_HEALTH_TIMEOUT=$(read_json_value '.timeouts.service_health' '180')
readonly HEALTH_CHECK_INTERVAL=$(read_json_value '.timeouts.health_check_interval' '5')
readonly CONNECTION_RETRY_COUNT=$(read_json_value '.timeouts.connection_retry' '10')
readonly MIGRATION_RETRY_COUNT=5
readonly USER_INIT_RETRY_COUNT=5

# =============================================================================
# COLOR CODES
# =============================================================================
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly RED='\033[0;31m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color
readonly INFO="${BLUE}[INFO]${NC}"
readonly SUCCESS="${GREEN}[SUCCESS]${NC}"
readonly ERROR="${RED}[ERROR]${NC}"
readonly WARNING="${YELLOW}[WARNING]${NC}"

# =============================================================================
# STATUS MESSAGES WITH FORMATTING
# =============================================================================
readonly STATUS_ALL_SYSTEMS_OPERATIONAL="${SUCCESS} 🎉 EXCELLENT: All systems are fully operational!"
readonly STATUS_PARTIAL_SUCCESS="${WARNING} ⚠️  PARTIAL: Core services running but authentication needs attention"
readonly STATUS_ISSUES_DETECTED="${ERROR} ❌ ISSUES: Some services are not working correctly"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

# Print section header
print_section() {
    echo -e "\n${BLUE}==== $1 ====${NC}"
}

# Print status with emoji
print_status() {
    local status=$1
    local message=$2
    case $status in
        "success"|"ok")
            echo -e "${SUCCESS} ✅ $message"
            ;;
        "error"|"fail")
            echo -e "${ERROR} ❌ $message"
            ;;
        "warning"|"warn")
            echo -e "${WARNING} ⚠️  $message"
            ;;
        "info")
            echo -e "${INFO} ℹ️  $message"
            ;;
        *)
            echo -e "$message"
            ;;
    esac
}

# Get user credentials by role
get_user_credentials() {
    local role=$1
    case $role in
        "admin")
            echo "${ADMIN_EMAIL}:${DEV_PASSWORD}"
            ;;
        "instructor")
            echo "${INSTRUCTOR_EMAIL}:${DEV_PASSWORD}"
            ;;
        "student")
            echo "${STUDENT_EMAIL}:${DEV_PASSWORD}"
            ;;
        *)
            echo ""
            ;;
    esac
}

# Display all available user credentials
show_user_credentials() {
    echo -e "${INFO} Available user accounts:"
    echo -e "  • ${GREEN}Admin:${NC}      ${ADMIN_EMAIL} / ${DEV_PASSWORD}"
    echo -e "  • ${GREEN}Instructor:${NC} ${INSTRUCTOR_EMAIL} / ${DEV_PASSWORD}"
    echo -e "  • ${GREEN}Student:${NC}    ${STUDENT_EMAIL} / ${DEV_PASSWORD}"
}

# Test authentication for a user
test_user_auth() {
    local email=$1
    local password=$2
    local role=$3
    
    local auth_response
    auth_response=$(curl -s -X POST "${LOGIN_ENDPOINT}" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"${email}\",\"password\":\"${password}\"}" 2>/dev/null)
    
    if echo "$auth_response" | grep -q "access_token"; then
        print_status "success" "Authentication successful for ${role}: ${email}"
        return 0
    else
        print_status "error" "Authentication failed for ${role}: ${email}"
        return 1
    fi
}

# Display service URLs
show_service_urls() {
    echo -e "${BLUE}🌐 Service URLs:${NC}"
    echo -e "Frontend:        ${FRONTEND_URL}"
    echo -e "Backend API:     ${BACKEND_URL}"
    echo -e "API Docs:        ${API_DOCS_URL}"
    echo -e "Database:        ${DB_HOST}:${DB_PORT}"
}

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

# Check if URL is reachable
check_url() {
    local url=$1
    local timeout=${2:-10}
    
    if curl -s --connect-timeout "$timeout" "$url" >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check if service is healthy
check_service_health() {
    local service_name=$1
    local health_url=$2
    
    if check_url "$health_url"; then
        print_status "success" "${service_name} is healthy"
        return 0
    else
        print_status "error" "${service_name} is not responding"
        return 1
    fi
}

# Export all functions and variables for use in other scripts
export -f print_section print_status get_user_credentials show_user_credentials
export -f test_user_auth show_service_urls check_url check_service_health

# Mark this file as loaded
readonly CONSTANTS_LOADED=true
