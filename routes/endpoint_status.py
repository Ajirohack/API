"""
API endpoints for endpoint status tracking
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel

from core.endpoint_tracking.registry import get_registry, EndpointStatus

# Set up logger
logger = logging.getLogger("endpoint_status")

# Create router
router = APIRouter(tags=["endpoint-status"], prefix="/api")


class UpdateEndpointStatusRequest(BaseModel):
    """Request for updating endpoint status"""
    status: EndpointStatus
    comment: Optional[str] = None


class RegisterEndpointRequest(BaseModel):
    """Request for registering a new endpoint"""
    path: str
    method: str
    plugin_name: Optional[str] = None
    description: Optional[str] = None
    status: EndpointStatus = EndpointStatus.PLANNED
    owner: Optional[str] = None
    tags: Optional[List[str]] = None


@router.get("/endpoints")
def list_endpoints(
    plugin_name: Optional[str] = None,
    status: Optional[EndpointStatus] = None,
    tag: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List endpoints with optional filtering
    
    Args:
        plugin_name: Filter by plugin name
        status: Filter by endpoint status
        tag: Filter by tag
    
    Returns:
        List of endpoint info dictionaries
    """
    registry = get_registry()
    return registry.list_endpoints(plugin_name=plugin_name, status=status, tag=tag)


@router.get("/endpoints/status")
def get_endpoints_summary() -> Dict[str, Any]:
    """
    Get endpoint implementation status summary
    
    Returns:
        Summary of endpoint implementation status
    """
    registry = get_registry()
    return registry.get_summary()


@router.get("/endpoints/{method}/{path:path}")
def get_endpoint_status(method: str, path: str) -> Dict[str, Any]:
    """
    Get status of a specific endpoint
    
    Args:
        method: HTTP method
        path: API endpoint path
        
    Returns:
        Endpoint information
    """
    registry = get_registry()
    endpoint = registry.get_endpoint(path=path, method=method)
    
    if endpoint is None:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    return endpoint


@router.post("/endpoints", status_code=201)
def register_endpoint(request: RegisterEndpointRequest) -> Dict[str, str]:
    """
    Register a new API endpoint
    
    Args:
        request: Endpoint registration request
        
    Returns:
        Success message
    """
    registry = get_registry()
    registry.register_endpoint(
        path=request.path,
        method=request.method,
        plugin_name=request.plugin_name,
        description=request.description,
        status=request.status,
        owner=request.owner,
        tags=request.tags
    )
    
    return {"status": "success", "message": "Endpoint registered successfully"}


@router.put("/endpoints/{method}/{path:path}")
def update_endpoint_status(
    method: str, 
    path: str, 
    request: UpdateEndpointStatusRequest
) -> Dict[str, str]:
    """
    Update status of an endpoint
    
    Args:
        method: HTTP method
        path: API endpoint path
        request: Status update request
        
    Returns:
        Success message
    """
    registry = get_registry()
    result = registry.update_status(
        path=path,
        method=method,
        status=request.status,
        comment=request.comment
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    return {
        "status": "success",
        "message": f"Endpoint status updated to {request.status}"
    }
