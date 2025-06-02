"""
Health check API for the SpaceNew project.
This module provides endpoints for system health monitoring.
"""
from datetime import datetime
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db_session
from config.configuration import config
import psycopg2
import redis

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    Returns status of the API service.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": config.environment,
        "service": "frontend-engine"
    }

@router.get("/health/detailed")
async def detailed_health_check(session: Session = Depends(get_db_session)) -> Dict[str, Any]:
    """
    Detailed health check for all system components.
    Checks database, Redis, and other critical services.
    """
    checks = []
    is_healthy = True
    
    # Check database connection
    db_status = check_database(session)
    checks.append(db_status)
    if not db_status["healthy"]:
        is_healthy = False
    
    # Check Redis connection
    redis_status = check_redis()
    checks.append(redis_status)
    if not redis_status["healthy"]:
        is_healthy = False
    
    # Add more component checks here as needed
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "environment": config.environment,
        "service": "frontend-engine",
        "checks": checks
    }

def check_database(session: Session) -> Dict[str, Any]:
    """Check database connectivity and status"""
    try:
        # Execute simple query to verify connection
        result = session.execute("SELECT 1").fetchone()
        if result and result[0] == 1:
            return {
                "component": "database",
                "healthy": True,
                "latency_ms": None  # Could add timing here
            }
        return {
            "component": "database",
            "healthy": False,
            "error": "Query returned unexpected result"
        }
    except Exception as e:
        return {
            "component": "database",
            "healthy": False,
            "error": str(e)
        }

def check_redis() -> Dict[str, Any]:
    """Check Redis connectivity and status"""
    try:
        # Parse Redis URL from config
        redis_url = config.get("redis_url", "redis://redis:6379/0")
        if redis_url.startswith("redis://"):
            # Strip redis:// prefix
            host_port_db = redis_url[8:]
            
            # Parse host, port, db
            if "/" in host_port_db:
                host_port, db = host_port_db.rsplit("/", 1)
            else:
                host_port, db = host_port_db, "0"
                
            # Parse host, port
            if ":" in host_port:
                host, port = host_port.split(":", 1)
                port = int(port)
            else:
                host, port = host_port, 6379
                
            # Connect to Redis
            r = redis.Redis(host=host, port=port, db=int(db))
            if r.ping():
                return {
                    "component": "redis",
                    "healthy": True
                }
        
        return {
            "component": "redis",
            "healthy": False,
            "error": "Failed to ping Redis"
        }
    except Exception as e:
        return {
            "component": "redis",
            "healthy": False,
            "error": str(e)
        }
