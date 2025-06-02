"""
Plugin system models
"""
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel

class PluginStatus(str, Enum):
    """Plugin status enum"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"

class PluginRead(BaseModel):
    """Plugin read model"""
    id: str
    name: str
    version: str
    description: str
    status: PluginStatus
    manifest: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
