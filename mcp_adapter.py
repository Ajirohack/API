"""
MCP Adapter Router for Model Context Protocol integration.
Enables tool/agent interoperability via the Model Context Protocol standard.
"""
from fastapi import APIRouter, Request, HTTPException, Depends, status
from fastapi.responses import JSONResponse
# Removed fastapi_mcp import due to dependency conflicts
from typing import Dict, Any, Optional
import logging
from pydantic import BaseModel, Field
import uuid
from datetime import datetime
from context_providers.mem0_provider import ContextProvider

# Configure logging
logger = logging.getLogger("api.mcp_adapter")

router = APIRouter(prefix="/api/mcp", tags=["mcp"])

# Initialize context provider
context_provider = ContextProvider()

@router.get("/health")
async def health_check():
    """
    Health check endpoint for the MCP adapter.
    Verifies that the adapter and its context provider are functioning correctly.
    """
    try:
        # Generate a test context ID
        test_id = generate_context_id("health")
        
        # Test storing and retrieving context
        test_data = {"status": "healthy", "timestamp": datetime.now().isoformat()}
        await context_provider.store(test_id, test_data)
        retrieved = await context_provider.retrieve(test_id)
        
        # Clean up test data
        await context_provider.delete(test_id)
        
        # Verify the test worked
        if retrieved and retrieved.get("status") == "healthy":
            return {
                "status": "healthy",
                "message": "MCP adapter is functioning correctly",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "degraded",
                "message": "Context provider test failed",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": f"MCP adapter error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

def generate_context_id(prefix: str) -> str:
    """Generate a unique context ID with prefix"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}-{timestamp}-{unique_id}"

async def store_context(context_id: str, context_data: Dict[str, Any]) -> None:
    """Store context in the provider"""
    await context_provider.store(context_id, context_data)

async def retrieve_context(context_id: str) -> Dict[str, Any]:
    """Retrieve context from the provider"""
    return await context_provider.retrieve(context_id)

async def update_context(context_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update existing context"""
    context = await context_provider.retrieve(context_id)
    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Context not found: {context_id}"
        )
    
    # Deep merge updates
    updated_context = deep_merge(context, updates)
    await context_provider.store(context_id, updated_context)
    return updated_context

def deep_merge(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    merged = base.copy()
    for key, value in updates.items():
        if (
            key in merged and 
            isinstance(merged[key], dict) and 
            isinstance(value, dict)
        ):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged

class ContextRequest(BaseModel):
    context_type: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ToolRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    context_id: Optional[str] = None

class ContextUpdateRequest(BaseModel):
    context_id: str
    updates: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ModelRequest(BaseModel):
    model_name: str
    model_type: str
    parameters: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class PredictRequest(BaseModel):
    model_id: str
    inputs: Dict[str, Any]
    context_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)

@router.post("/context")
async def mcp_context_endpoint(request: Request, context_data: ContextRequest):
    """
    Handle incoming context requests from external components.
    """
    try:
        logger.info(f"Received context request for type: {context_data.context_type}")
        
        # Process the context based on type
        processed_context = await process_context(context_data)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "context_id": processed_context.get("id"),
                "data": processed_context
            }
        )
    except Exception as e:
        logger.error(f"Error processing context: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process context: {str(e)}"
        )

@router.post("/tool-invoke")
async def mcp_tool_invoke(request: Request, tool_data: ToolRequest):
    """
    Handle tool invocation requests from external components.
    """
    try:
        logger.info(f"Received tool invocation request for: {tool_data.tool_name}")
        
        # Validate and execute the tool
        result = await execute_tool(tool_data)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "tool": tool_data.tool_name,
                "result": result
            }
        )
    except Exception as e:
        logger.error(f"Error executing tool: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute tool: {str(e)}"
        )

@router.post("/context/update")
async def update_context_endpoint(request: Request, update_data: ContextUpdateRequest):
    """
    Handle context update requests from external components.
    """
    try:
        logger.info(f"Received context update request for ID: {update_data.context_id}")
        
        # Process the context update
        # Retrieve existing context
        context = await retrieve_context(update_data.context_id)
        if not context:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Context not found: {update_data.context_id}"
            )
        
        # Update context
        updated_context = await update_context(update_data.context_id, update_data.updates)
        
        # Apply metadata updates if provided
        if update_data.metadata:
            # If context already has metadata, merge with new metadata
            if "metadata" in updated_context:
                updated_metadata = deep_merge(updated_context["metadata"], update_data.metadata)
            else:
                updated_metadata = update_data.metadata
            
            await update_context(update_data.context_id, {"metadata": updated_metadata})
            updated_context["metadata"] = updated_metadata
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "context_id": update_data.context_id,
                "updated_data": updated_context
            }
        )
    except Exception as e:
        logger.error(f"Error updating context: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update context: {str(e)}"
        )

