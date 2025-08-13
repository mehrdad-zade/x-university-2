#!/bin/bash

# Enhanced cleanup script for X University development environment
# Ensures complete removal of all project resources to prevent conflicts

set -e  # Exit on error for critical operations
set -o pipefail  # Fail on pipe errors

# Parse command-line arguments
FORCE_POSTGRES_CLEANUP=false
for arg in "$@"; do
    case $arg in
        --force-postgres)
            FORCE_POSTGRES_CLEANUP=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--force-postgres]"
            echo "Options:"
            echo "  --force-postgres    Aggressively remove ALL PostgreSQL data and images"
            echo "  --help, -h         Show this help message"
            exit 0
            ;;
    esac
done

# Print colored output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

INFO="${BLUE}[INFO]${NC}"
SUCCESS="${GREEN}[SUCCESS]${NC}"
WARNING="${YELLOW}[WARNING]${NC}"
ERROR="${RED}[ERROR]${NC}"

if [ "$FORCE_POSTGRES_CLEANUP" = true ]; then
    echo -e "${YELLOW}🧹 Enhanced cleanup with AGGRESSIVE PostgreSQL cleanup for X University development environment...${NC}"
    echo -e "${WARNING} ⚠️  This will remove ALL PostgreSQL data and images on this system!"
else
    echo -e "${YELLOW}🧹 Enhanced cleanup for X University development environment...${NC}"
fi

# Enhanced function to run cleanup commands with better error handling
run_cleanup_step() {
    local description="$1"
    local command="$2"
    local critical="${3:-false}"
    
    echo -e "\n${INFO} $description..."
    if eval "$command" >/dev/null 2>&1; then
        echo -e "${SUCCESS} ✓ $description completed"
        return 0
    else
        if [ "$critical" = "true" ]; then
            echo -e "${ERROR} ✗ $description failed (critical)"
            return 1
        else
            echo -e "${WARNING} ⚠ $description failed (non-critical, continuing)"
            return 0
        fi
    fi
}

# Function to force remove containers by pattern
force_remove_containers() {
    local pattern="$1"
    echo -e "${INFO} Looking for containers matching pattern: $pattern"
    
    # Get container IDs matching the pattern
    CONTAINER_IDS=$(docker ps -aq --filter "name=$pattern" 2>/dev/null || true)
    if [ -n "$CONTAINER_IDS" ]; then
        echo -e "${INFO} Found containers to remove: $(echo $CONTAINER_IDS | tr '\n' ' ')"
        docker rm -f $CONTAINER_IDS >/dev/null 2>&1 || true
        echo -e "${SUCCESS} Removed containers matching $pattern"
    else
        echo -e "${INFO} No containers found matching $pattern"
    fi
}

# Function to force remove images by pattern
force_remove_images() {
    local pattern="$1"
    echo -e "${INFO} Looking for images matching pattern: $pattern"
    
    # Get image IDs matching the pattern
    IMAGE_IDS=$(docker images -q "$pattern" 2>/dev/null || true)
    if [ -n "$IMAGE_IDS" ]; then
        echo -e "${INFO} Found images to remove: $(echo $IMAGE_IDS | tr '\n' ' ')"
        docker rmi -f $IMAGE_IDS >/dev/null 2>&1 || true
        echo -e "${SUCCESS} Removed images matching $pattern"
    else
        echo -e "${INFO} No images found matching $pattern"
    fi
}

# Function to force remove volumes by pattern
force_remove_volumes() {
    local pattern="$1"
    echo -e "${INFO} Looking for volumes matching pattern: $pattern"
    
    # Get volume names matching the pattern
    VOLUME_NAMES=$(docker volume ls -q | grep -E "$pattern" 2>/dev/null || true)
    if [ -n "$VOLUME_NAMES" ]; then
        echo -e "${INFO} Found volumes to remove: $(echo $VOLUME_NAMES | tr '\n' ' ')"
        echo $VOLUME_NAMES | xargs -r docker volume rm -f >/dev/null 2>&1 || true
        echo -e "${SUCCESS} Removed volumes matching $pattern"
    else
        echo -e "${INFO} No volumes found matching $pattern"
    fi
}

