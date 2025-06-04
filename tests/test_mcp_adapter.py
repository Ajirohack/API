"""
Unit tests for the MCP Adapter
"""
import pytest
import json
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock

from main import app
from mcp_adapter import generate_context_id

client = TestClient(app)

@pytest.fixture
def mock_context_provider():
    """Mock the context provider for testing"""
    with patch("mcp_adapter.context_provider") as mock_provider:
        # Set up AsyncMock methods
        mock_provider.store = AsyncMock()
        mock_provider.retrieve = AsyncMock()
        mock_provider.update = AsyncMock()
        mock_provider.delete = AsyncMock()
        
        # Configure default return values
        mock_provider.retrieve.return_value = None
        
        yield mock_provider

def test_generate_context_id():
    """Test context ID generation"""
    context_id = generate_context_id("test")
    
    # Check format: prefix-timestamp-uuid
    parts = context_id.split("-")
    assert parts[0] == "test"
    assert len(parts) >= 3
    
    # Check timestamp part (should be current date)
    current_date = datetime.now().strftime("%Y%m%d")
    assert current_date in parts[1]

class TestContextEndpoints:
    """Tests for context management endpoints"""
    
    def test_create_conversation_context(self, mock_context_provider):
        """Test creating a conversation context"""
        # Configure mock to return a successful storage
        mock_context_provider.store.return_value = None
        
        # Test data
        test_data = {
            "context_type": "conversation",
            "data": {
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there"}
                ],
                "state": {"active": True}
            },
            "metadata": {"user_id": "test123"}
        }
        
        # Make request
        response = client.post("/api/mcp/context", json=test_data)
        
        # Verify response
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert "context_id" in result
        assert result["context_id"].startswith("conversation-")
        
        # Verify mock called
        mock_context_provider.store.assert_called_once()
    
    def test_update_context(self, mock_context_provider):
        """Test updating a context"""
        # Configure mock to return an existing context
        context_id = "test-context-123"
        mock_context = {
            "id": context_id,
            "type": "conversation",
            "messages": [{"role": "user", "content": "Hello"}],
            "metadata": {"created_at": "2025-06-03T12:00:00"}
        }
        mock_context_provider.retrieve.return_value = mock_context
        
        # Update data
        update_data = {
            "context_id": context_id,
            "updates": {
                "messages": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there"}
                ]
            }
        }
        
        # Configure mock for update
        updated_context = {**mock_context}
        updated_context["messages"] = update_data["updates"]["messages"]
        mock_context_provider.store.return_value = None
        
        # Make request
        response = client.post("/api/mcp/context/update", json=update_data)
        
        # Verify response
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert result["context_id"] == context_id
        
        # Verify mock called
        mock_context_provider.retrieve.assert_called_once_with(context_id)
        mock_context_provider.store.assert_called_once()

class TestToolEndpoints:
    """Tests for tool invocation endpoints"""
    
    def test_text_summarizer_tool(self, mock_context_provider):
        """Test the text summarizer tool"""
        # Configure mock
        execution_id = "tool-exec-123456"
        with patch("mcp_adapter.generate_context_id", return_value=execution_id):
            # Test data
            tool_data = {
                "tool_name": "text_summarizer",
                "parameters": {
                    "text": "This is a long text that needs summarizing. It contains multiple sentences and details.",
                    "max_length": 20
                }
            }
            
            # Make request
            response = client.post("/api/mcp/tool-invoke", json=tool_data)
            
            # Verify response
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert result["tool"] == "text_summarizer"
            assert "result" in result
            
            # Check tool result
            tool_result = result["result"]
            assert "execution_id" in tool_result
            assert tool_result["execution_id"] == execution_id
            assert "result" in tool_result
            assert "summary" in tool_result["result"]
            assert len(tool_result["result"]["summary"]) <= 23  # 20 + "..."
    
    def test_sentiment_analyzer_tool(self, mock_context_provider):
        """Test the sentiment analyzer tool"""
        # Configure mock
        execution_id = "tool-exec-123456"
        with patch("mcp_adapter.generate_context_id", return_value=execution_id):
            # Test data
            tool_data = {
                "tool_name": "sentiment_analyzer",
                "parameters": {
                    "text": "I love this product! It's the best thing ever."
                }
            }
            
            # Make request
            response = client.post("/api/mcp/tool-invoke", json=tool_data)
            
            # Verify response
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert result["tool"] == "sentiment_analyzer"
            
            # Check tool result
            tool_result = result["result"]
            assert "result" in tool_result
            assert "sentiment" in tool_result["result"]
            assert tool_result["result"]["sentiment"] == "positive"

class TestModelEndpoints:
    """Tests for model endpoints"""
    
    def test_register_model(self, mock_context_provider):
        """Test registering a model"""
        # Configure mock
        mock_context_provider.store.return_value = None
        
        # Test data
        model_data = {
            "model_name": "test_model",
            "model_type": "classification",
            "parameters": {
                "version": "1.0",
                "features": ["sentiment"]
            },
            "metadata": {
                "description": "Test model for sentiment analysis"
            }
        }
        
        # Make request
        response = client.post("/api/mcp/model", json=model_data)
        
        # Verify response
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert "model_id" in result
        assert result["model_id"] == "classification-test_model"
        
        # Verify mock called
        mock_context_provider.store.assert_called_once()
    
    def test_predict(self, mock_context_provider):
        """Test model prediction"""
        # Configure mock to return a model
        model_id = "classification-test_model"
        model_context_id = f"model-{model_id}"
        
        mock_model = {
            "id": model_id,
            "name": "test_model",
            "type": "classification",
            "parameters": {"version": "1.0"}
        }
        
        # Configure retrieval to return the model
        mock_context_provider.retrieve.side_effect = lambda cid: mock_model if cid == model_context_id else None
        
        # Configure prediction ID
        prediction_id = "prediction-123456"
        with patch("mcp_adapter.generate_context_id", return_value=prediction_id):
            # Test data
            predict_data = {
                "model_id": model_id,
                "inputs": {
                    "text": "This is a test input"
                },
                "parameters": {
                    "temperature": 0.7
                }
            }
            
            # Make request
            response = client.post("/api/mcp/predict", json=predict_data)
            
            # Verify response
            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert "prediction" in result
            assert result["prediction"]["id"] == prediction_id
            assert result["prediction"]["model_id"] == model_id
            assert "outputs" in result["prediction"]
