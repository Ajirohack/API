"""
API Key Management Routes
Provides endpoints for managing external service API keys and integrations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from database.connection import get_db_session
from api.services.api_key_service import APIKeyService, INTEGRATION_DEFINITIONS
from api.models.api_keys import APIKeyManager, IntegrationConfig

router = APIRouter(prefix="/integrations", tags=["integrations"])


# Pydantic models
class APIKeyCreate(BaseModel):
    service_name: str = Field(..., description="Name of the service (e.g., 'openai', 'anthropic')")
    service_category: str = Field(..., description="Category of service (e.g., 'ai_models', 'search', 'storage')")
    api_key: str = Field(..., description="API key for the service")
    configuration: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional configuration")
    description: Optional[str] = Field(None, description="Description of the API key")


class APIKeyResponse(BaseModel):
    id: str
    service_name: str
    service_category: str
    description: Optional[str]
    has_key: bool
    configuration: Dict[str, Any]
    created_at: str
    updated_at: str


class IntegrationStatus(BaseModel):
    integration_name: str
    enabled: bool
    ready: bool
    required_keys: Dict[str, bool]
    configuration: Dict[str, Any]


class EnvironmentConfig(BaseModel):
    environment: str = Field(default="production")
    include_comments: bool = Field(default=True)


def get_db():
    """Get database session for API routes"""
    return next(get_db_session())


@router.post("/api-keys", response_model=Dict[str, Any])
async def create_api_key(
    api_key_data: APIKeyCreate,
    db: Session = Depends(get_db)
):
    """Create or update an API key for a service"""
    try:
        service = APIKeyService(db)
        
        api_key = service.create_api_key(
            service_name=api_key_data.service_name,
            service_category=api_key_data.service_category,
            api_key=api_key_data.api_key,
            configuration=api_key_data.configuration,
            description=api_key_data.description
        )
        
        return {
            "success": True,
            "message": f"API key for {api_key_data.service_name} created/updated successfully",
            "service_name": api_key.service_name,
            "service_category": api_key.service_category
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating API key: {str(e)}"
        )


@router.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all configured API keys (without exposing actual keys)"""
    try:
        service = APIKeyService(db)
        keys = service.list_api_keys(category=category)
        
        return [
            APIKeyResponse(
                id=key["id"],
                service_name=key["service_name"],
                service_category=key["service_category"],
                description=key["description"],
                has_key=key["has_key"],
                configuration=key["configuration"],
                created_at=key["created_at"].isoformat() if key["created_at"] else "",
                updated_at=key["updated_at"].isoformat() if key["updated_at"] else ""
            )
            for key in keys
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing API keys: {str(e)}"
        )


@router.delete("/api-keys/{service_name}")
async def delete_api_key(
    service_name: str,
    db: Session = Depends(get_db)
):
    """Delete an API key for a service"""
    try:
        service = APIKeyService(db)
        success = service.delete_api_key(service_name)
        
        if success:
            return {"success": True, "message": f"API key for {service_name} deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"API key for {service_name} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting API key: {str(e)}"
        )


@router.get("/status", response_model=Dict[str, IntegrationStatus])
async def get_integration_status(db: Session = Depends(get_db)):
    """Get status of all integrations"""
    try:
        service = APIKeyService(db)
        status = service.get_integration_status()
        
        return {
            name: IntegrationStatus(
                integration_name=name,
                enabled=data["enabled"],
                ready=data["ready"],
                required_keys=data["required_keys"],
                configuration=data["configuration"]
            )
            for name, data in status.items()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting integration status: {str(e)}"
        )


@router.post("/integrations/{integration_name}/enable")
async def enable_integration(
    integration_name: str,
    db: Session = Depends(get_db)
):
    """Enable an integration"""
    try:
        service = APIKeyService(db)
        success = service.enable_integration(integration_name)
        
        if success:
            return {"success": True, "message": f"Integration {integration_name} enabled"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Integration {integration_name} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enabling integration: {str(e)}"
        )


@router.post("/integrations/{integration_name}/disable")
async def disable_integration(
    integration_name: str,
    db: Session = Depends(get_db)
):
    """Disable an integration"""
    try:
        service = APIKeyService(db)
        success = service.disable_integration(integration_name)
        
        if success:
            return {"success": True, "message": f"Integration {integration_name} disabled"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Integration {integration_name} not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error disabling integration: {str(e)}"
        )


@router.get("/definitions")
async def get_integration_definitions():
    """Get available integration definitions"""
    return {
        "integrations": INTEGRATION_DEFINITIONS,
        "categories": {
            "ai_models": [
                "openai", "anthropic", "groq", "perplexity"
            ],
            "search": [
                "google_search", "bing_search", "brave_search", "serpapi", "tavily_search"
            ],
            "storage": [
                "azure_storage"
            ],
            "web_tools": [
                "firecrawl"
            ]
        }
    }


@router.post("/initialize")
async def initialize_integrations(db: Session = Depends(get_db)):
    """Initialize all predefined integrations"""
    try:
        service = APIKeyService(db)
        
        initialized = []
        for integration_name, config in INTEGRATION_DEFINITIONS.items():
            integration_config = service.create_integration_config(
                integration_name=integration_name,
                required_keys=config["required_keys"],
                environment_mappings=config["environment_mappings"],
                configuration=config["configuration"]
            )
            initialized.append(integration_name)
        
        return {
            "success": True,
            "message": "Integrations initialized successfully",
            "initialized": initialized
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initializing integrations: {str(e)}"
        )


@router.post("/generate-env", response_model=Dict[str, Any])
async def generate_environment_file(
    config: EnvironmentConfig = Body(...),
    db: Session = Depends(get_db)
):
    """Generate environment file with all configured API keys"""
    try:
        service = APIKeyService(db)
        env_content = service.generate_env_file(environment=config.environment)
        
        return {
            "success": True,
            "environment": config.environment,
            "content": env_content,
            "message": f"Environment file generated for {config.environment}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating environment file: {str(e)}"
        )


@router.post("/bulk-upload")
async def bulk_upload_api_keys(
    keys: List[APIKeyCreate],
    db: Session = Depends(get_db)
):
    """Upload multiple API keys at once"""
    try:
        service = APIKeyService(db)
        
        results = []
        for key_data in keys:
            try:
                api_key = service.create_api_key(
                    service_name=key_data.service_name,
                    service_category=key_data.service_category,
                    api_key=key_data.api_key,
                    configuration=key_data.configuration,
                    description=key_data.description
                )
                results.append({
                    "service_name": key_data.service_name,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "service_name": key_data.service_name,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "success": True,
            "message": f"Processed {len(keys)} API keys",
            "results": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading API keys: {str(e)}"
        )


@router.get("/health")
async def integration_health_check(db: Session = Depends(get_db)):
    """Health check for integration system"""
    try:
        service = APIKeyService(db)
        status = service.get_integration_status()
        
        total_integrations = len(status)
        enabled_integrations = len([s for s in status.values() if s["enabled"]])
        ready_integrations = len([s for s in status.values() if s["ready"]])
        
        return {
            "status": "healthy",
            "total_integrations": total_integrations,
            "enabled_integrations": enabled_integrations,
            "ready_integrations": ready_integrations,
            "health_score": ready_integrations / total_integrations if total_integrations > 0 else 0
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