@router.post("/model")
async def register_model(request: Request, model_data: ModelRequest):
    """
    Register a new model with the system
    """
    try:
        logger.info(f"Registering model: {model_data.model_name}")
        
        model_id = f"{model_data.model_type}-{model_data.model_name}"
        
        # Store model configuration
        model_config = {
            "id": model_id,
            "name": model_data.model_name,
            "type": model_data.model_type,
            "parameters": model_data.parameters,
            "metadata": model_data.metadata,
            "registered_at": datetime.now().isoformat()
        }
        
        await store_context(f"model-{model_id}", model_config)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "model_id": model_id,
                "config": model_config
            }
        )
        
    except Exception as e:
        logger.error(f"Error registering model: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/predict")
async def model_predict(request: Request, predict_data: PredictRequest):
    """
    Make predictions using a registered model
    """
    try:
        logger.info(f"Prediction request for model: {predict_data.model_id}")
        
        # Retrieve model configuration
        model_config = await retrieve_context(f"model-{predict_data.model_id}")
        if not model_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model not found: {predict_data.model_id}"
            )
        
        # Get context if provided
        context = None
        if predict_data.context_id:
            context = await retrieve_context(predict_data.context_id)
            if not context:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Context not found: {predict_data.context_id}"
                )
        
        # Prepare prediction parameters
        prediction_params = {
            "model_config": model_config,
            "inputs": predict_data.inputs,
            "context": context,
            "parameters": predict_data.parameters
        }
        
        # Generate prediction ID for tracking
        prediction_id = generate_context_id("prediction")
        
        # Store prediction request
        await store_context(prediction_id, {
            "id": prediction_id,
            "model_id": predict_data.model_id,
            "inputs": predict_data.inputs,
            "context_id": predict_data.context_id,
            "parameters": predict_data.parameters,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        })
        
        # TODO: Implement actual model prediction logic here
        # This would typically involve:
        # 1. Loading the appropriate model
        # 2. Preprocessing inputs
        # 3. Running prediction
        # 4. Post-processing outputs
        
        # For now, return a mock response
        prediction_result = {
            "id": prediction_id,
            "model_id": predict_data.model_id,
            "outputs": {
                "result": "Mock prediction result",
                "confidence": 0.95
            },
            "metadata": {
                "duration_ms": 100,
                "model_version": "1.0"
            }
        }
        
        # Update prediction status
        await update_context(prediction_id, {
            "status": "completed",
            "outputs": prediction_result["outputs"],
            "metadata": prediction_result["metadata"]
        })
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "prediction": prediction_result
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error making prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

async def process_context(context_data: ContextRequest) -> Dict[str, Any]:
    """Process and store context based on type"""
    context_types = {
        "conversation": process_conversation_context,
        "document": process_document_context,
        "tool": process_tool_context,
        "system": process_system_context
    }
    
    processor = context_types.get(context_data.context_type)
    if not processor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported context type: {context_data.context_type}"
        )
    
    return await processor(context_data.data, context_data.metadata)

async def process_conversation_context(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Process conversation history and state"""
    # Extract messages and state
    messages = data.get("messages", [])
    state = data.get("state", {})
    
    # Generate context ID
    context_id = generate_context_id("conversation")
    
    # Store in context provider
    context = {
        "id": context_id,
        "type": "conversation",
        "messages": messages,
        "state": state,
        "metadata": metadata
    }
    await store_context(context_id, context)
    
    return context

async def process_document_context(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Process document content and structure"""
    content = data.get("content")
    doc_type = data.get("type", "text")
    
    # Generate context ID
    context_id = generate_context_id("document")
    
    # Process and store document
    context = {
        "id": context_id,
        "type": "document",
        "content": content,
        "doc_type": doc_type,
        "metadata": metadata
    }
    await store_context(context_id, context)
    
    return context

async def process_tool_context(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Process tool state and parameters"""
    tool_name = data.get("tool_name")
    params = data.get("parameters", {})
    
    # Generate context ID
    context_id = generate_context_id("tool")
    
    # Store tool context
    context = {
        "id": context_id,
        "type": "tool",
        "tool_name": tool_name,
        "parameters": params,
        "metadata": metadata
    }
    await store_context(context_id, context)
    
    return context

async def process_system_context(data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Process system state and configuration"""
    system_type = data.get("system_type")
    config = data.get("config", {})
    
    # Generate context ID
    context_id = generate_context_id("system")
    
    # Store system context
    context = {
        "id": context_id,
        "type": "system",
        "system_type": system_type,
        "config": config,
        "metadata": metadata
    }
    await store_context(context_id, context)
    
    return context

async def execute_tool(tool_data: ToolRequest) -> Dict[str, Any]:
    """Execute the requested tool with given parameters."""
    
    # Dictionary of available tools
    tools = {
        "text_summarizer": execute_text_summarizer,
        "sentiment_analyzer": execute_sentiment_analyzer,
        "question_answerer": execute_question_answerer,
        "translation": execute_translation,
        "extraction": execute_extraction
    }
    
    # Check if tool exists
    if tool_data.tool_name not in tools:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tool not found: {tool_data.tool_name}"
        )
    
    # Get context if provided
    context = None
    if tool_data.context_id:
        context = await retrieve_context(tool_data.context_id)
        if not context:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Context not found: {tool_data.context_id}"
            )
    
    # Execute the tool
    tool_fn = tools[tool_data.tool_name]
    result = await tool_fn(tool_data.parameters, context)
    
    # Generate and store execution record
    execution_id = generate_context_id("tool-exec")
    execution_record = {
        "id": execution_id,
        "tool": tool_data.tool_name,
        "parameters": tool_data.parameters,
        "context_id": tool_data.context_id,
        "result": result,
        "timestamp": datetime.now().isoformat()
    }
    
    await store_context(execution_id, execution_record)
    
    return {
        "execution_id": execution_id,
        "tool": tool_data.tool_name,
        "result": result
    }