# Enhanced PostgreSQL cleanup function
cleanup_postgres_data() {
    echo -e "${INFO} Performing enhanced PostgreSQL data cleanup..."
    
    # Stop any running PostgreSQL containers first
    POSTGRES_CONTAINERS=$(docker ps -aq --filter "name=*postgres*" 2>/dev/null || true)
    if [ -n "$POSTGRES_CONTAINERS" ]; then
        echo -e "${INFO} Stopping PostgreSQL containers..."
        echo $POSTGRES_CONTAINERS | xargs -r docker stop --time 10 >/dev/null 2>&1 || true
        echo $POSTGRES_CONTAINERS | xargs -r docker rm -f >/dev/null 2>&1 || true
    fi
    
    # Remove PostgreSQL volumes with detailed checking
    POSTGRES_VOLUME_PATTERNS=(
        ".*postgres.*"
        ".*postgresql.*"
        "infra_postgres.*"
        "x-university-infra_postgres.*"
        ".*_postgres_data"
        ".*postgres_data.*"
    )
    
    for pattern in "${POSTGRES_VOLUME_PATTERNS[@]}"; do
        POSTGRES_VOLUMES=$(docker volume ls -q | grep -E "$pattern" 2>/dev/null || true)
        if [ -n "$POSTGRES_VOLUMES" ]; then
            echo -e "${INFO} Found PostgreSQL volumes: $(echo $POSTGRES_VOLUMES | tr '\n' ' ')"
            for volume in $POSTGRES_VOLUMES; do
                echo -e "${INFO} Inspecting volume: $volume"
                # Get detailed volume info
                VOLUME_INFO=$(docker volume inspect "$volume" 2>/dev/null || true)
                if [ -n "$VOLUME_INFO" ]; then
                    echo -e "${INFO} Removing PostgreSQL volume: $volume"
                    docker volume rm -f "$volume" >/dev/null 2>&1 || {
                        echo -e "${WARNING} Failed to remove $volume, attempting force cleanup..."
                        # Try to find and stop any containers using this volume
                        docker ps -aq | xargs -r -I {} docker inspect {} 2>/dev/null | grep -l "$volume" | cut -d'"' -f4 | xargs -r docker rm -f >/dev/null 2>&1 || true
                        docker volume rm -f "$volume" >/dev/null 2>&1 || true
                    }
                fi
            done
        fi
    done
    
    # Clean up any bind-mounted PostgreSQL directories
    if [ -d "data/postgres" ]; then
        echo -e "${INFO} Removing bind-mounted PostgreSQL directory: data/postgres"
        sudo rm -rf "data/postgres" 2>/dev/null || rm -rf "data/postgres" 2>/dev/null || true
    fi
    
    # Aggressive cleanup if flag is set
    if [ "$FORCE_POSTGRES_CLEANUP" = true ]; then
        echo -e "${WARNING} Performing AGGRESSIVE PostgreSQL cleanup..."
        
        # Remove ALL PostgreSQL containers (not just project ones)
        ALL_POSTGRES_CONTAINERS=$(docker ps -aq --filter "ancestor=postgres" 2>/dev/null || true)
        if [ -n "$ALL_POSTGRES_CONTAINERS" ]; then
            echo -e "${INFO} Removing ALL PostgreSQL containers..."
            echo $ALL_POSTGRES_CONTAINERS | xargs -r docker rm -f >/dev/null 2>&1 || true
        fi
        
        # Remove ALL PostgreSQL volumes 
        ALL_POSTGRES_VOLUMES=$(docker volume ls -q | grep -i postgres 2>/dev/null || true)
        if [ -n "$ALL_POSTGRES_VOLUMES" ]; then
            echo -e "${WARNING} Removing ALL PostgreSQL volumes..."
            echo $ALL_POSTGRES_VOLUMES | xargs -r docker volume rm -f >/dev/null 2>&1 || true
        fi
        
        # Remove ALL PostgreSQL images
        ALL_POSTGRES_IMAGES=$(docker images -q postgres 2>/dev/null || true)
        if [ -n "$ALL_POSTGRES_IMAGES" ]; then
            echo -e "${WARNING} Removing ALL PostgreSQL images..."
            echo $ALL_POSTGRES_IMAGES | xargs -r docker rmi -f >/dev/null 2>&1 || true
        fi
        
        # Clean up Docker builder cache for PostgreSQL
        docker builder prune --filter "label=postgres" -f >/dev/null 2>&1 || true
        
        echo -e "${SUCCESS} Aggressive PostgreSQL cleanup completed"
    fi
    
    # Clean up any temporary PostgreSQL files
    find . -name "*postgres*" -type f -path "*/tmp/*" -delete 2>/dev/null || true
    
    echo -e "${SUCCESS} Enhanced PostgreSQL cleanup completed"
}

