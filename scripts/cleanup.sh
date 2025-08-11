#!/bin/bash

# Set script to exit on error
set -e

# Print colored output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Cleaning up X University development environment...${NC}"

# Stop all running containers
echo -e "\n${GREEN}Stopping running containers...${NC}"
docker compose -f infra/docker-compose.yml down

# Remove project containers
echo -e "\n${GREEN}Removing project containers...${NC}"
docker rm -f xu2-postgres xu2-backend xu2-frontend 2>/dev/null || true

# Remove project images
echo -e "\n${GREEN}Removing project images...${NC}"
docker rmi -f backend-x-university frontend-x-university 2>/dev/null || true

# Remove project volumes
echo -e "\n${GREEN}Removing project volumes...${NC}"
docker volume rm x-university-infra_postgres_data x-university-infra_neo4j_data x-university-infra_neo4j_logs x-university-infra_neo4j_import x-university-infra_neo4j_plugins 2>/dev/null || true

# Remove project and dependency images
echo -e "\n${GREEN}Removing project and dependency images...${NC}"
docker rmi -f postgres:16 2>/dev/null || true
docker rmi -f $(docker images | grep 'x-university\|postgres' | awk '{print $1":"$2}') 2>/dev/null || true

# Remove any dangling images
echo -e "\n${GREEN}Removing dangling images...${NC}"
docker image prune -f

# Remove any unused volumes
echo -e "\n${GREEN}Removing unused volumes...${NC}"
docker volume prune -f

echo -e "\n${GREEN}Cleanup complete!${NC}"
echo -e "${YELLOW}You can now rebuild the project with: docker compose -f infra/docker-compose.yml up -d --build${NC}"
