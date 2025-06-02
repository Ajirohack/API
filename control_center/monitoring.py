"""
System monitoring API for SpaceNew platform.
Provides health check, metrics collection and system status endpoints.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import psutil
import platform
from fastapi import APIRouter, Depends, HTTPException, status
import os
import time

from api.models import DataResponse
from api.auth import get_current_active_user, get_current_admin_user
from database.connection import get_db_session
from database.models.user import User
from database.models.user import User as DBUser
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

def get_redis_client():
    """Get Redis client with lazy connection"""
    try:
        return redis.Redis.from_url(REDIS_URL, socket_connect_timeout=1, socket_timeout=1)
    except Exception:
        return None

router = APIRouter(prefix="/api/control-center/monitoring", tags=["monitoring"])

class ServiceStatus(str, Enum):
    """Status values for services"""
    UP = "up"
    DOWN = "down"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"

class HealthStatus(str, Enum):
    """Overall health status values"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@router.get("/health", response_model=DataResponse)
async def health_check(current_user: User = Depends(get_current_active_user)):
    """
    Get overall system health status.
    Checks all critical components and services.
    """
    start_time = time.time()
    
    # Check database connectivity
    db_status = check_database()
    
    # Check plugin status
    plugin_statuses = check_all_plugins()
    
    # Check overall system resources
    system_status = check_system_resources()
    
    # Calculate overall health
    overall_health = calculate_overall_health(
        db_status=db_status,
        plugin_statuses=plugin_statuses,
        system_status=system_status
    )
    
    # Response time calculation
    response_time_ms = int((time.time() - start_time) * 1000)
    
    return DataResponse(
        status="success",
        message="Health check completed",
        data={
            "timestamp": datetime.now().isoformat(),
            "status": overall_health,
            "response_time_ms": response_time_ms,
            "components": {
                "database": db_status,
                "plugins": plugin_statuses,
                "system": system_status
            }
        }
    )

@router.get("/metrics", response_model=DataResponse)
async def system_metrics(current_user: User = Depends(get_current_active_user)):
    """
    Get detailed system metrics.
    Includes CPU, memory, disk and network usage.
    """
    # Get memory info
    mem = psutil.virtual_memory()
    mem_info = {
        "total": mem.total,
        "available": mem.available,
        "used": mem.used,
        "percent": mem.percent
    }
    
    # Get CPU info
    cpu_info = {
        "percent": psutil.cpu_percent(interval=0.1),
        "count": psutil.cpu_count(logical=True),
        "physical_count": psutil.cpu_count(logical=False)
    }
    
    # Get disk info
    disk = psutil.disk_usage("/")
    disk_info = {
        "total": disk.total,
        "used": disk.used,
        "free": disk.free,
        "percent": disk.percent
    }
    
    # Get process info
    process = psutil.Process(os.getpid())
    process_info = {
        "memory_info": process.memory_info()._asdict(),
        "cpu_percent": process.cpu_percent(),
        "create_time": datetime.fromtimestamp(process.create_time()).isoformat(),
        "status": process.status()
    }
    
    # Get OS info
    os_info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version()
    }
    
    return DataResponse(
        status="success",
        message="System metrics retrieved",
        data={
            "timestamp": datetime.now().isoformat(),
            "memory": mem_info,
            "cpu": cpu_info,
            "disk": disk_info,
            "process": process_info,
            "os": os_info
        }
    )

@router.get("/plugins", response_model=DataResponse)
async def plugin_status(current_user: User = Depends(get_current_active_user)):
    """
    Get status of all plugins.
    Shows which plugins are active and their health status.
    """
    statuses = check_all_plugins()
    
    return DataResponse(
        status="success",
        message="Plugin status retrieved",
        data=statuses
    )

