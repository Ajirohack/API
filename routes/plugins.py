"""
API endpoints for plugin system and UI marketplace.
"""
from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from core.plugin_system.plugin_manager import PluginManager
import asyncio
import json

router = APIRouter(tags=["plugins"])
plugin_manager = PluginManager()

# In-memory event log for SSE demo
plugin_event_log = []

@router.get("/api/plugins/marketplace")
def get_marketplace_plugins():
    # For demo: discover plugins from plugins/ dir
    plugin_manager.discover_plugins("plugins")
    return plugin_manager.list_plugins()

@router.get("/api/plugins/installed")
def get_installed_plugins():
    return plugin_manager.list_plugins()

@router.post("/api/plugins/install")
def install_plugin(data: dict):
    name = data.get("name")
    # For demo: just mark as installed if found in marketplace
    for plugin in plugin_manager.list_plugins():
        if plugin["name"] == name:
            plugin_event_log.append(f"Installed plugin '{name}'")
            return {"status": "installed"}
    return {"status": "not found"}

@router.post("/api/plugins/uninstall")
def uninstall_plugin(data: dict):
    name = data.get("name")
    if name in plugin_manager.plugins:
        del plugin_manager.plugins[name]
        plugin_event_log.append(f"Uninstalled plugin '{name}'")
        return {"status": "uninstalled"}
    return {"status": "not installed"}

@router.post("/api/plugins/settings")
def save_plugin_settings(data: dict):
    name = data.get("name")
    settings = data.get("settings")
    if name in plugin_manager.plugin_meta:
        plugin_manager.plugin_meta[name]["settings"] = settings
        plugin_event_log.append(f"Saved settings for plugin '{name}'")
        return {"status": "ok"}
    return {"status": "not found"}

@router.get("/api/plugins/settings/{name}")
def get_plugin_settings(name: str):
    meta = plugin_manager.plugin_meta.get(name)
    if meta and "settings" in meta:
        return meta["settings"]
    return {}

@router.post("/api/plugins/trigger")
def trigger_plugin(data: dict):
    name = data.get("name")
    try:
        result = plugin_manager.trigger_plugin_action(data)
        # If plugin returns events, emit them
        events = []
        if isinstance(result, dict) and "events" in result:
            for ev in result["events"]:
                plugin_event_log.append(f"[Plugin Event] {ev}")
            events = result["events"]
        plugin_event_log.append(f"Triggered plugin '{name}' with result: {result}")
        return {"result": result, "events": events}
    except Exception as e:
        plugin_event_log.append(f"Error triggering plugin '{name}': {e}")
        return {"error": str(e)}

@router.get("/api/plugins/events")
async def plugin_events():
    async def event_stream():
        last_idx = 0
        while True:
            await asyncio.sleep(1)
            if last_idx < len(plugin_event_log):
                for msg in plugin_event_log[last_idx:]:
                    yield f"data: {msg}\n\n"
                last_idx = len(plugin_event_log)
    return StreamingResponse(event_stream(), media_type="text/event-stream")
