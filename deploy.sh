#!/bin/bash
# Deployment script for SpaceNew API

# Set up colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}SpaceNew API Deployment Script${NC}"
echo "============================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Stop any running containers
echo -e "${YELLOW}Stopping any running containers...${NC}"
docker-compose down

# Build and start the containers
echo -e "${YELLOW}Building and starting containers...${NC}"
docker-compose up --build -d

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 10

# Run database migrations
echo -e "${YELLOW}Running database migrations...${NC}"
docker-compose exec api bash -c "chmod +x scripts/initialize_db.sh && ./scripts/initialize_db.sh"

echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${GREEN}API is now running at http://localhost:8000${NC}"
echo -e "${GREEN}API Documentation is available at http://localhost:8000/api/docs${NC}"
