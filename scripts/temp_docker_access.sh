#!/bin/bash

# Automated Temporary Docker Access Script
# This script temporarily enables Docker monitoring, fetches data, then reverts back

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/infra/docker-compose.yml"
OVERRIDE_FILE="/tmp/docker-compose.temp-monitoring.yml"
SIGNAL_FILE="/tmp/request_docker_access.signal"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Cleanup function to ensure we always revert
cleanup() {
    echo -e "\n${YELLOW}🔄 Ensuring secure mode is restored...${NC}"
    cd "$PROJECT_ROOT"
    docker compose -f "$DOCKER_COMPOSE_FILE" up -d --force-recreate backend >/dev/null 2>&1 || true
    rm -f "$OVERRIDE_FILE" >/dev/null 2>&1 || true
    rm -f "$SIGNAL_FILE" >/dev/null 2>&1 || true
    echo -e "${GREEN}✅ System restored to secure mode${NC}"
}

# Set trap to ensure cleanup happens even if script is interrupted
trap cleanup EXIT INT TERM

echo -e "${BLUE}🐳 Automated Temporary Docker Access${NC}"
echo -e "This will temporarily enable Docker monitoring, then automatically revert back."
echo -e "${RED}⚠️  Do NOT interrupt this script to avoid performance issues!${NC}"
echo ""

# Check if signal file exists (requested by API)
if [[ -f "$SIGNAL_FILE" ]]; then
    echo -e "${YELLOW}📡 API request detected for Docker access${NC}"
    rm -f "$SIGNAL_FILE"
fi

# Step 1: Create temporary override
echo -e "${YELLOW}1. Creating temporary Docker access configuration...${NC}"
cat > "$OVERRIDE_FILE" << 'EOF'
services:
  backend:
    user: "root"
    volumes:
      - ../backend:/app
      - /app/__pycache__
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      - TEMP_DOCKER_ACCESS=true
EOF

# Step 2: Enable Docker access
echo -e "${YELLOW}2. Temporarily enabling Docker access...${NC}"
cd "$PROJECT_ROOT"
docker compose -f "$DOCKER_COMPOSE_FILE" -f "$OVERRIDE_FILE" up -d --force-recreate backend >/dev/null

# Step 3: Wait for backend to start
echo -e "${YELLOW}3. Waiting for backend to restart with Docker access...${NC}"
sleep 3

# Step 4: Fetch data quickly
echo -e "${YELLOW}4. Fetching Docker container data...${NC}"
echo -e "   ${GREEN}✓${NC} Docker monitoring temporarily enabled"
echo -e "   ${GREEN}✓${NC} Visit http://localhost:5173/monitor to see containers"

# Step 5: Short window for data collection
echo -e "${YELLOW}5. Keeping Docker access active for 15 seconds...${NC}"
echo -e "   ${BLUE}💡 Refresh your monitor page now!${NC}"

for i in {15..1}; do
    echo -ne "\r   ⏰ Auto-revert in ${i} seconds... "
    sleep 1
done
echo ""

# Step 6: Automatic revert (handled by cleanup function)
echo -e "${YELLOW}6. Reverting to secure mode...${NC}"

# The cleanup function will handle the revert
exit 0
