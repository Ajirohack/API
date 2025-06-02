"""
Unified Storage API endpoints for Archivist
- Vector search, graph queries, event tracking, and state management
"""
from fastapi import APIRouter, Query
import os

router = APIRouter(tags=["storage"])

# Lazy initialization to avoid startup delays
_storage = None
_qdrant_adapter = None
_neo4j_adapter = None
_redis_adapter = None
_postgres_adapter = None

def get_storage():
    """Get the unified storage layer instance (lazy initialization)."""
    global _storage
    if _storage is None:
        from core.unified_storage import UnifiedStorageLayer
        _storage = UnifiedStorageLayer()
    return _storage

def get_qdrant_adapter():
    """Get the Qdrant adapter instance (lazy initialization)."""
    global _qdrant_adapter
    if _qdrant_adapter is None:
        from core.storage.adapters.qdrant_adapter import QdrantAdapter
        _qdrant_adapter = QdrantAdapter()
    return _qdrant_adapter

def get_neo4j_adapter():
    """Get the Neo4j adapter instance (lazy initialization)."""
    global _neo4j_adapter
    if _neo4j_adapter is None:
        from core.storage.adapters.neo4j_adapter import Neo4jAdapter
        _neo4j_adapter = Neo4jAdapter()
    return _neo4j_adapter

def get_redis_adapter():
    """Get the Redis adapter instance (lazy initialization)."""
    global _redis_adapter
    if _redis_adapter is None:
        from core.storage.adapters.redis_adapter import RedisAdapter
        _redis_adapter = RedisAdapter()
    return _redis_adapter

def get_postgres_adapter():
    """Get the Postgres adapter instance (lazy initialization)."""
    global _postgres_adapter
    if _postgres_adapter is None:
        from core.storage.adapters.postgres_adapter import PostgresAdapter
        _postgres_adapter = PostgresAdapter()
    return _postgres_adapter

# Vector search endpoint (H2OAI/Qdrant)
@router.post("/api/storage/vector_search")
def vector_search(collection: str = Query(...), query_vector: list = Query(...), limit: int = 5):
    # For demo: use Qdrant adapter
    qdrant = QdrantAdapter()
    results = qdrant.search_vectors(collection, query_vector, limit)
    return {"results": results}

# Graph query endpoint (Neo4j)
@router.post("/api/storage/graph_query")
def graph_query(cypher: str = Query(...)):
    neo4j = Neo4jAdapter()
    # For demo: run a cypher query and return results
    results = neo4j.run_query(cypher)
    return {"results": results}

# Event tracking endpoint (Postgres)
@router.post("/api/storage/track_event")
def track_event(event_type: str = Query(...), payload: dict = Query(...)):
    pg = PostgresAdapter(os.getenv("POSTGRES_DSN", ""))
    # For demo: insert event into event_log table
    pg.set("event_log", event_type, payload)
    return {"status": "ok"}

# Cache endpoint (Redis)
@router.post("/api/storage/cache")
def cache_set(key: str = Query(...), value: str = Query(...)):
    redis = RedisAdapter()
    redis.set(key, value)
    return {"status": "ok"}
