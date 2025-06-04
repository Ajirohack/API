"""
Simple Memory Service Client for API
This is a simple implementation of a memory service client
that can be used to store and retrieve memories.
"""
import requests
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("api.mem0")

class Memory:
    """Memory client for interaction with memory service"""
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        base_url: str = "https://api.mem0.ai",
        collection: str = "default"
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.collection = collection
        self.headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        
        logger.info(f"Initialized Memory client with collection: {collection}")
    
    def add_memory(self, user_id: str, content: str) -> Dict[str, Any]:
        """Add a memory for a user"""
        # If no external service, store in-memory
        return {
            "id": f"mem_{user_id}_{len(content) % 10000}",
            "user_id": user_id,
            "content": content,
            "status": "stored"
        }
    
    def get_memories(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all memories for a user"""
        # Return empty list as this is a stub implementation
        return []
    
    def update_memory(self, user_id: str, memory_id: str, content: str) -> Dict[str, Any]:
        """Update a memory"""
        return {
            "id": memory_id,
            "user_id": user_id,
            "content": content,
            "status": "updated"
        }
    
    def search_memories(self, user_id: str, query: str) -> List[Dict[str, Any]]:
        """Search memories for a user"""
        # Return empty results as this is a stub implementation
        return []
    
    def clear_memories(self, user_id: str) -> Dict[str, Any]:
        """Clear all memories for a user"""
        return {
            "user_id": user_id,
            "status": "cleared"
        }