# === PHASE 1: Stop all running services gracefully ===
echo -e "\n${BLUE}=== Phase 1: Graceful Service Shutdown ===${NC}"

# Stop services using docker-compose (try multiple compose file locations)
COMPOSE_FILES=(
    "infra/docker-compose.yml"
    "infra/docker-compose.yaml" 
    "docker-compose.yml"
    "docker-compose.yaml"
)

COMPOSE_STOPPED=false
for compose_file in "${COMPOSE_FILES[@]}"; do
    if [ -f "$compose_file" ]; then
        echo -e "${INFO} Found compose file: $compose_file"
        run_cleanup_step "Stopping services via $compose_file" \
            "docker compose -f $compose_file down --timeout 30 --remove-orphans"
        COMPOSE_STOPPED=true
        break
    fi
done

if [ "$COMPOSE_STOPPED" = "false" ]; then
    echo -e "${WARNING} No docker-compose file found, skipping compose down"
fi

# === PHASE 2: Force removal of project containers ===
echo -e "\n${BLUE}=== Phase 2: Container Cleanup ===${NC}"

# Remove containers by explicit names
CONTAINER_NAMES=(
    "xu2-postgres" 
    "xu2-backend" 
    "xu2-frontend" 
    "xu2-neo4j"
    "x-university-postgres"
    "x-university-backend"
    "x-university-frontend"
    "x-university-neo4j"
)

echo -e "${INFO} Removing containers by name..."
for container in "${CONTAINER_NAMES[@]}"; do
    if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
        echo -e "${INFO} Removing container: $container"
        docker rm -f "$container" >/dev/null 2>&1 || true
    fi
done

# Remove containers by pattern matching
force_remove_containers "*xu2*"
force_remove_containers "*x-university*"
force_remove_containers "*infra*"

# === PHASE 3: Network cleanup ===
echo -e "\n${BLUE}=== Phase 3: Network Cleanup ===${NC}"

# Remove project networks
NETWORK_PATTERNS=(
    "infra_default"
    "xu2_default"
    "x-university_default"
    "*x-university*"
    "*xu2*"
    "*infra*"
)

for pattern in "${NETWORK_PATTERNS[@]}"; do
    NETWORKS=$(docker network ls --format '{{.Name}}' | grep -E "$pattern" 2>/dev/null || true)
    if [ -n "$NETWORKS" ]; then
        echo -e "${INFO} Removing networks: $NETWORKS"
        echo "$NETWORKS" | xargs -r docker network rm >/dev/null 2>&1 || true
    fi
done

# === PHASE 4: Image cleanup ===
echo -e "\n${BLUE}=== Phase 4: Image Cleanup ===${NC}"

# Remove project-specific images
PROJECT_IMAGES=(
    "backend-x-university"
    "frontend-x-university"
    "x-university-backend"
    "x-university-frontend"
    "*x-university*"
    "*xu2*"
)

for image_pattern in "${PROJECT_IMAGES[@]}"; do
    force_remove_images "$image_pattern"
done

# === PHASE 5: Volume cleanup ===
echo -e "\n${BLUE}=== Phase 5: Volume Cleanup ===${NC}"

# Enhanced PostgreSQL cleanup first
cleanup_postgres_data

# Remove project volumes with all possible naming patterns
VOLUME_PATTERNS=(
    "infra_.*"
    "x-university-infra_.*"
    "xu2_.*"
    ".*postgres.*data.*"
    ".*neo4j.*"
    ".*x-university.*"
    ".*xu2.*"
)

