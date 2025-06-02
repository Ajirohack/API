"""
Plugin system router for managing and interacting with plugins.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List, Dict, Any
from sqlalchemy.orm import Session
import os
import zipfile
import json

from models import DataResponse, PluginStatus, PluginRead
from config.settings import settings
from database.connection import get_db_session

router = APIRouter(prefix="/plugins", tags=["plugins"])

async def validate_plugin_manifest(manifest_data: Dict[str, Any]) -> None:
    """Validate plugin manifest file"""
    required_fields = ["name", "version", "description", "entry_point"]
    missing_fields = [field for field in required_fields if field not in manifest_data]
    if missing_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required fields in manifest: {', '.join(missing_fields)}"
        )

@router.get("/", response_model=List[PluginRead])
async def list_plugins(db: Session = Depends(get_db_session)):
    """List all installed plugins"""
    plugins = []
    plugin_dir = settings.PLUGIN_DIR
    
    for plugin_name in os.listdir(plugin_dir):
        plugin_path = os.path.join(plugin_dir, plugin_name)
        if os.path.isdir(plugin_path):
            manifest_path = os.path.join(plugin_path, "manifest.json")
            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
                plugins.append(
                    PluginRead(
                        id=plugin_name,
                        name=manifest.get("name", plugin_name),
                        version=manifest.get("version", "0.0.0"),
                        description=manifest.get("description", ""),
                        status=PluginStatus.ENABLED,
                        manifest=manifest,
                        error=None
                    )
                )
    
    return plugins

@router.post("/upload", response_model=PluginRead)
async def upload_plugin(
    plugin_file: UploadFile = File(...),
    db: Session = Depends(get_db_session)
):
    """Upload and install a new plugin"""
    if not plugin_file.filename.endswith('.zip'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plugin must be a ZIP file"
        )
    
    # Create temporary file
    temp_path = f"/tmp/{plugin_file.filename}"
    try:
        with open(temp_path, "wb") as f:
            content = await plugin_file.read()
            f.write(content)
        
        # Extract plugin
        with zipfile.ZipFile(temp_path, 'r') as zip_ref:
            # Verify manifest exists
            if "manifest.json" not in zip_ref.namelist():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Plugin package must contain a manifest.json file"
                )
            
            # Read and validate manifest
            manifest_data = json.loads(zip_ref.read("manifest.json"))
            await validate_plugin_manifest(manifest_data)
            
            # Extract to plugins directory
            plugin_dir = os.path.join(settings.PLUGIN_DIR, manifest_data["name"])
            zip_ref.extractall(plugin_dir)
        
        return PluginRead(
            id=manifest_data["name"],
            name=manifest_data["name"],
            version=manifest_data["version"],
            description=manifest_data.get("description", ""),
            status=PluginStatus.ENABLED,
            manifest=manifest_data,
            error=None
        )
    
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.delete("/{plugin_id}", response_model=DataResponse)
async def uninstall_plugin(
    plugin_id: str,
    db: Session = Depends(get_db_session)
):
    """Uninstall a plugin"""
    plugin_path = os.path.join(settings.PLUGIN_DIR, plugin_id)
    if not os.path.exists(plugin_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin {plugin_id} not found"
        )
    
    # Remove plugin directory
    import shutil
    shutil.rmtree(plugin_path)
    
    return DataResponse(
        status="success",
        message=f"Plugin {plugin_id} uninstalled successfully",
        data={"plugin_id": plugin_id}
    )

@router.post("/{plugin_id}/enable", response_model=PluginRead)
async def enable_plugin(
    plugin_id: str,
    db: Session = Depends(get_db_session)
):
    """Enable a plugin"""
    plugin_path = os.path.join(settings.PLUGIN_DIR, plugin_id)
    if not os.path.exists(plugin_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin {plugin_id} not found"
        )
    
    # Read manifest
    manifest_path = os.path.join(plugin_path, "manifest.json")
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    
    # TODO: Actually enable the plugin in the system
    
    return PluginRead(
        id=plugin_id,
        name=manifest.get("name", plugin_id),
        version=manifest.get("version", "0.0.0"),
        description=manifest.get("description", ""),
        status=PluginStatus.ENABLED,
        manifest=manifest,
        error=None
    )

@router.post("/{plugin_id}/disable", response_model=PluginRead)
async def disable_plugin(
    plugin_id: str,
    db: Session = Depends(get_db_session)
):
    """Disable a plugin"""
    plugin_path = os.path.join(settings.PLUGIN_DIR, plugin_id)
    if not os.path.exists(plugin_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plugin {plugin_id} not found"
        )
    
    # Read manifest
    manifest_path = os.path.join(plugin_path, "manifest.json")
    with open(manifest_path, "r") as f:
        manifest = json.load(f)
    
    # TODO: Actually disable the plugin in the system
    
    return PluginRead(
        id=plugin_id,
        name=manifest.get("name", plugin_id),
        version=manifest.get("version", "0.0.0"),
        description=manifest.get("description", ""),
        status=PluginStatus.DISABLED,
        capabilities=manifest.get("capabilities", []),
        settings=manifest.get("settings", {})
    )
