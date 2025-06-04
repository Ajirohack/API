"""
Model Manager for MCP Adapter
Provides a simple implementation for model loading and inference with MCP
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
import httpx
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("model_manager")

class ModelManager:
    """
    Model Manager for MCP Adapter integration
    Handles model registration, loading, and inference
    """
    
    def __init__(self, mcp_url: str = "http://localhost:8000/api/mcp"):
        self.mcp_url = mcp_url
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.models: Dict[str, Dict[str, Any]] = {}
        self.model_instances: Dict[str, Any] = {}
        
    async def close(self):
        """Close resources"""
        await self.http_client.aclose()
        
    async def register_model(
        self, 
        model_name: str, 
        model_type: str, 
        model_path: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register a model with the MCP adapter
        
        Args:
            model_name: Name of the model
            model_type: Type of model (e.g., 'text-generation', 'text-embedding')
            model_path: Path to model files (optional)
            parameters: Model parameters (optional)
            metadata: Model metadata (optional)
            
        Returns:
            model_id: The registered model ID
        """
        if parameters is None:
            parameters = {}
            
        if metadata is None:
            metadata = {}
            
        if model_path:
            parameters["model_path"] = model_path
            
        # Add registration timestamp
        metadata["registered_at"] = datetime.now().isoformat()
        
        # Register with MCP
        try:
            response = await self.http_client.post(
                f"{self.mcp_url}/model",
                json={
                    "model_name": model_name,
                    "model_type": model_type,
                    "parameters": parameters,
                    "metadata": metadata
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to register model: {response.text}")
                raise Exception(f"Model registration failed: {response.text}")
                
            result = response.json()
            model_id = result.get("model_id")
            
            # Cache model info
            self.models[model_id] = {
                "name": model_name,
                "type": model_type,
                "parameters": parameters,
                "metadata": metadata
            }
            
            logger.info(f"Registered model {model_name} with ID {model_id}")
            return model_id
            
        except Exception as e:
            logger.error(f"Error registering model: {str(e)}")
            raise
    
    async def load_model(self, model_id: str) -> bool:
        """
        Load a model into memory
        
        Args:
            model_id: The model ID to load
            
        Returns:
            success: Whether the model was loaded successfully
        """
        # Check if model is already loaded
        if model_id in self.model_instances:
            logger.info(f"Model {model_id} is already loaded")
            return True
            
        # Get model info
        model_info = self.models.get(model_id)
        if not model_info:
            # Try to fetch from MCP
            try:
                response = await self.http_client.get(
                    f"{self.mcp_url}/model/{model_id}"
                )
                
                if response.status_code != 200:
                    logger.error(f"Failed to get model info: {response.text}")
                    return False
                    
                model_info = response.json().get("config", {})
                self.models[model_id] = model_info
                
            except Exception as e:
                logger.error(f"Error getting model info: {str(e)}")
                return False
        
        # Demo implementation - just create a placeholder
        # In a real implementation, you would load the actual model
        self.model_instances[model_id] = {
            "id": model_id,
            "info": model_info,
            "loaded_at": datetime.now().isoformat()
        }
        
        logger.info(f"Loaded model {model_id}")
        return True
    
    async def predict(
        self,
        model_id: str,
        inputs: Dict[str, Any],
        context_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a prediction using a model
        
        Args:
            model_id: The model ID to use
            inputs: Input data for the model
            context_id: Optional context ID for the prediction
            parameters: Optional prediction parameters
            
        Returns:
            result: The prediction result
        """
        # Ensure model is loaded
        if model_id not in self.model_instances:
            loaded = await self.load_model(model_id)
            if not loaded:
                raise Exception(f"Failed to load model {model_id}")
        
        # Make prediction through MCP
        try:
            payload = {
                "model_id": model_id,
                "inputs": inputs
            }
            
            if context_id:
                payload["context_id"] = context_id
                
            if parameters:
                payload["parameters"] = parameters
                
            response = await self.http_client.post(
                f"{self.mcp_url}/predict",
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to make prediction: {response.text}")
                raise Exception(f"Prediction failed: {response.text}")
                
            result = response.json()
            return result.get("prediction", {})
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            raise
            
    async def create_context(
        self,
        context_type: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new context in the MCP adapter
        
        Args:
            context_type: Type of context (conversation, document, tool, system)
            data: Context data
            metadata: Optional context metadata
            
        Returns:
            context_id: The created context ID
        """
        if metadata is None:
            metadata = {}
            
        try:
            response = await self.http_client.post(
                f"{self.mcp_url}/context",
                json={
                    "context_type": context_type,
                    "data": data,
                    "metadata": metadata
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to create context: {response.text}")
                raise Exception(f"Context creation failed: {response.text}")
                
            result = response.json()
            context_id = result.get("context_id")
            
            logger.info(f"Created context with ID {context_id}")
            return context_id
            
        except Exception as e:
            logger.error(f"Error creating context: {str(e)}")
            raise
            
    async def update_context(
        self,
        context_id: str,
        updates: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing context
        
        Args:
            context_id: The context ID to update
            updates: The updates to apply
            metadata: Optional metadata updates
            
        Returns:
            updated_context: The updated context data
        """
        if metadata is None:
            metadata = {}
            
        try:
            response = await self.http_client.post(
                f"{self.mcp_url}/context/update",
                json={
                    "context_id": context_id,
                    "updates": updates,
                    "metadata": metadata
                }
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to update context: {response.text}")
                raise Exception(f"Context update failed: {response.text}")
                
            result = response.json()
            return result.get("updated_data", {})
            
        except Exception as e:
            logger.error(f"Error updating context: {str(e)}")
            raise
            
    async def invoke_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invoke a tool via the MCP adapter
        
        Args:
            tool_name: The name of the tool to invoke
            parameters: Tool parameters
            context_id: Optional context ID
            
        Returns:
            result: The tool execution result
        """
        try:
            payload = {
                "tool_name": tool_name,
                "parameters": parameters
            }
            
            if context_id:
                payload["context_id"] = context_id
                
            response = await self.http_client.post(
                f"{self.mcp_url}/tool-invoke",
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to invoke tool: {response.text}")
                raise Exception(f"Tool invocation failed: {response.text}")
                
            result = response.json()
            return result.get("result", {})
            
        except Exception as e:
            logger.error(f"Error invoking tool: {str(e)}")
            raise

# Enhanced usage examples
async def conversation_example():
    """Example of using MCP for a conversation"""
    manager = ModelManager()
    
    try:
        # Create a conversation context
        context_id = await manager.create_context(
            context_type="conversation",
            data={
                "messages": [
                    {"role": "user", "content": "I'm looking for investment advice."},
                    {"role": "assistant", "content": "I'd be happy to help with investment advice. What's your risk tolerance?"}
                ],
                "state": {
                    "current_topic": "investment_advice",
                    "user_profile": {
                        "risk_tolerance": "unknown"
                    }
                }
            },
            metadata={
                "user_id": "user123",
                "session_id": "session456"
            }
        )
        
        # Update context with new message
        await manager.update_context(
            context_id=context_id,
            updates={
                "messages": [
                    {"role": "user", "content": "I'm looking for investment advice."},
                    {"role": "assistant", "content": "I'd be happy to help with investment advice. What's your risk tolerance?"},
                    {"role": "user", "content": "I'm conservative with my investments."}
                ],
                "state": {
                    "current_topic": "investment_advice",
                    "user_profile": {
                        "risk_tolerance": "conservative"
                    }
                }
            }
        )
        
        # Analyze sentiment of the latest message
        sentiment_result = await manager.invoke_tool(
            tool_name="sentiment_analyzer",
            parameters={
                "text": "I'm conservative with my investments."
            },
            context_id=context_id
        )
        
        print(f"Sentiment analysis: {json.dumps(sentiment_result, indent=2)}")
        
        # Register and use a financial advice model
        model_id = await manager.register_model(
            model_name="financial_advisor",
            model_type="text_generation",
            parameters={
                "version": "1.0",
                "specialization": "conservative_investments"
            },
            metadata={
                "description": "Financial advice model for conservative investors",
                "author": "Space API Team"
            }
        )
        
        # Generate financial advice using the model and conversation context
        prediction = await manager.predict(
            model_id=model_id,
            inputs={
                "prompt": "Generate conservative investment advice"
            },
            context_id=context_id,
            parameters={
                "max_length": 150,
                "temperature": 0.7
            }
        )
        
        print(f"Financial advice: {json.dumps(prediction, indent=2)}")
        
    finally:
        await manager.close()

async def document_analysis_example():
    """Example of using MCP for document analysis"""
    manager = ModelManager()
    
    try:
        # Create a document context
        document_text = """
        Annual Financial Report 2025
        
        This year, our company achieved record revenue of $10.5 million,
        a 15% increase from the previous year. Net profit was $2.3 million,
        with an EBITDA of $3.1 million. Operating expenses increased by 5%
        to $4.8 million, primarily due to expansion into new markets.
        
        Our key investments in renewable energy technology yielded a 22% return,
        while our conservative bond portfolio provided stable 3.5% returns.
        """
        
        context_id = await manager.create_context(
            context_type="document",
            data={
                "content": document_text,
                "type": "financial_report",
                "title": "Annual Financial Report 2025"
            },
            metadata={
                "document_id": "doc789",
                "author": "Finance Department",
                "created_at": "2025-05-15T10:30:00Z"
            }
        )
        
        # Extract entities from the document
        entities = await manager.invoke_tool(
            tool_name="extraction",
            parameters={
                "text": document_text,
                "type": "entities"
            },
            context_id=context_id
        )
        
        print(f"Extracted entities: {json.dumps(entities, indent=2)}")
        
        # Extract keywords from the document
        keywords = await manager.invoke_tool(
            tool_name="extraction",
            parameters={
                "text": document_text,
                "type": "keywords"
            },
            context_id=context_id
        )
        
        print(f"Extracted keywords: {json.dumps(keywords, indent=2)}")
        
        # Summarize the document
        summary = await manager.invoke_tool(
            tool_name="text_summarizer",
            parameters={
                "text": document_text,
                "max_length": 100
            },
            context_id=context_id
        )
        
        print(f"Document summary: {json.dumps(summary, indent=2)}")
        
    finally:
        await manager.close()

async def multi_service_integration_example():
    """Example of integrating MCP with multiple services"""
    manager = ModelManager()
    
    try:
        # 1. Create a system context with configuration
        system_context_id = await manager.create_context(
            context_type="system",
            data={
                "system_type": "integration_workflow",
                "config": {
                    "services": ["crm", "analytics", "notification"],
                    "workflow_name": "customer_insights"
                }
            },
            metadata={
                "owner": "integration_team",
                "priority": "high"
            }
        )
        
        # 2. Create a tool context for CRM integration
        crm_context_id = await manager.create_context(
            context_type="tool",
            data={
                "tool_name": "crm_connector",
                "parameters": {
                    "endpoint": "https://crm.example.com/api/v1",
                    "auth_type": "oauth2"
                }
            }
        )
        
        # 3. Register a customer segmentation model
        model_id = await manager.register_model(
            model_name="customer_segmentation",
            model_type="classification",
            parameters={
                "features": ["purchase_history", "demographics", "engagement"],
                "segments": ["high_value", "growth", "at_risk", "dormant"]
            }
        )
        
        # 4. Create a document with customer data
        customer_data = """
        Customer ID: 12345
        Name: Jane Smith
        Signup Date: 2024-01-15
        Last Purchase: 2025-05-10
        Purchase Frequency: 2.3 per month
        Average Order Value: $125
        Total Spend: $3,450
        Product Categories: Electronics, Home Goods
        Support Tickets: 2 (resolved)
        """
        
        document_context_id = await manager.create_context(
            context_type="document",
            data={
                "content": customer_data,
                "type": "customer_profile"
            }
        )
        
        # 5. Extract structured information from customer data
        extracted_data = await manager.invoke_tool(
            tool_name="extraction",
            parameters={
                "text": customer_data,
                "type": "entities"
            },
            context_id=document_context_id
        )
        
        # 6. Run customer segmentation model
        segmentation_result = await manager.predict(
            model_id=model_id,
            inputs={
                "customer_id": "12345",
                "purchase_frequency": 2.3,
                "average_order_value": 125,
                "months_active": 16,
                "support_tickets": 2
            }
        )
        
        # 7. Update system context with integration results
        await manager.update_context(
            context_id=system_context_id,
            updates={
                "results": {
                    "customer_id": "12345",
                    "extracted_data": extracted_data,
                    "segmentation": segmentation_result,
                    "timestamp": datetime.now().isoformat()
                },
                "status": "completed"
            }
        )
        
        print("Multi-service integration completed successfully!")
        
    finally:
        await manager.close()

# Demo usage
async def main():
    """Demo the model manager"""
    manager = ModelManager()
    
    try:
        # Register a demo model
        model_id = await manager.register_model(
            model_name="text_classifier",
            model_type="text_classification",
            parameters={
                "version": "1.0",
                "features": ["sentiment", "topic"]
            },
            metadata={
                "description": "Demo text classifier model",
                "author": "Space API Team"
            }
        )
        
        # Load the model
        loaded = await manager.load_model(model_id)
        if not loaded:
            logger.error("Failed to load model")
            return
        
        # Make a prediction
        result = await manager.predict(
            model_id=model_id,
            inputs={
                "text": "I really love this product! It's amazing."
            },
            parameters={
                "temperature": 0.7
            }
        )
        
        print(f"Prediction result: {json.dumps(result, indent=2)}")
        
        # Run the enhanced examples
        print("\n=== Conversation Example ===")
        await conversation_example()
        
        print("\n=== Document Analysis Example ===")
        await document_analysis_example()
        
        print("\n=== Multi-Service Integration Example ===")
        await multi_service_integration_example()
        
    finally:
        await manager.close()

if __name__ == "__main__":
    asyncio.run(main())
