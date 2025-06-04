#!/bin/bash
# Deployment script for SpaceNew API

# Set up colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Process command line arguments
RUN_ENDPOINT_TESTS=false

# Process command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --test-endpoints) RUN_ENDPOINT_TESTS=true ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

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

# Check for port conflicts
echo -e "${YELLOW}Checking for port conflicts...${NC}"
POSTGRES_PORT=5433
REDIS_PORT=6380
API_PORT=8000

# Check if PostgreSQL port is in use
if lsof -i:$POSTGRES_PORT &>/dev/null; then
    echo -e "${RED}Port $POSTGRES_PORT is already in use. Please stop any running PostgreSQL instances or change the port in docker-compose.yml.${NC}"
    exit 1
fi

# Check if Redis port is in use
if lsof -i:$REDIS_PORT &>/dev/null; then
    echo -e "${RED}Port $REDIS_PORT is already in use. Please stop any running Redis instances or change the port in docker-compose.yml.${NC}"
    exit 1
fi

# Check if API port is in use
if lsof -i:$API_PORT &>/dev/null; then
    echo -e "${RED}Port $API_PORT is already in use. Please stop any services using this port or change the port in docker-compose.yml.${NC}"
    exit 1
fi

# Stop any running containers
echo -e "${YELLOW}Stopping any running containers...${NC}"
docker-compose down

# Build and start the containers
echo -e "${YELLOW}Building and starting containers...${NC}"
if ! docker-compose up --build -d; then
    echo -e "${RED}Failed to start containers. Check docker logs for details.${NC}"
    exit 1
fi

# Wait for services to be ready
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
echo -e "${YELLOW}This may take up to 30 seconds...${NC}"

# Wait for API to be ready (with timeout)
TIMEOUT=60
START_TIME=$(date +%s)
while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED_TIME=$((CURRENT_TIME - START_TIME))
    
    if [ $ELAPSED_TIME -gt $TIMEOUT ]; then
        echo -e "${RED}Timeout waiting for API to be ready. Check logs:${NC}"
        docker-compose logs api
        exit 1
    fi
    
    if docker-compose exec -T api curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}API is ready.${NC}"
        break
    fi
    
    echo -e "${YELLOW}Waiting for API to start... (${ELAPSED_TIME}s)${NC}"
    sleep 5
done

# Run database migrations
echo -e "${YELLOW}Checking database connection...${NC}"

# Wait for PostgreSQL to be ready (with timeout)
TIMEOUT=30
START_TIME=$(date +%s)
while true; do
    CURRENT_TIME=$(date +%s)
    ELAPSED_TIME=$((CURRENT_TIME - START_TIME))
    
    if [ $ELAPSED_TIME -gt $TIMEOUT ]; then
        echo -e "${RED}Timeout waiting for PostgreSQL to be ready. Check logs:${NC}"
        docker-compose logs db
        exit 1
    fi
    
    if docker-compose exec -T db pg_isready -h localhost > /dev/null 2>&1; then
        echo -e "${GREEN}PostgreSQL is ready.${NC}"
        break
    fi
    
    echo -e "${YELLOW}Waiting for PostgreSQL to start... (${ELAPSED_TIME}s)${NC}"
    sleep 2
done

# Run database initialization
echo -e "${YELLOW}Initializing database...${NC}"
if ! docker-compose exec -T api bash -c "chmod +x /app/scripts/initialize_db.sh && /app/scripts/initialize_db.sh"; then
    echo -e "${RED}Failed to initialize database. Check logs for details.${NC}"
    docker-compose logs api
    exit 1
fi

# Check MCP adapter health
echo -e "${YELLOW}Checking MCP adapter health...${NC}"
MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    MCP_HEALTH_CHECK=$(docker-compose exec -T api curl -s http://localhost:8000/api/mcp/health)
    if echo "$MCP_HEALTH_CHECK" | grep -q "healthy"; then
        echo -e "${GREEN}MCP adapter is healthy.${NC}"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo -e "${YELLOW}MCP adapter health check failed. Retrying (${RETRY_COUNT}/${MAX_RETRIES})...${NC}"
            sleep 5
        else
            echo -e "${YELLOW}MCP adapter health check failed. This is not critical, but should be investigated.${NC}"
            echo "$MCP_HEALTH_CHECK"
        fi
    fi
done

# Test MCP adapter functionality
echo -e "${YELLOW}Testing MCP adapter functionality...${NC}"
if ! docker-compose exec -T api bash -c "chmod +x /app/scripts/test_mcp_direct.py && python /app/scripts/test_mcp_direct.py"; then
    echo -e "${YELLOW}MCP adapter tests failed. This is not critical, but should be investigated.${NC}"
else
    echo -e "${GREEN}MCP adapter functionality verified.${NC}"
fi

echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${GREEN}API is now running at http://localhost:8000${NC}"
echo -e "${GREEN}API Documentation is available at http://localhost:8000/api/docs${NC}"

# Run endpoint tests if requested
if [ "$RUN_ENDPOINT_TESTS" = true ]; then
    echo -e "${YELLOW}Running MCP endpoint tests...${NC}"
    if ! ./scripts/test_mcp_endpoints.sh http://localhost:8000; then
        echo -e "${YELLOW}MCP endpoint tests failed. This is not critical, but should be investigated.${NC}"
    else
        echo -e "${GREEN}MCP endpoint tests completed successfully.${NC}"
    fi
fi

# Display container status
echo -e "${YELLOW}Container status:${NC}"
docker-compose ps
