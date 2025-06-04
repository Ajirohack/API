"""
Endpoint Tracking Integration
Provides automatic discovery and registration of API endpoints for monitoring.
"""
import logging
import inspect
from typing import List, Dict, Any, Optional, Callable, Type
from fastapi import FastAPI, APIRouter
from core.endpoint_tracking.registry import get_registry, EndpointStatus

# Setup logger
logger = logging.getLogger("endpoint_tracking.integration")

def autodiscover_endpoints(app: FastAPI) -> None:
    """
    Automatically discover and register FastAPI endpoints with the endpoint registry.
    
    This function scans the FastAPI application and all its routers to find
    endpoints, then registers them with the endpoint tracking registry.
    
    Args:
        app: The FastAPI application to scan
    """
    registry = get_registry()
    
    # Track discovered endpoints to avoid duplicates
    discovered = set()
    
    # Process app routes
    _process_routes(app.routes, "main", discovered, registry)
    
    # Process mounted routers
    for mount in getattr(app, "routes", []):
        if hasattr(mount, "app") and isinstance(mount.app, FastAPI):
            prefix = mount.path or ""
            _process_routes(mount.app.routes, f"mount:{prefix}", discovered, registry)
    
    logger.info(f"Autodiscovered {len(discovered)} endpoints for tracking")

def _process_routes(routes: List[Any], source: str, discovered: set, registry: Any) -> None:
    """
    Process a list of routes and register them with the registry.
    
    Args:
        routes: List of routes to process
        source: Source identifier for the routes
        discovered: Set of already discovered routes to avoid duplicates
        registry: Endpoint registry
    """
    for route in routes:
        # Skip if not a route with path
        if not hasattr(route, "path"):
            continue
            
        # Handle APIRouter (recursively process its routes)
        if isinstance(route, APIRouter):
            _process_routes(route.routes, f"{source}:router", discovered, registry)
            continue
            
        # Regular route
        path = getattr(route, "path", "")
        name = getattr(route, "name", None) or f"endpoint:{path}"
        methods = getattr(route, "methods", ["GET"])
        
        for method in methods:
            endpoint_id = f"{method}:{path}"
            
            # Skip if already discovered
            if endpoint_id in discovered:
                continue
                
            # Get endpoint details from docstring if available
            endpoint_func = getattr(route, "endpoint", None)
            description = None
            if endpoint_func and callable(endpoint_func):
                description = inspect.getdoc(endpoint_func)
                
            # Register endpoint
            registry.register_endpoint(
                endpoint_id=endpoint_id,
                name=f"{method} {path}",
                description=description or f"{method} endpoint for {path}",
                category=source,
                status=EndpointStatus.STARTING,
                metadata={
                    "method": method,
                    "path": path,
                    "source": source
                }
            )
            
            discovered.add(endpoint_id)
