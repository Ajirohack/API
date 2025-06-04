"""
Health Utilities for System Monitoring
- Provides system health status information
- Monitors plugin health and status
"""
from typing import Dict, Any, List
import time
import psutil
import platform
import os
from datetime import datetime

# Mock plugin registry for demonstration
PLUGIN_REGISTRY = {
    "fmt_engine": {
        "name": "FMT Engine",
        "version": "0.1.0",
        "status": "active",
        "last_check": time.time()
    },
    "storage_adapter": {
        "name": "Storage Adapter",
        "version": "0.1.0",
        "status": "active",
        "last_check": time.time()
    },
    "conversation_engine": {
        "name": "Conversation Engine",
        "version": "0.1.0",
        "status": "active",
        "last_check": time.time()
    }
}

def get_system_health_status() -> Dict[str, Any]:
    """
    Get system health status including CPU, memory, disk usage.
    
    Returns:
        Dictionary with system health metrics
    """
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    uptime = int(time.time() - psutil.boot_time())
    uptime_str = str(datetime.utcfromtimestamp(uptime).strftime('%H:%M:%S'))
    
    # Get plugin status summary
    plugin_status = get_plugin_health_status()
    active_plugins = sum(1 for p in plugin_status.values() if p.get('status') == 'active')
    total_plugins = len(plugin_status)
    
    return {
        "system": {
            "hostname": platform.node(),
            "platform": platform.system(),
            "version": platform.version(),
            "cpu_usage": cpu_percent,
            "memory_total": memory.total,
            "memory_available": memory.available,
            "memory_percent": memory.percent,
            "disk_total": disk.total,
            "disk_free": disk.free,
            "disk_percent": disk.percent,
            "uptime": uptime,
            "uptime_formatted": uptime_str,
            "timestamp": time.time()
        },
        "plugins": {
            "active": active_plugins,
            "total": total_plugins,
            "health_percent": (active_plugins / total_plugins * 100) if total_plugins > 0 else 0
        }
    }

def get_plugin_health_status() -> Dict[str, Dict[str, Any]]:
    """
    Get health status for all registered plugins.
    
    Returns:
        Dictionary with plugin health information
    """
    # In a real implementation, we would check actual plugin health
    # For now, just return the mock registry
    for plugin_id in PLUGIN_REGISTRY:
        # Simulate random health checks (in real implementation, would be actual checks)
        if time.time() - PLUGIN_REGISTRY[plugin_id]["last_check"] > 60:
            PLUGIN_REGISTRY[plugin_id]["last_check"] = time.time()
    
    return PLUGIN_REGISTRY

def check_plugin_health(plugin_id: str) -> Dict[str, Any]:
    """
    Check health of a specific plugin.
    
    Args:
        plugin_id: ID of the plugin to check
        
    Returns:
        Dictionary with plugin health information
    """
    if plugin_id not in PLUGIN_REGISTRY:
        return {"error": "Plugin not found", "plugin_id": plugin_id}
    
    plugin = PLUGIN_REGISTRY[plugin_id]
    
    # In a real implementation, we would do actual health checks
    return {
        "plugin_id": plugin_id,
        "name": plugin["name"],
        "version": plugin["version"],
        "status": plugin["status"],
        "last_check": plugin["last_check"],
        "details": {
            "memory_usage": "12.5 MB",  # Example metrics
            "response_time": "45ms",
            "error_rate": "0.01%"
        }
    }
