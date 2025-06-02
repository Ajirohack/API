"""
Core API models and schemas for the SpaceNew platform.
"""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Literal
from pydantic import BaseModel, Field, validator

# Common types and enums

class ResourceType(str, Enum):
    """Types of resources in the system"""
    AGENT = "agent"
    WORKFLOW = "workflow"
    PLUGIN = "plugin"
    USER = "user"
    DOCUMENT = "document"
    CONVERSATION = "conversation"
    TEMPLATE = "template"
    CHARACTER = "character"
    INTERFACE = "interface"
    ENDPOINT = "endpoint"

class ResponseStatus(str, Enum):
    """Status values for API responses"""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"

# Base response models

class BaseResponse(BaseModel):
    """Base model for all API responses"""
    status: ResponseStatus = Field(..., description="Response status")
    message: str = Field(..., description="Human-readable message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

class ErrorResponse(BaseResponse):
    """Model for error responses"""
    status: Literal[ResponseStatus.ERROR] = Field(ResponseStatus.ERROR, description="Response status")
    error_code: str = Field(..., description="Error code for programmatic handling")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

class SuccessResponse(BaseResponse):
    """Model for success responses with no data"""
    status: Literal[ResponseStatus.SUCCESS] = Field(ResponseStatus.SUCCESS, description="Response status")

class DataResponse(SuccessResponse):
    """Model for success responses with data"""
    data: Dict[str, Any] = Field(..., description="Response data")

class PaginatedResponse(SuccessResponse):
    """Model for paginated responses"""
    items: List[Any] = Field(..., description="Page of results")
    total: int = Field(..., description="Total number of results")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Number of results per page")
    pages: int = Field(..., description="Total number of pages")
    
    @property
    def total_pages(self) -> int:
        """Calculate total number of pages"""
        return (self.total + self.size - 1) // self.size

# Common query parameters

class PaginationParams(BaseModel):
    """Common pagination parameters"""
    page: int = Field(default=1, gt=0, description="Page number (1-indexed)")
    size: int = Field(default=10, gt=0, le=100, description="Number of items per page")

class SortParams(BaseModel):
    """Common sorting parameters"""
    field: str = Field(..., description="Field to sort by")
    order: Literal["asc", "desc"] = Field("asc", description="Sort order")

# User and authentication models

class UserRole(str, Enum):
    """User roles in the system"""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    SYSTEM = "system"
    API = "api"

class UserCreate(BaseModel):
    """Model for creating a new user"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    password: str = Field(..., min_length=8)
    role: UserRole = Field(default=UserRole.USER, description="User role")
    
    @validator("username")
    def username_alphanumeric(cls, v):
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username must be alphanumeric")
        return v

class UserUpdate(BaseModel):
    """Model for updating a user"""
    email: Optional[str] = Field(None, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[UserRole] = None

    class Config:
        extra = "forbid"

class UserRead(BaseModel):
    """Model for reading a user"""
    id: int
    username: str
    email: str
    role: UserRole
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    """Authentication token model"""
    access_token: str
    token_type: str = "bearer"

# Plugin models

class PluginStatus(str, Enum):
    """Status values for plugins"""
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"

class PluginRead(BaseModel):
    """Model for reading plugin information"""
    id: str = Field(..., description="Plugin ID")
    name: str = Field(..., description="Display name")
    version: str = Field(..., description="Version string")
    description: Optional[str] = Field(None, description="Description")
    status: PluginStatus = Field(..., description="Current status")
    capabilities: List[str] = Field([], description="Capabilities provided")
    settings: Dict[str, Any] = Field({}, description="Current settings")

# Agent models

class AgentType(str, Enum):
    """Types of agents in the system"""
    CONVERSATIONAL = "conversational"
    TASK = "task"
    PERSONA = "persona"
    SYSTEM = "system"

class AgentStatus(str, Enum):
    """Status values for agents"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"

class AgentCreate(BaseModel):
    """Model for creating a new agent"""
    name: str = Field(..., min_length=1, max_length=100)
    type: AgentType = Field(..., description="Agent type")
    description: Optional[str] = Field(None, description="Description")
    config: Dict[str, Any] = Field({}, description="Agent configuration")

class AgentRead(BaseModel):
    """Model for reading agent information"""
    id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Display name")
    type: AgentType = Field(..., description="Agent type")
    description: Optional[str] = Field(None, description="Description")
    status: AgentStatus = Field(..., description="Current status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

# Workflow models

class WorkflowStatus(str, Enum):
    """Status values for workflows"""
    DRAFT = "draft"
    ACTIVE = "active"
    DISABLED = "disabled"
    ARCHIVED = "archived"

class WorkflowStepType(str, Enum):
    """Types of workflow steps"""
    AGENT = "agent"
    CONDITION = "condition"
    DELAY = "delay"
    NOTIFICATION = "notification"
    EXTERNAL = "external"

class WorkflowStep(BaseModel):
    """Model for a workflow step"""
    id: str = Field(..., description="Step ID")
    name: str = Field(..., description="Step name")
    type: WorkflowStepType = Field(..., description="Step type")
    config: Dict[str, Any] = Field({}, description="Step configuration")
    next_steps: List[str] = Field([], description="IDs of next steps")

class WorkflowCreate(BaseModel):
    """Model for creating a new workflow"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Description")
    steps: List[WorkflowStep] = Field([], description="Workflow steps")
    triggers: List[Dict[str, Any]] = Field([], description="Workflow triggers")
    is_active: bool = Field(False, description="Whether workflow is active")

class WorkflowRead(BaseModel):
    """Model for reading workflow information"""
    id: str = Field(..., description="Workflow ID")
    name: str = Field(..., description="Display name")
    description: Optional[str] = Field(None, description="Description")
    status: WorkflowStatus = Field(..., description="Current status")
    steps: List[WorkflowStep] = Field([], description="Workflow steps")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

# Document models

class DocumentType(str, Enum):
    """Types of documents in the system"""
    TEXT = "text"
    PDF = "pdf"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"

class DocumentCreate(BaseModel):
    """Model for creating a new document"""
    name: str = Field(..., min_length=1, max_length=100)
    type: DocumentType = Field(..., description="Document type")
    content: Optional[str] = Field(None, description="Document content (for text)")
    metadata: Dict[str, Any] = Field({}, description="Document metadata")

class DocumentRead(BaseModel):
    """Model for reading document information"""
    id: str = Field(..., description="Document ID")
    name: str = Field(..., description="Display name")
    type: DocumentType = Field(..., description="Document type")
    size: int = Field(..., description="Document size in bytes")
    metadata: Dict[str, Any] = Field({}, description="Document metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
