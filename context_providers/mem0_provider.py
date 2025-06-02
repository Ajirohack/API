"""
Mem0 Context Provider Integration
Provides endpoints to interact with mem0 memory/context server.

This module implements production-ready endpoints for:
- Adding memories
- Retrieving memories
- Updating memories
- Searching memories
- Clearing memories
"""
import logging
import os
from fastapi import APIRouter, HTTPException, Query, Body, Depends, Request
from typing import List, Optional, Dict, Any
from mem0 import Memory
import asyncio
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger("api.context_providers.mem0")

router = APIRouter(prefix="/api/context/mem0", tags=["context", "mem0"])

# Global mem0 client
_mem0_client = None

def get_mem0_client():
    """Get or create the mem0 client with proper configuration"""
    global _mem0_client
    
    if _mem0_client is None:
        try:
            # Use environment variables for configuration
            api_key = os.getenv("MEM0_API_KEY")
            base_url = os.getenv("MEM0_BASE_URL", "https://api.mem0.ai")
            collection = os.getenv("MEM0_COLLECTION", "space-default")
            
            # Initialize the client
            _mem0_client = Memory(
                api_key=api_key, 
                base_url=base_url,
                collection=collection
            )
            logger.info("mem0 client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize mem0 client: {str(e)}")
            _mem0_client = None
    
    if _mem0_client is None:
        raise HTTPException(
            status_code=503,
            detail="mem0 service unavailable. Please check configuration."
        )
        
    return _mem0_client

# For backward compatibility
mem0_client = get_mem0_client

@router.get("/memory")
async def get_memories(user_id: str = Query(...)):
    """Retrieve memories for a user from mem0"""
    try:
        memories = mem0_client.get_memories(user_id=user_id)
        return {"user_id": user_id, "memories": memories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"mem0 error: {str(e)}")

@router.post("/memory")
async def add_memory(user_id: str = Query(...), content: str = Query(...)):
    """Add a memory for a user in mem0"""
    try:
        mem0_client.add_memory(user_id=user_id, content=content)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"mem0 error: {str(e)}")

@router.post("/memory/add")
async def add_mem0_memory(user_id: str = Body(...), content: str = Body(...)):
    """Add a memory for a user in mem0 (shared client)"""
    try:
        client = get_mem0_client()
        result = client.add_memory(user_id=user_id, content=content)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"mem0 error: {str(e)}")

@router.post("/memory/update")
async def update_mem0_memory(user_id: str = Body(...), memory_id: str = Body(...), content: str = Body(...)):
    """Update a memory for a user in mem0 (shared client)"""
    try:
        client = get_mem0_client()
        result = client.update_memory(user_id=user_id, memory_id=memory_id, content=content)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"mem0 error: {str(e)}")

@router.get("/memory/search")
async def search_mem0_memory(user_id: str, query: str):
    """Search memories for a user in mem0 (shared client)"""
    try:
        client = get_mem0_client()
        results = client.search_memories(user_id=user_id, query=query)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"mem0 error: {str(e)}")

@router.delete("/memory/clear")
async def clear_mem0_memory(user_id: str):
    """Clear all memories for a user in mem0 (shared client)"""
    try:
        client = get_mem0_client()
        result = client.clear_memories(user_id=user_id)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"mem0 error: {str(e)}")

class ContextProvider:
    """In-memory context provider with basic persistence"""
    
    def __init__(self):
        self._storage: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self._ttl_seconds = 3600  # 1 hour default TTL
    
    async def store(self, context_id: str, context_data: Dict[str, Any]) -> None:
        """Store context with TTL"""
        async with self._lock:
            self._storage[context_id] = {
                "data": context_data,
                "expires_at": datetime.now() + timedelta(seconds=self._ttl_seconds)
            }
    
    async def retrieve(self, context_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve context if it exists and hasn't expired"""
        async with self._lock:
            if context_id not in self._storage:
                return None
            
            context = self._storage[context_id]
            if datetime.now() > context["expires_at"]:
                del self._storage[context_id]
                return None
            
            return context["data"]
    
    async def update(self, context_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update existing context"""
        async with self._lock:
            if context_id not in self._storage:
                return None
            
            context = self._storage[context_id]
            if datetime.now() > context["expires_at"]:
                del self._storage[context_id]
                return None
            
            # Deep merge updates
            updated_data = deep_merge(context["data"], updates)
            context["data"] = updated_data
            context["expires_at"] = datetime.now() + timedelta(seconds=self._ttl_seconds)
            
            return updated_data
    
    async def delete(self, context_id: str) -> bool:
        """Delete context if it exists"""
        async with self._lock:
            if context_id in self._storage:
                del self._storage[context_id]
                return True
            return False
    
    async def cleanup_expired(self) -> None:
        """Remove all expired contexts"""
        async with self._lock:
            now = datetime.now()
            expired = [
                cid for cid, ctx in self._storage.items()
                if now > ctx["expires_at"]
            ]
            for cid in expired:
                del self._storage[cid]

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

# TODO: Extend with more advanced context operations as needed
