"""
Health check endpoints for service monitoring.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict
import psutil
import platform

from models import SuccessResponse
from database.connection import get_db_session
from database.models import FMTTemplate

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/", response_model=SuccessResponse)
async def health_check():
    """Basic health check endpoint"""
    return SuccessResponse(
        status="success",
        message="Service is healthy"
    )

@router.get("/details", response_model=Dict)
async def detailed_health_check(db: Session = Depends(get_db_session)):
    """Detailed health check with system metrics"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    # System metrics
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Count database entities
    # character_count = db.query(CharacterProfile).count()  # TODO: Implement CharacterProfile model
    fmt_template_count = db.query(FMTTemplate).count()
    
    # Check if Diego exists
    # diego_exists = db.query(CharacterProfile).filter(
    #     CharacterProfile.name == "Diego Camilleri"
    # ).count() > 0
    
    # Check Diego's templates if he exists
    # diego_template_count = 0
    # if diego_exists:
    #     diego = db.query(CharacterProfile).filter(
    #         CharacterProfile.name == "Diego Camilleri"
    #     ).first()
    #     
    #     if diego:
    #         diego_template_count = db.query(FMTTemplate).filter(
    #             FMTTemplate.character_id == diego.id
    #         ).count()
    
    # Get endpoint implementation status
    endpoint_status = {}
    try:
        from core.endpoint_tracking.registry import get_registry
        registry = get_registry()
        endpoint_status = registry.get_summary()
    except Exception as e:
        endpoint_status = {"error": str(e)}
    
    return {
        "status": "success",
        "system": {
            "platform": platform.system(),
            "version": platform.version(),
            "python_version": platform.python_version(),
        },
        "resources": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_used_percent": memory.percent,
            "disk_used_percent": disk.percent,
        },
        "database": {
            "status": db_status
        },
        "character_stats": {
            "total_characters": 0,  # TODO: Implement CharacterProfile model
            "total_fmt_templates": fmt_template_count,
            "default_character": {
                "exists": False,  # TODO: Implement CharacterProfile model
                "name": None,
                "template_count": 0
            }
        },
        "endpoint_implementation_status": endpoint_status
    }