@router.post("/maintenance-mode", response_model=DataResponse)
async def set_maintenance_mode(
    enable: bool,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Enable or disable system maintenance mode.
    When in maintenance mode, only admin users can access the system.
    Requires admin privileges.
    """
    # In a real implementation, this would set a flag in the database
    # or config that all services would check
    
    return DataResponse(
        status="success",
        message=f"Maintenance mode {'enabled' if enable else 'disabled'}",
        data={
            "maintenance_mode": enable,
            "timestamp": datetime.now().isoformat()
        }
    )

@router.get("/deep-health", response_model=DataResponse)
async def deep_health_check(current_user: User = Depends(get_current_admin_user)):
    """
    Deep health check: DB, Redis, plugin, and external API status.
    """
    db_status = check_database()
    plugin_statuses = check_all_plugins()
    system_status = check_system_resources()
    # Redis check
    try:
        redis_client = get_redis_client()
        if redis_client:
            redis_client.ping()
            redis_status = {"status": ServiceStatus.UP}
        else:
            redis_status = {"status": ServiceStatus.DOWN, "error": "Connection failed"}
    except Exception as e:
        redis_status = {"status": ServiceStatus.DOWN, "error": str(e)}
    # External API check (example: MIS)
    import httpx
    mis_status = {"status": ServiceStatus.UNKNOWN}
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            resp = await client.get(os.getenv("MIS_BACKEND_URL", "http://localhost:3000") + "/health")
            if resp.status_code == 200:
                mis_status = {"status": ServiceStatus.UP}
            else:
                mis_status = {"status": ServiceStatus.DEGRADED, "code": resp.status_code}
    except Exception as e:
        mis_status = {"status": ServiceStatus.DOWN, "error": str(e)}
    return DataResponse(
        status="success",
        message="Deep health check completed",
        data={
            "timestamp": datetime.now().isoformat(),
            "database": db_status,
            "plugins": plugin_statuses,
            "system": system_status,
            "redis": redis_status,
            "mis": mis_status
        }
    )

@router.get("/business-metrics", response_model=DataResponse)
async def business_metrics(current_user: User = Depends(get_current_admin_user)):
    """
    Business metrics: user count, active users, plugin usage, etc.
    """
    db = next(get_db_session())
    user_count = db.query(DBUser).count()
    # Example: count of active users in last 24h
    from datetime import timedelta
    since = datetime.now() - timedelta(days=1)
    active_users = db.query(DBUser).filter(DBUser.last_active >= since).count()
    # Example: plugin usage (stub)
    plugin_usage = {p["id"]: 0 for p in check_all_plugins()}
    return DataResponse(
        status="success",
        message="Business metrics collected",
        data={
            "timestamp": datetime.now().isoformat(),
            "user_count": user_count,
            "active_users_24h": active_users,
            "plugin_usage": plugin_usage
        }
    )

def check_database() -> Dict[str, Any]:
    """Check database connectivity and status"""
    # In a real implementation, this would actually check the database
    # using SQLAlchemy or similar
    
    return {
        "status": ServiceStatus.UP,
        "latency_ms": 5,
        "connections": 10,
        "last_checked": datetime.now().isoformat()
    }

def check_all_plugins() -> List[Dict[str, Any]]:
    """Check status of all plugins"""
    plugin_statuses = []
    
    # Get all plugin IDs
    plugin_ids = registry.get_all_plugins()
    enabled_plugins = set(registry.get_enabled_plugins())
    
    # Get status for each plugin
    for plugin_id in plugin_ids:
        manifest = registry.get_plugin_manifest(plugin_id)
        if manifest:
            plugin_statuses.append({
                "id": plugin_id,
                "name": manifest.name,
                "version": manifest.version,
                "status": ServiceStatus.UP if plugin_id in enabled_plugins else ServiceStatus.DOWN,
                "capabilities": [c.value for c in manifest.capabilities],
                "last_checked": datetime.now().isoformat()
            })
    
    return plugin_statuses

def check_system_resources() -> Dict[str, Any]:
    """Check system resource utilization"""
    mem = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=0.1)
    
    # Determine status based on resource utilization
    status = ServiceStatus.UP
    if mem.percent > 90 or cpu_percent > 90:
        status = ServiceStatus.DEGRADED
    
    return {
        "status": status,
        "memory_percent": mem.percent,
        "cpu_percent": cpu_percent,
        "last_checked": datetime.now().isoformat()
    }

def calculate_overall_health(
    db_status: Dict[str, Any],
    plugin_statuses: List[Dict[str, Any]],
    system_status: Dict[str, Any]
) -> HealthStatus:
    """Calculate overall system health based on component status"""
    # Check database
    if db_status["status"] == ServiceStatus.DOWN:
        return HealthStatus.UNHEALTHY
    
    # Check system resources
    if system_status["status"] == ServiceStatus.DOWN:
        return HealthStatus.UNHEALTHY
    
    # Count plugin status
    total_plugins = len(plugin_statuses)
    if total_plugins == 0:
        # No plugins is a degraded state
        return HealthStatus.DEGRADED
    
    down_plugins = sum(1 for p in plugin_statuses if p["status"] == ServiceStatus.DOWN)
    down_percentage = down_plugins / total_plugins if total_plugins > 0 else 0
    
    # Determine overall health
    if down_percentage > 0.5:
        return HealthStatus.UNHEALTHY
    elif down_percentage > 0.2 or db_status["status"] == ServiceStatus.DEGRADED or system_status["status"] == ServiceStatus.DEGRADED:
        return HealthStatus.DEGRADED
    else:
        return HealthStatus.HEALTHY
