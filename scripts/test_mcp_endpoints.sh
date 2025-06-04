#!/bin/bash
# Test script for MCP adapter endpoints
# This script tests the MCP adapter endpoints by making HTTP requests to the API

# Set up colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# API URL
API_URL=${1:-"http://localhost:8000"}
MCP_URL="${API_URL}/api/mcp"

echo -e "${YELLOW}MCP Adapter Endpoint Test Script${NC}"
echo "============================================"
echo "Testing against: ${MCP_URL}"

# Function to make a request and check the response
function test_endpoint() {
  local name=$1
  local method=$2
  local endpoint=$3
  local data=$4
  local expected_status=$5

  echo -e "\n${YELLOW}Testing ${name}...${NC}"
  
  if [ "$method" == "GET" ]; then
    response=$(curl -s -o response.json -w "%{http_code}" ${MCP_URL}${endpoint})
  else
    response=$(curl -s -o response.json -w "%{http_code}" -X ${method} -H "Content-Type: application/json" -d "${data}" ${MCP_URL}${endpoint})
  fi
  
  if [ "$response" -eq "$expected_status" ]; then
    echo -e "${GREEN}✓ ${name} returned status ${response} as expected${NC}"
    echo "Response: $(cat response.json | head -50)"
    return 0
  else
    echo -e "${RED}✗ ${name} returned status ${response}, expected ${expected_status}${NC}"
    echo "Response: $(cat response.json)"
    return 1
  fi
}

# Test health endpoint
test_endpoint "Health Check" "GET" "/health" "" 200

# Test context creation
CONTEXT_DATA='{
  "context_type": "conversation",
  "data": {
    "messages": [
      {"role": "user", "content": "Hello"},
      {"role": "assistant", "content": "Hi there"}
    ],
    "state": {"active": true}
  },
  "metadata": {"user_id": "test123"}
}'

test_endpoint "Context Creation" "POST" "/context" "$CONTEXT_DATA" 200

# Extract context ID from response
CONTEXT_ID=$(cat response.json | grep -o '"context_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$CONTEXT_ID" ]; then
  echo -e "${RED}Could not extract context ID from response${NC}"
  exit 1
fi

echo -e "${GREEN}Created context with ID: ${CONTEXT_ID}${NC}"

# Test tool invocation
TOOL_DATA='{
  "tool_name": "sentiment_analyzer",
  "parameters": {
    "text": "I really love this product!"
  },
  "context_id": "'$CONTEXT_ID'"
}'

test_endpoint "Tool Invocation" "POST" "/tool-invoke" "$TOOL_DATA" 200

# Test context update
UPDATE_DATA='{
  "context_id": "'$CONTEXT_ID'",
  "updates": {
    "messages": [
      {"role": "user", "content": "Hello"},
      {"role": "assistant", "content": "Hi there"},
      {"role": "user", "content": "How are you?"}
    ]
  },
  "metadata": {"updated": true}
}'

test_endpoint "Context Update" "POST" "/context/update" "$UPDATE_DATA" 200

# Test model registration
MODEL_DATA='{
  "model_name": "test_model",
  "model_type": "text_classification",
  "parameters": {
    "version": "1.0",
    "features": ["sentiment"]
  },
  "metadata": {
    "description": "Test model for sentiment analysis"
  }
}'

test_endpoint "Model Registration" "POST" "/model" "$MODEL_DATA" 200

# Extract model ID from response
MODEL_ID=$(cat response.json | grep -o '"model_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$MODEL_ID" ]; then
  echo -e "${RED}Could not extract model ID from response${NC}"
  exit 1
fi

echo -e "${GREEN}Registered model with ID: ${MODEL_ID}${NC}"

# Test prediction
PREDICT_DATA='{
  "model_id": "'$MODEL_ID'",
  "inputs": {
    "text": "This is a test input"
  },
  "parameters": {
    "temperature": 0.7
  }
}'

test_endpoint "Model Prediction" "POST" "/predict" "$PREDICT_DATA" 200

# Clean up
rm -f response.json

echo -e "\n${GREEN}All MCP adapter endpoint tests completed!${NC}"
