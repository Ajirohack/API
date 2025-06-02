"""
Health check API for the system-engine service.
This module provides endpoints for system health monitoring.
"""
from datetime import datetime
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connections.base import db
from config.configuration import config

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    Returns status of the system-engine API service.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": config.environment,
        "service": "system-engine"
    }

@router.get("/health/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check for all system components.
    Checks database, agent system, workflow engine and other critical services.
    """
    checks = []
    is_healthy = True
    
    # Check database connection
    db_status = check_database()
    checks.append(db_status)
    if not db_status["healthy"]:
        is_healthy = False
    
    # Check agent system
    agent_system_status = check_agent_system()
    checks.append(agent_system_status)
    if not agent_system_status["healthy"]:
        is_healthy = False
    
    # Check workflow engine
    workflow_engine_status = check_workflow_engine()
    checks.append(workflow_engine_status)
    if not workflow_engine_status["healthy"]:
        is_healthy = False
    
    # Add more component checks as needed
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "environment": config.environment,
        "service": "system-engine",
        "checks": checks
    }

def check_database() -> Dict[str, Any]:
    """Check database connectivity and status"""
    try:
        # Execute simple query to verify connection
        with db.get_session() as session:
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

def check_agent_system() -> Dict[str, Any]:
    """Check agent system status"""
    # In a real implementation, this would check the agent framework
    # For now, return mock healthy status
    return {
        "component": "agent_system",
        "healthy": True
    }

def check_workflow_engine() -> Dict[str, Any]:
    """Check workflow engine status"""
    # In a real implementation, this would check the workflow engine
    # For now, return mock healthy status
    return {
        "component": "workflow_engine",
        "healthy": True
    }