for pattern in "${VOLUME_PATTERNS[@]}"; do
    force_remove_volumes "$pattern"
done

# === PHASE 6: Optional dependency cleanup ===
echo -e "\n${BLUE}=== Phase 6: Optional Dependency Cleanup ===${NC}"

# Remove PostgreSQL and other dependency images automatically
echo -e "${INFO} Removing dependency images..."

DEPENDENCY_IMAGES=(
    "postgres:16" 
    "postgres:15"
    "postgres:14"
    "neo4j:5.15"
    "neo4j:5.*"
    "postgres:*"
)

for image in "${DEPENDENCY_IMAGES[@]}"; do
    force_remove_images "$image"
done
echo -e "${SUCCESS} Dependency images removed"

# === PHASE 7: Local environment cleanup ===
echo -e "\n${BLUE}=== Phase 7: Local Environment Cleanup ===${NC}"

# Clean up Python and Node environments
if [ -d "backend/.venv" ]; then
    run_cleanup_step "Removing Python virtual environment" \
        "rm -rf backend/.venv" "false"
fi

if [ -d "frontend/node_modules" ]; then
    run_cleanup_step "Removing Node.js modules and lock files" \
        "rm -rf frontend/node_modules frontend/package-lock.json" "false"
fi

# Clean up any Python cache files
run_cleanup_step "Removing Python cache files" \
    "find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null" "false"

# Clean up any log files
if [ -d "logs" ]; then
    run_cleanup_step "Removing log files" \
        "rm -rf logs/*" "false"
fi

# === PHASE 8: Docker system cleanup ===
echo -e "\n${BLUE}=== Phase 8: Docker System Cleanup ===${NC}"

# Remove dangling images
run_cleanup_step "Removing dangling images" \
    "docker image prune -f" "false"

# Remove unused volumes automatically (affects all Docker volumes)
echo -e "${INFO} Removing ALL unused volumes..."
run_cleanup_step "Removing ALL unused volumes" \
    "docker volume prune -f" "false"

# Remove unused networks
run_cleanup_step "Removing unused networks" \
    "docker network prune -f" "false"

# === PHASE 9: Verification ===
echo -e "\n${BLUE}=== Phase 9: Cleanup Verification ===${NC}"
echo -e "${INFO} Performing comprehensive cleanup verification..."

# PostgreSQL-specific verification
echo -e "${INFO} PostgreSQL cleanup verification:"
POSTGRES_CONTAINERS=$(docker ps -aq --filter "name=*postgres*" | wc -l | tr -d ' ')
POSTGRES_VOLUMES=$(docker volume ls -q | { grep -E "(postgres|postgresql)" || true; } | wc -l | tr -d ' ')
POSTGRES_IMAGES=$(docker images --format '{{.Repository}}:{{.Tag}}' | { grep -i postgres || true; } | wc -l | tr -d ' ')

echo -e "  🐘 PostgreSQL containers: $POSTGRES_CONTAINERS remaining"
echo -e "  💾 PostgreSQL volumes: $POSTGRES_VOLUMES remaining"
echo -e "  🖼️  PostgreSQL images: $POSTGRES_IMAGES remaining"

if [ "$POSTGRES_VOLUMES" -gt 0 ]; then
    echo -e "\n${WARNING} Remaining PostgreSQL volumes:"
    docker volume ls | { grep -E "(postgres|postgresql)" || true; }
    echo -e "${INFO} These will be recreated fresh on next startup"
fi

# Check for bind mount directories that might cause issues
if [ -d "data" ]; then
    echo -e "${INFO} Checking for bind mount directories..."
    BIND_DIRS=$(find data -name "*postgres*" -type d 2>/dev/null || true)
    if [ -n "$BIND_DIRS" ]; then
        echo -e "${WARNING} Found PostgreSQL bind mount directories:"
        echo "$BIND_DIRS"
        echo -e "${INFO} These may cause 'directory not empty' errors"
    fi
fi

