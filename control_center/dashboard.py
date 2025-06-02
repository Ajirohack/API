"""
Dashboard API for SpaceNew Control Center.
Provides endpoints for dashboard data and visualization.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from api.models import DataResponse, PaginationParams
from api.auth import get_current_active_user, get_current_admin_user
from database.models.user import User
from core.plugin_system.registry import registry

router = APIRouter(prefix="/api/control-center/dashboard", tags=["dashboard"])

@router.get("/", response_model=DataResponse)
async def get_dashboard(current_user: User = Depends(get_current_active_user)):
    """
    Get main dashboard data.
    Returns summary statistics and status information.
    """
    # Get plugin statistics
    plugin_stats = get_plugin_statistics()
    
    # Get system statistics
    system_stats = get_system_statistics()
    
    # Get recent activity
    recent_activity = get_recent_activity(limit=5)
    
    return DataResponse(
        status="success",
        message="Dashboard data retrieved",
        data={
            "timestamp": datetime.now().isoformat(),
            "plugin_stats": plugin_stats,
            "system_stats": system_stats,
            "recent_activity": recent_activity
        }
    )

@router.get("/plugins", response_model=DataResponse)
async def get_plugin_dashboard(current_user: User = Depends(get_current_active_user)):
    """
    Get plugin dashboard data.
    Returns detailed plugin statistics and status.
    """
    return DataResponse(
        status="success",
        message="Plugin dashboard data retrieved",
        data={
            "timestamp": datetime.now().isoformat(),
            "plugins": get_plugin_detailed_status(),
            "statistics": get_plugin_statistics()
        }
    )

@router.get("/system", response_model=DataResponse)
async def get_system_dashboard(current_user: User = Depends(get_current_active_user)):
    """
    Get system dashboard data.
    Returns detailed system statistics and resource usage.
    """
    # Get historical CPU usage (simulated)
    cpu_history = [
        {"timestamp": (datetime.now() - timedelta(minutes=i)).isoformat(), "value": 50 + i % 20}
        for i in range(60, 0, -5)
    ]
    
    # Get historical memory usage (simulated)
    memory_history = [
        {"timestamp": (datetime.now() - timedelta(minutes=i)).isoformat(), "value": 60 + i % 15}
        for i in range(60, 0, -5)
    ]
    
    # Get historical API requests (simulated)
    request_history = [
        {"timestamp": (datetime.now() - timedelta(minutes=i)).isoformat(), "value": 100 + (i % 50)}
        for i in range(60, 0, -5)
    ]
    
    return DataResponse(
        status="success",
        message="System dashboard data retrieved",
        data={
            "timestamp": datetime.now().isoformat(),
            "current": get_system_statistics(),
            "history": {
                "cpu": cpu_history,
                "memory": memory_history,
                "requests": request_history
            }
        }
    )

@router.get("/activity", response_model=DataResponse)
async def get_activity_log(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get system activity log.
    Returns a paginated list of system activities and events.
    """
    # Get activity log (simulated)
    activities = get_recent_activity(limit=pagination.page_size, offset=(pagination.page - 1) * pagination.page_size)
    
    return DataResponse(
        status="success",
        message="Activity log retrieved",
        data={
            "timestamp": datetime.now().isoformat(),
            "activities": activities,
            "pagination": {
                "page": pagination.page,
                "page_size": pagination.page_size,
                "total": 100  # Simulated total count
            }
        }
    )

def get_plugin_statistics() -> Dict[str, Any]:
    """Get plugin statistics"""
    # Get all plugin IDs
    plugin_ids = registry.get_all_plugins()
    enabled_plugins = set(registry.get_enabled_plugins())
    
    return {
        "total": len(plugin_ids),
        "enabled": len(enabled_plugins),
        "disabled": len(plugin_ids) - len(enabled_plugins),
        "by_capability": {
            "data_processing": 2,  # Simulated data
            "user_interface": 3,
            "workflow": 1,
            "integration": 2
        }
    }

def get_plugin_detailed_status() -> List[Dict[str, Any]]:
    """Get detailed status for all plugins"""
    plugin_statuses = []
    
    # Get all plugin IDs
    plugin_ids = registry.get_all_plugins()
    enabled_plugins = set(registry.get_enabled_plugins())
    
    # Get status for each plugin
    for plugin_id in plugin_ids:
        manifest = registry.get_plugin_manifest(plugin_id)
        if manifest:
            # Simulated usage statistics
            plugin_statuses.append({
                "id": plugin_id,
                "name": manifest.name,
                "version": manifest.version,
                "enabled": plugin_id in enabled_plugins,
                "api_calls_today": 120 + hash(plugin_id) % 500,  # Simulated data
                "errors_today": hash(plugin_id) % 10,
                "avg_response_time_ms": 50 + hash(plugin_id) % 200,
                "capabilities": [c.value for c in manifest.capabilities]
            })
    
    return plugin_statuses

def get_system_statistics() -> Dict[str, Any]:
    """Get system statistics"""
    return {
        "uptime_hours": 72,  # Simulated data
        "cpu_usage_percent": 45,
        "memory_usage_percent": 60,
        "disk_usage_percent": 35,
        "active_users": 15,
        "api_requests_per_minute": 120,
        "plugin_api_calls_today": 5280,
        "errors_today": 12
    }

def get_recent_activity(limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """Get recent system activity"""
    # Simulated activity data
    activity_types = [
        "user_login",
        "plugin_enabled",
        "plugin_disabled",
        "system_alert",
        "workflow_executed",
        "api_error"
    ]
    
    activities = []
    for i in range(offset, offset + limit):
        idx = i % len(activity_types)
        activities.append({
            "id": f"act-{i}",
            "timestamp": (datetime.now() - timedelta(minutes=i*5)).isoformat(),
            "type": activity_types[idx],
            "summary": f"Activity {activity_types[idx]} occurred",
            "details": {
                "user_id": "usr-123" if idx == 0 else None,
                "plugin_id": f"plugin-{idx}" if idx in [1, 2] else None,
                "workflow_id": f"workflow-{idx}" if idx == 4 else None,
                "severity": "high" if idx in [3, 5] else "normal"
            }
        })
    
    return activities