async def execute_text_summarizer(parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Summarize text content"""
    text = parameters.get("text", "")
    max_length = parameters.get("max_length", 100)
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text parameter is required"
        )
    
    # Simple summarization (in production would use proper NLP)
    if len(text) <= max_length:
        summary = text
    else:
        # Very basic summarization - first sentence plus length restriction
        sentences = text.split(".")
        summary = sentences[0] + "."
        if len(summary) < max_length and len(sentences) > 1:
            summary += " " + sentences[1] + "."
        summary = summary[:max_length] + ("..." if len(summary) > max_length else "")
    
    return {
        "summary": summary,
        "original_length": len(text),
        "summary_length": len(summary)
    }

async def execute_sentiment_analyzer(parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Analyze sentiment of text"""
    text = parameters.get("text", "")
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text parameter is required"
        )
    
    # Simple sentiment analysis (in production would use proper NLP)
    positive_words = ["good", "great", "excellent", "happy", "like", "love", "best"]
    negative_words = ["bad", "terrible", "awful", "hate", "dislike", "worst"]
    
    text_lower = text.lower()
    
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    total = pos_count + neg_count
    if total == 0:
        sentiment = "neutral"
        score = 0.0
    else:
        score = (pos_count - neg_count) / total
        if score > 0.2:
            sentiment = "positive"
        elif score < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
    
    return {
        "sentiment": sentiment,
        "score": score,
        "details": {
            "positive_matches": pos_count,
            "negative_matches": neg_count
        }
    }

async def execute_question_answerer(parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Answer questions based on context"""
    question = parameters.get("question", "")
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question parameter is required"
        )
    
    # Use context if available
    context_content = ""
    if context and "content" in context:
        context_content = context["content"]
    
    # Simple demo response
    return {
        "answer": "This is a placeholder answer. In production, this would use an actual QA model.",
        "confidence": 0.7,
        "sources": []
    }

async def execute_translation(parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Translate text between languages"""
    text = parameters.get("text", "")
    source_lang = parameters.get("source_lang", "auto")
    target_lang = parameters.get("target_lang", "en")
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text parameter is required"
        )
    
    if not target_lang:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target language parameter is required"
        )
    
    # Simple demo response
    return {
        "translated_text": f"[Translation of '{text}' from {source_lang} to {target_lang}]",
        "detected_source_lang": source_lang if source_lang != "auto" else "en",
        "target_lang": target_lang
    }

async def execute_extraction(parameters: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Extract structured information from text"""
    text = parameters.get("text", "")
    extract_type = parameters.get("type", "entities")
    
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text parameter is required"
        )
    
    # Simple entity extraction (for demonstration)
    if extract_type == "entities":
        # Very simple entity recognition
        potential_entities = text.split()
        entities = [
            word for word in potential_entities 
            if word and word[0].isupper() and len(word) > 1
        ]
        
        return {
            "entities": entities,
            "count": len(entities)
        }
    
    # Simple keyword extraction
    elif extract_type == "keywords":
        # Very simple keyword extraction
        words = text.lower().split()
        stopwords = ["the", "a", "an", "in", "on", "at", "to", "for", "with", "by", "about", "like"]
        keywords = [
            word for word in words 
            if word and len(word) > 3 and word not in stopwords
        ]
        
        return {
            "keywords": keywords[:10],  # Limit to top 10
            "count": len(keywords)
        }
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported extraction type: {extract_type}"
        )
