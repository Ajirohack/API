# API Models Package
from typing import Any, Optional, Dict
from pydantic import BaseModel
from .api_keys import APIKeyManager, IntegrationConfig, DeploymentEnvironment
from .plugins import PluginStatus, PluginRead
from .auth import Token, User, UserRead, UserCreate, UserUpdate

class SuccessResponse(BaseModel):
    """Base success response model"""
    status: str = "success"
    message: str | None = None

class PaginationParams(BaseModel):
    """Common pagination parameters"""
    page: int = 1
    per_page: int = 10

class DataResponse(SuccessResponse):
    """Response model with data payload"""
    data: Optional[Any] = None
    meta: Optional[Dict[str, Any]] = None

__all__ = [
    "APIKeyManager", "IntegrationConfig", "DeploymentEnvironment",
    "SuccessResponse", "DataResponse", "PaginationParams",
    "PluginStatus", "PluginRead", "Token", "User", "UserRead", "UserCreate", "UserUpdate"
]
