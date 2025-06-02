"""
Agent API endpoints for creating, managing, and interacting with agents.
"""
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from api.models import AgentCreate, AgentRead, AgentType, AgentStatus
from api.auth import get_current_active_user, get_current_admin_user
from database.models.user import User

router = APIRouter(prefix="/agents", tags=["agents"])

# Mock agent storage for now
# In a real implementation, this would use the database
_agents = {}

class Message(BaseModel):
    """Message in a conversation with an agent"""
    content: str = Field(..., description="Message content")
    role: str = Field(..., description="Message role (user or assistant)")
    timestamp: datetime = Field(default_factory=datetime.now)

class ConversationRequest(BaseModel):
    """Request to send a message to an agent"""
    message: str = Field(..., description="Message to send to the agent")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID")

class ConversationResponse(BaseModel):
    """Response from an agent"""
    message: str = Field(..., description="Agent response message")
    conversation_id: str = Field(..., description="Conversation ID for continuing the conversation")
    agent_id: str = Field(..., description="Agent ID")
    timestamp: datetime = Field(default_factory=datetime.now)

@router.post("/", response_model=AgentRead)
async def create_agent(
    agent: AgentCreate,
    current_user: User = Depends(get_current_admin_user)
) -> AgentRead:
    """Create a new agent (admin only)"""
    agent_id = str(uuid4())
    created_at = datetime.now()
    
    agent_data = AgentRead(
        id=agent_id,
        name=agent.name,
        type=agent.type,
        description=agent.description,
        status=AgentStatus.IDLE,
        created_at=created_at,
        updated_at=created_at
    )
    
    _agents[agent_id] = {
        **agent_data.dict(),
        "config": agent.config,
        "conversations": {},
        "creator_id": current_user.id
    }
    
    return agent_data

@router.get("/", response_model=List[AgentRead])
async def list_agents(
    type: Optional[AgentType] = Query(None, description="Filter by agent type"),
    status: Optional[AgentStatus] = Query(None, description="Filter by agent status"),
    current_user: User = Depends(get_current_active_user)
) -> List[AgentRead]:
    """List all available agents"""
    results = []
    
    for agent_id, agent_data in _agents.items():
        # Apply filters if specified
        if type and agent_data["type"] != type:
            continue
        if status and agent_data["status"] != status:
            continue
            
        results.append(AgentRead(
            id=agent_id,
            name=agent_data["name"],
            type=agent_data["type"],
            description=agent_data["description"],
            status=agent_data["status"],
            created_at=agent_data["created_at"],
            updated_at=agent_data["updated_at"]
        ))
        
    return results

@router.get("/{agent_id}", response_model=AgentRead)
async def get_agent(
    agent_id: str = Path(..., description="Agent ID"),
    current_user: User = Depends(get_current_active_user)
) -> AgentRead:
    """Get details for a specific agent"""
    if agent_id not in _agents:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    agent_data = _agents[agent_id]
    
    return AgentRead(
        id=agent_id,
        name=agent_data["name"],
        type=agent_data["type"],
        description=agent_data["description"],
        status=agent_data["status"],
        created_at=agent_data["created_at"],
        updated_at=agent_data["updated_at"]
    )

@router.post("/{agent_id}/conversation", response_model=ConversationResponse)
async def converse_with_agent(
    request: ConversationRequest,
    agent_id: str = Path(..., description="Agent ID"),
    current_user: User = Depends(get_current_active_user)
) -> ConversationResponse:
    """Send a message to an agent and get a response"""
    if agent_id not in _agents:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    agent_data = _agents[agent_id]
    
    # Start a new conversation if needed
    conversation_id = request.conversation_id or str(uuid4())
    
    if conversation_id not in agent_data["conversations"]:
        agent_data["conversations"][conversation_id] = []
    
    # Add user message to conversation
    agent_data["conversations"][conversation_id].append(
        Message(content=request.message, role="user")
    )
    
    # Generate mock response 
    # In a real implementation, this would call the agent framework
    response_text = f"Mock response from {agent_data['name']} agent: I received your message '{request.message}'"
    
    # Add agent response to conversation
    agent_data["conversations"][conversation_id].append(
        Message(content=response_text, role="assistant")
    )
    
    return ConversationResponse(
        message=response_text,
        conversation_id=conversation_id,
        agent_id=agent_id,
        timestamp=datetime.now()
    )

@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str = Path(..., description="Agent ID"),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Delete an agent (admin only)"""
    if agent_id not in _agents:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    del _agents[agent_id]
    
    return {
        "status": "success",
        "message": f"Agent {agent_id} deleted successfully"
    }
