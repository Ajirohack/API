# Model Context Protocol (MCP) Adapter

The Model Context Protocol (MCP) adapter provides a standardized way for models, tools, and agents to exchange context and capabilities. This document covers how to use the MCP adapter endpoints in the SpaceNew API.

## Overview

The MCP adapter enables:

1. Context management (creating, retrieving, updating contexts)
2. Tool invocation (running tools with context)
3. Model registration and prediction

## Endpoints

### Context Management

#### Create Context

```http
POST /api/mcp/context
```

Creates a new context of a specific type.

**Request Body:**

```json
{
  "context_type": "conversation|document|tool|system",
  "data": {
    // Context-specific data
  },
  "metadata": {
    // Optional metadata
  }
}
```

**Response:**

```json
{
  "status": "success",
  "context_id": "context-20250603-123456-abcd1234",
  "data": {
    "id": "context-20250603-123456-abcd1234",
    "type": "conversation",
    // Other context data
  }
}
```

#### Update Context

```http
POST /api/mcp/context/update
```

Updates an existing context.

**Request Body:**

```json
{
  "context_id": "context-20250603-123456-abcd1234",
  "updates": {
    // Fields to update
  },
  "metadata": {
    // Optional metadata updates
  }
}
```

**Response:**

```json
{
  "status": "success",
  "context_id": "context-20250603-123456-abcd1234",
  "updated_data": {
    // Updated context
  }
}
```

### Tool Invocation

#### Invoke Tool

```http
POST /api/mcp/tool-invoke
```

Invokes a tool, optionally with context.

**Request Body:**

```json
{
  "tool_name": "text_summarizer|sentiment_analyzer|question_answerer|translation|extraction",
  "parameters": {
    // Tool-specific parameters
  },
  "context_id": "optional-context-id"
}
```

**Response:**

```json
{
  "status": "success",
  "tool": "text_summarizer",
  "result": {
    "execution_id": "tool-exec-20250603-123456-abcd1234",
    "tool": "text_summarizer",
    "result": {
      // Tool-specific result
    }
  }
}
```

### Model Management

#### Register Model

```http
POST /api/mcp/model
```

Registers a new model.

**Request Body:**

```json
{
  "model_name": "my_model",
  "model_type": "text_classification|completion|embedding|etc",
  "parameters": {
    // Model parameters
  },
  "metadata": {
    // Optional metadata
  }
}
```

**Response:**

```json
{
  "status": "success",
  "model_id": "text_classification-my_model",
  "config": {
    // Model configuration
  }
}
```

#### Predict

```http
POST /api/mcp/predict
```

Makes a prediction using a registered model.

**Request Body:**

```json
{
  "model_id": "text_classification-my_model",
  "inputs": {
    // Model inputs
  },
  "context_id": "optional-context-id",
  "parameters": {
    // Optional prediction parameters
  }
}
```

**Response:**

```json
{
  "status": "success",
  "prediction": {
    "id": "prediction-20250603-123456-abcd1234",
    "model_id": "text_classification-my_model",
    "outputs": {
      // Prediction outputs
    },
    "metadata": {
      // Prediction metadata
    }
  }
}
```

## Available Tools

### Text Summarizer

Summarizes text content.

**Parameters:**

- `text`: The text to summarize (required)
- `max_length`: Maximum length of summary (default: 100)

### Sentiment Analyzer

Analyzes sentiment in text.

**Parameters:**

- `text`: The text to analyze (required)

### Question Answerer

Answers questions based on context.

**Parameters:**

- `question`: The question to answer (required)

### Translation

Translates text between languages.

**Parameters:**

- `text`: The text to translate (required)
- `source_lang`: Source language (default: "auto")
- `target_lang`: Target language (default: "en")

### Extraction

Extracts structured information from text.

**Parameters:**

- `text`: The text to extract from (required)
- `type`: Type of extraction - "entities" or "keywords" (default: "entities")

## Examples

### Creating a Conversation Context

```python
import requests

response = requests.post(
    "http://localhost:8000/api/mcp/context",
    json={
        "context_type": "conversation",
        "data": {
            "messages": [
                {"role": "user", "content": "Hello, I need help with financial analysis."},
                {"role": "assistant", "content": "I'd be happy to help with financial analysis. What specifically do you need?"}
            ],
            "state": {
                "current_topic": "financial_analysis"
            }
        },
        "metadata": {
            "user_id": "user123"
        }
    }
)

context_id = response.json()["context_id"]
```

### Invoking a Tool

```python
response = requests.post(
    "http://localhost:8000/api/mcp/tool-invoke",
    json={
        "tool_name": "sentiment_analyzer",
        "parameters": {
            "text": "I'm really excited about the financial analysis results. They look great!"
        },
        "context_id": context_id  # Optional
    }
)

result = response.json()["result"]
```

## Testing

### Testing Internal Functionality

You can test the MCP adapter's internal functionality using the provided Python test script:

```bash
python scripts/test_mcp_direct.py
```

This script tests core functions directly without going through HTTP endpoints:

- Context ID generation
- Text summarization
- Sentiment analysis
- Entity extraction
- Keyword extraction

### Testing HTTP Endpoints

To test the MCP adapter endpoints via HTTP, use the shell script:

```bash
# Test against a local deployment
./scripts/test_mcp_endpoints.sh http://localhost:8000

# Test against a specific URL
./scripts/test_mcp_endpoints.sh https://your-api-url.com
```

This script performs a sequence of HTTP requests to verify all MCP adapter endpoints:

1. Health check
2. Context creation
3. Tool invocation
4. Context update
5. Model registration
6. Model prediction

### Testing During Deployment

When deploying with the `deploy.sh` script, you can include endpoint testing:

```bash
./deploy.sh --test-endpoints
```

This will run the API, initialize the database, and then test all MCP endpoints.

## Integration Examples

The `model_manager.py` script provides a comprehensive client for working with the MCP adapter, featuring several examples of how to integrate MCP into your services:

### Basic Usage

```python
from scripts.model_manager import ModelManager
import asyncio

async def main():
    # Initialize the manager
    manager = ModelManager("http://localhost:8000/api/mcp")
    
    try:
        # Register a model
        model_id = await manager.register_model(
            model_name="my_model",
            model_type="text_classification"
        )
        
        # Make a prediction
        result = await manager.predict(
            model_id=model_id,
            inputs={"text": "This is a sample text"}
        )
        
        print(f"Prediction result: {result}")
    finally:
        await manager.close()

asyncio.run(main())
```

### Advanced Integration Scenarios

The `model_manager.py` script includes several example implementations:

1. **Conversation Management Example**: Demonstrates creating conversation contexts, updating them, and using them with tools and models.

2. **Document Analysis Example**: Shows how to create document contexts and analyze them with extraction tools.

3. **Multi-Service Integration Example**: Illustrates a complete workflow integrating multiple services with context sharing.

Run the script to see these examples in action:

```bash
python scripts/model_manager.py
```

### Implementing Your Own Integration

To implement your own integration:

1. Create a `ModelManager` instance
2. Use the methods for context, tool, and model operations:
   - `create_context` - Create a new context
   - `update_context` - Update an existing context
   - `invoke_tool` - Run a tool with optional context
   - `register_model` - Register a new model
   - `predict` - Make a prediction with a model

All operations are asynchronous and follow standard error handling patterns.
