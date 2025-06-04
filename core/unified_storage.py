"""
Unified Storage Layer for Space-0.2
Provides a consistent API for accessing different storage backends
"""
import logging
import os
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class UnifiedStorageLayer:
    """
    A unified storage layer that provides a consistent API for all storage backends
    """
    
    def __init__(self):
        """Initialize the unified storage layer"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing unified storage layer")
        
        # Storage adapters will be lazy-loaded when needed
        self._qdrant = None
        self._neo4j = None
        self._redis = None
        self._postgres = None
    
    def get_qdrant(self):
        """Get the Qdrant adapter"""
        if self._qdrant is None:
            from core.storage.adapters.qdrant_adapter import QdrantAdapter
            self._qdrant = QdrantAdapter()
        return self._qdrant
    
    def get_neo4j(self):
        """Get the Neo4j adapter"""
        if self._neo4j is None:
            from core.storage.adapters.neo4j_adapter import Neo4jAdapter
            self._neo4j = Neo4jAdapter()
        return self._neo4j
    
    def get_redis(self):
        """Get the Redis adapter"""
        if self._redis is None:
            from core.storage.adapters.redis_adapter import RedisAdapter
            self._redis = RedisAdapter()
        return self._redis
    
    def get_postgres(self):
        """Get the Postgres adapter"""
        if self._postgres is None:
            from core.storage.adapters.postgres_adapter import PostgresAdapter
            self._postgres = PostgresAdapter()
        return self._postgres
        
    def search_vectors(self, collection: str, query_vector: List[float], limit: int = 5) -> List[Dict]:
        """Search for vectors in a collection"""
        return self.get_qdrant().search_vectors(collection, query_vector, limit)
    
    def run_graph_query(self, query: str) -> List[Dict]:
        """Run a graph query"""
        return self.get_neo4j().run_query(query)
    
    def set_cache(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set a cache value"""
        return self.get_redis().set(key, value, ttl)
    
    def get_cache(self, key: str) -> Any:
        """Get a cache value"""
        return self.get_redis().get(key)
    
    def store_event(self, event_type: str, payload: Dict):
        """Store an event in the database"""
        return self.get_postgres().set("event_log", event_type, payload)