# Count remaining project resources
REMAINING_CONTAINERS=$(docker ps -aq --filter "name=*xu2*" --filter "name=*x-university*" | wc -l | tr -d ' ')
REMAINING_IMAGES=$(docker images --format 'table {{.Repository}}:{{.Tag}}' | { grep -E "(xu2|x-university|backend-x-university|frontend-x-university)" || true; } | wc -l | tr -d ' ')
REMAINING_NETWORKS=$(docker network ls --format '{{.Name}}' | { grep -E "(xu2|x-university|infra)" || true; } | wc -l | tr -d ' ')
REMAINING_VOLUMES=$(docker volume ls -q | { grep -E "(infra_|x-university-infra_|xu2_)" || true; } | wc -l | tr -d ' ')

echo -e "\n${INFO} General cleanup verification results:"
echo -e "  📦 Containers: $REMAINING_CONTAINERS remaining"
echo -e "  🖼️  Images: $REMAINING_IMAGES remaining" 
echo -e "  🌐 Networks: $REMAINING_NETWORKS remaining"
echo -e "  💾 Volumes: $REMAINING_VOLUMES remaining"

# Detailed verification
if [ "$REMAINING_CONTAINERS" -gt 0 ]; then
    echo -e "\n${WARNING} Remaining containers:"
    docker ps -a --filter "name=*xu2*" --filter "name=*x-university*" --format "table {{.Names}}\t{{.Status}}" || true
fi

if [ "$REMAINING_IMAGES" -gt 0 ]; then
    echo -e "\n${WARNING} Remaining images:"
    docker images --format 'table {{.Repository}}:{{.Tag}}\t{{.Size}}' | grep -E "(xu2|x-university|backend-x-university|frontend-x-university)" || true
fi

if [ "$REMAINING_VOLUMES" -gt 0 ]; then
    echo -e "\n${WARNING} Remaining volumes:"
    docker volume ls | grep -E "(infra_|x-university-infra_|xu2_)" || true
fi

# Overall status
TOTAL_REMAINING=$((REMAINING_CONTAINERS + REMAINING_IMAGES + REMAINING_NETWORKS + REMAINING_VOLUMES))

if [ "$TOTAL_REMAINING" -eq 0 ]; then
    echo -e "\n${SUCCESS} ✅ Perfect cleanup! All project resources have been removed"
    echo -e "${SUCCESS} 🎉 Environment is ready for a fresh setup"
else
    if [ "$TOTAL_REMAINING" -le 2 ]; then
        echo -e "\n${WARNING} ⚠️  Mostly clean - $TOTAL_REMAINING resources remaining (likely non-critical)"
    else
        echo -e "\n${WARNING} ⚠️  Partial cleanup - $TOTAL_REMAINING resources remaining"
        echo -e "${INFO} This may be due to:"
        echo -e "  • Resources in use by other processes"
        echo -e "  • Permission issues"
        echo -e "  • Docker daemon issues"
    fi
    echo -e "${INFO} Run ./scripts/setup.sh --clean to handle any remaining issues"
fi

echo -e "\n${SUCCESS} 🧹 Enhanced cleanup complete!"

# === PHASE 10: Next steps and system status ===
echo -e "\n${BLUE}=== Next Steps ===${NC}"
echo -e "${INFO} To start fresh, run one of:"
echo -e "  🚀 ${GREEN}./scripts/setup.sh --clean${NC}     - Complete fresh setup"
echo -e "  ⚡ ${GREEN}./scripts/setup.sh${NC}            - Normal setup"
echo -e "  🔧 ${GREEN}make setup${NC}             - Alternative setup method"
echo -e ""
echo -e "${INFO} If PostgreSQL issues persist:"
echo -e "  🛠️  ${GREEN}./scripts/cleanup.sh --force-postgres${NC} - Aggressive PostgreSQL cleanup"
echo -e "  📋 ${GREEN}make diagnose-postgres${NC}        - Run PostgreSQL diagnostics"

# Show current Docker resource usage
echo -e "\n${BLUE}=== Docker System Status ===${NC}"
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    echo -e "${INFO} Current Docker resource usage:"
    docker system df 2>/dev/null || echo -e "${WARNING} Could not retrieve Docker system info"
else
    echo -e "${WARNING} Docker is not running or not accessible"
fi

echo -e "\n${SUCCESS} 🎯 Ready for fresh setup!"

# Explicit success exit
exit 0
