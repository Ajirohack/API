"""
Endpoint Registry for tracking status of API endpoints.
- Provides centralized registry of endpoint health and status
- Allows services to report their health status
- Used by health endpoints to aggregate system status
"""
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import time
import logging
from datetime import datetime
import threading

# Setup logger
logger = logging.getLogger("endpoint_registry")

class EndpointStatus(str, Enum):
    """Status of an endpoint"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"
    STARTING = "starting"
    MAINTENANCE = "maintenance"
    PLANNED = "planned"


class EndpointInfo:
    """Information about an endpoint's status and health"""
    
    def __init__(
        self,
        endpoint_id: str,
        name: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        status: EndpointStatus = EndpointStatus.UNKNOWN,
        last_checked: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.endpoint_id = endpoint_id
        self.name = name
        self.description = description or f"Endpoint {name}"
        self.category = category or "uncategorized"
        self.status = status
        self.last_checked = last_checked or time.time()
        self.metadata = metadata or {}
        self.history: List[Dict[str, Any]] = []
        self.max_history_size = 100  # Keep last 100 status changes
    
    def update_status(self, status: EndpointStatus, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Update the status of this endpoint.
        
        Args:
            status: New status
            metadata: Optional metadata about the status change
        """
        # Don't record if status hasn't changed
        if status == self.status:
            self.last_checked = time.time()
            return
            
        # Record the previous status in history
        self.history.append({
            "previous_status": self.status,
            "new_status": status,
            "timestamp": time.time(),
            "metadata": self.metadata.copy()
        })
        
        # Trim history if needed
        if len(self.history) > self.max_history_size:
            self.history = self.history[-self.max_history_size:]
            
        # Update current status
        self.status = status
        self.last_checked = time.time()
        
        if metadata:
            self.metadata.update(metadata)
            
        logger.info(f"Endpoint {self.name} status changed to {status}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this endpoint info to a dictionary.
        
        Returns:
            Dictionary representation of this endpoint info
        """
        return {
            "endpoint_id": self.endpoint_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "status": self.status,
            "last_checked": self.last_checked,
            "last_checked_formatted": datetime.fromtimestamp(self.last_checked).strftime("%Y-%m-%d %H:%M:%S"),
            "metadata": self.metadata,
            "history_count": len(self.history)
        }


class EndpointRegistry:
    """Registry for tracking endpoint status"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern to ensure only one registry exists"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EndpointRegistry, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        """Initialize the registry if not already initialized"""
        if self._initialized:
            return
            
        self._endpoints: Dict[str, EndpointInfo] = {}
        self._lock = threading.RLock()
        self._initialized = True
        logger.info("Endpoint registry initialized")
    
    def register_endpoint(
        self,
        endpoint_id: str,
        name: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        status: EndpointStatus = EndpointStatus.STARTING,
        metadata: Optional[Dict[str, Any]] = None
    ) -> EndpointInfo:
        """
        Register an endpoint with the registry.
        
        Args:
            endpoint_id: Unique identifier for the endpoint
            name: Human-readable name
            description: Optional description
            category: Category for grouping endpoints
            status: Initial status
            metadata: Additional metadata
            
        Returns:
            The created endpoint info
        """
        with self._lock:
            if endpoint_id in self._endpoints:
                logger.warning(f"Endpoint {endpoint_id} already registered, updating info")
                self._endpoints[endpoint_id].name = name
                if description:
                    self._endpoints[endpoint_id].description = description
                if category:
                    self._endpoints[endpoint_id].category = category
                if metadata:
                    self._endpoints[endpoint_id].metadata.update(metadata)
                return self._endpoints[endpoint_id]
            
            endpoint = EndpointInfo(
                endpoint_id=endpoint_id,
                name=name,
                description=description,
                category=category,
                status=status,
                metadata=metadata
            )
            self._endpoints[endpoint_id] = endpoint
            logger.info(f"Registered endpoint {endpoint_id} ({name}) with status {status}")
            return endpoint
    
    def update_status(
        self,
        endpoint_id: str,
        status: EndpointStatus,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update the status of an endpoint.
        
        Args:
            endpoint_id: ID of the endpoint to update
            status: New status
            metadata: Optional metadata about the status change
        
        Raises:
            KeyError: If the endpoint is not registered
        """
        with self._lock:
            if endpoint_id not in self._endpoints:
                raise KeyError(f"Endpoint {endpoint_id} not registered")
            
            self._endpoints[endpoint_id].update_status(status, metadata)
    
    def get_endpoint(self, endpoint_id: str) -> Optional[EndpointInfo]:
        """
        Get information about an endpoint.
        
        Args:
            endpoint_id: ID of the endpoint
            
        Returns:
            Endpoint info, or None if not found
        """
        with self._lock:
            return self._endpoints.get(endpoint_id)
    
    def get_all_endpoints(self) -> Dict[str, EndpointInfo]:
        """
        Get all registered endpoints.
        
        Returns:
            Dictionary of endpoint ID to endpoint info
        """
        with self._lock:
            return self._endpoints.copy()
    
    def get_endpoints_by_status(self, status: Union[EndpointStatus, List[EndpointStatus]]) -> Dict[str, EndpointInfo]:
        """
        Get all endpoints with a specific status.
        
        Args:
            status: Status or list of statuses to filter by
            
        Returns:
            Dictionary of endpoint ID to endpoint info
        """
        with self._lock:
            if isinstance(status, list):
                return {
                    endpoint_id: endpoint
                    for endpoint_id, endpoint in self._endpoints.items()
                    if endpoint.status in status
                }
            else:
                return {
                    endpoint_id: endpoint
                    for endpoint_id, endpoint in self._endpoints.items()
                    if endpoint.status == status
                }
    
    def get_endpoints_by_category(self, category: str) -> Dict[str, EndpointInfo]:
        """
        Get all endpoints in a specific category.
        
        Args:
            category: Category to filter by
            
        Returns:
            Dictionary of endpoint ID to endpoint info
        """
        with self._lock:
            return {
                endpoint_id: endpoint
                for endpoint_id, endpoint in self._endpoints.items()
                if endpoint.category == category
            }
    
    def get_status_summary(self) -> Dict[str, int]:
        """
        Get a summary of endpoint statuses.
        
        Returns:
            Dictionary of status to count
        """
        with self._lock:
            summary = {status: 0 for status in EndpointStatus}
            for endpoint in self._endpoints.values():
                summary[endpoint.status] += 1
            return summary


# Global registry instance
_registry = None


def get_registry() -> EndpointRegistry:
    """
    Get the global endpoint registry instance.
    
    Returns:
        Global endpoint registry
    """
    global _registry
    if _registry is None:
        _registry = EndpointRegistry()
    return _registry
