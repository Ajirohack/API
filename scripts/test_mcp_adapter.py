#!/usr/bin/env python3
"""
MCP Adapter Test Client
Test script to verify MCP adapter endpoints functionality
"""
import argparse
import asyncio
import json
import logging
import uuid
from datetime import datetime
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp_test_client")

# Default API URL
DEFAULT_API_URL = "http://localhost:8000/api/mcp"

class MCPTestClient:
    """Test client for MCP adapter endpoints"""
    
    def __init__(self, base_url=DEFAULT_API_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.context_ids = {}
    
    async def close(self):
        await self.client.aclose()
    
    async def create_context(self, context_type, data, metadata=None):
        """Create a new context"""
        if metadata is None:
            metadata = {}
            
        payload = {
            "context_type": context_type,
            "data": data,
            "metadata": metadata
        }
        
        logger.info(f"Creating {context_type} context")
        response = await self.client.post(
            f"{self.base_url}/context",
            json=payload
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to create context: {response.text}")
            return None
        
        result = response.json()
        context_id = result.get("context_id")
        self.context_ids[context_type] = context_id
        logger.info(f"Created context with ID: {context_id}")
        return result
    
    async def update_context(self, context_id, updates, metadata=None):
        """Update an existing context"""
        if metadata is None:
            metadata = {}
            
        payload = {
            "context_id": context_id,
            "updates": updates,
            "metadata": metadata
        }
        
        logger.info(f"Updating context: {context_id}")
        response = await self.client.post(
            f"{self.base_url}/context/update",
            json=payload
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to update context: {response.text}")
            return None
        
        result = response.json()
        logger.info(f"Updated context: {context_id}")
        return result
    
    async def invoke_tool(self, tool_name, parameters, context_id=None):
        """Invoke a tool"""
        payload = {
            "tool_name": tool_name,
            "parameters": parameters
        }
        
        if context_id:
            payload["context_id"] = context_id
            
        logger.info(f"Invoking tool: {tool_name}")
        response = await self.client.post(
            f"{self.base_url}/tool-invoke",
            json=payload
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to invoke tool: {response.text}")
            return None
        
        result = response.json()
        logger.info(f"Tool executed: {tool_name}")
        return result
    
    async def register_model(self, model_name, model_type, parameters=None, metadata=None):
        """Register a model"""
        if parameters is None:
            parameters = {}
        if metadata is None:
            metadata = {}
            
        payload = {
            "model_name": model_name,
            "model_type": model_type,
            "parameters": parameters,
            "metadata": metadata
        }
        
        logger.info(f"Registering model: {model_name}")
        response = await self.client.post(
            f"{self.base_url}/model",
            json=payload
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to register model: {response.text}")
            return None
        
        result = response.json()
        model_id = result.get("model_id")
        logger.info(f"Registered model with ID: {model_id}")
        return result
    
    async def predict(self, model_id, inputs, context_id=None, parameters=None):
        """Make predictions with a model"""
        if parameters is None:
            parameters = {}
            
        payload = {
            "model_id": model_id,
            "inputs": inputs
        }
        
        if context_id:
            payload["context_id"] = context_id
        
        if parameters:
            payload["parameters"] = parameters
            
        logger.info(f"Making prediction with model: {model_id}")
        response = await self.client.post(
            f"{self.base_url}/predict",
            json=payload
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to make prediction: {response.text}")
            return None
        
        result = response.json()
        logger.info(f"Prediction completed with model: {model_id}")
        return result

async def run_conversation_test(client):
    """Test conversation context creation and tool usage"""
    # Create conversation context
    conversation = await client.create_context(
        "conversation",
        {
            "messages": [
                {"role": "user", "content": "Hello, I need help with financial analysis."},
                {"role": "assistant", "content": "I'd be happy to help with financial analysis. What specifically do you need?"}
            ],
            "state": {
                "current_topic": "financial_analysis",
                "user_preferences": {
                    "detail_level": "high"
                }
            }
        },
        {
            "source": "test_script",
            "user_id": "test_user_123"
        }
    )
    
    if not conversation:
        logger.error("Conversation test failed at context creation")
        return False
    
    conversation_id = conversation.get("context_id")
    
    # Use the sentiment analysis tool
    sentiment = await client.invoke_tool(
        "sentiment_analyzer",
        {
            "text": "I'm really excited about the financial analysis results. They look great!"
        },
        conversation_id
    )
    
    if not sentiment:
        logger.error("Conversation test failed at sentiment analysis")
        return False
    
    # Update the conversation context with new message
    update_result = await client.update_context(
        conversation_id,
        {
            "messages": [
                {"role": "user", "content": "Hello, I need help with financial analysis."},
                {"role": "assistant", "content": "I'd be happy to help with financial analysis. What specifically do you need?"},
                {"role": "user", "content": "I need to analyze quarterly earnings reports."}
            ]
        }
    )
    
    if not update_result:
        logger.error("Conversation test failed at context update")
        return False
    
    logger.info("Conversation test completed successfully")
    return True

async def run_document_test(client):
    """Test document context creation and tools"""
    # Create document context
    document = await client.create_context(
        "document",
        {
            "content": "Financial Report Q2 2025\n\nRevenue: $10.2M\nExpenses: $7.5M\nProfit: $2.7M\n\nThe company performed exceptionally well this quarter with 15% growth year over year.",
            "type": "financial_report"
        },
        {
            "source": "test_script",
            "doc_id": "fin_report_q2_2025"
        }
    )
    
    if not document:
        logger.error("Document test failed at context creation")
        return False
    
    document_id = document.get("context_id")
    
    # Use the extraction tool
    extraction = await client.invoke_tool(
        "extraction",
        {
            "text": "Financial Report Q2 2025\n\nRevenue: $10.2M\nExpenses: $7.5M\nProfit: $2.7M\n\nThe company performed exceptionally well this quarter with 15% growth year over year.",
            "type": "entities"
        },
        document_id
    )
    
    if not extraction:
        logger.error("Document test failed at entity extraction")
        return False
    
    # Use the summarization tool
    summary = await client.invoke_tool(
        "text_summarizer",
        {
            "text": "Financial Report Q2 2025\n\nRevenue: $10.2M\nExpenses: $7.5M\nProfit: $2.7M\n\nThe company performed exceptionally well this quarter with 15% growth year over year.",
            "max_length": 50
        },
        document_id
    )
    
    if not summary:
        logger.error("Document test failed at summarization")
        return False
    
    logger.info("Document test completed successfully")
    return True

async def run_model_test(client):
    """Test model registration and prediction"""
    # Register a model
    model = await client.register_model(
        "financial_analyzer",
        "text_classification",
        {
            "version": "1.0",
            "features": ["sentiment", "entity_recognition", "topic_classification"],
            "thresholds": {
                "confidence": 0.7
            }
        },
        {
            "description": "Financial text analysis model",
            "created_by": "test_script"
        }
    )
    
    if not model:
        logger.error("Model test failed at registration")
        return False
    
    model_id = model.get("model_id")
    
    # Make a prediction
    prediction = await client.predict(
        model_id,
        {
            "text": "Q2 results show strong growth in the technology sector with revenue up 12%"
        },
        parameters={
            "temperature": 0.7,
            "features": ["sentiment", "topic"]
        }
    )
    
    if not prediction:
        logger.error("Model test failed at prediction")
        return False
    
    logger.info("Model test completed successfully")
    return True

async def main():
    parser = argparse.ArgumentParser(description="MCP Adapter Test Client")
    parser.add_argument("--url", default=DEFAULT_API_URL, help=f"MCP API URL (default: {DEFAULT_API_URL})")
    parser.add_argument("--test", choices=["all", "conversation", "document", "model"], default="all",
                        help="Test to run (default: all)")
    args = parser.parse_args()
    
    client = MCPTestClient(args.url)
    
    try:
        if args.test == "all" or args.test == "conversation":
            await run_conversation_test(client)
        
        if args.test == "all" or args.test == "document":
            await run_document_test(client)
        
        if args.test == "all" or args.test == "model":
            await run_model_test(client)
            
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
