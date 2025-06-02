"""
Workflow API endpoints for creating, managing, and executing workflows.
"""
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from api.models import WorkflowCreate, WorkflowRead, WorkflowStatus, WorkflowStep, WorkflowStepType
from api.auth import get_current_active_user, get_current_admin_user
from database.models.user import User

router = APIRouter(prefix="/workflows", tags=["workflows"])

# Mock workflow storage for now
# In a real implementation, this would use the database
_workflows = {}

class ExecutionRequest(BaseModel):
    """Request to execute a workflow"""
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Input data for the workflow")

class ExecutionResponse(BaseModel):
    """Response from workflow execution"""
    execution_id: str = Field(..., description="Workflow execution ID")
    workflow_id: str = Field(..., description="Workflow ID")
    status: str = Field(..., description="Execution status")
    timestamp: datetime = Field(default_factory=datetime.now)

@router.post("/", response_model=WorkflowRead)
async def create_workflow(
    workflow: WorkflowCreate,
    current_user: User = Depends(get_current_admin_user)
) -> WorkflowRead:
    """Create a new workflow (admin only)"""
    workflow_id = str(uuid4())
    created_at = datetime.now()
    
    workflow_data = WorkflowRead(
        id=workflow_id,
        name=workflow.name,
        description=workflow.description,
        status=WorkflowStatus.DRAFT,
        steps=workflow.steps,
        created_at=created_at,
        updated_at=created_at
    )
    
    _workflows[workflow_id] = {
        **workflow_data.dict(),
        "triggers": workflow.triggers,
        "is_active": workflow.is_active,
        "creator_id": current_user.id,
        "executions": {}
    }
    
    return workflow_data

@router.get("/", response_model=List[WorkflowRead])
async def list_workflows(
    status: Optional[WorkflowStatus] = Query(None, description="Filter by workflow status"),
    current_user: User = Depends(get_current_active_user)
) -> List[WorkflowRead]:
    """List all available workflows"""
    results = []
    
    for workflow_id, workflow_data in _workflows.items():
        # Apply filters if specified
        if status and workflow_data["status"] != status:
            continue
            
        results.append(WorkflowRead(
            id=workflow_id,
            name=workflow_data["name"],
            description=workflow_data["description"],
            status=workflow_data["status"],
            steps=workflow_data["steps"],
            created_at=workflow_data["created_at"],
            updated_at=workflow_data["updated_at"]
        ))
        
    return results

@router.get("/{workflow_id}", response_model=WorkflowRead)
async def get_workflow(
    workflow_id: str = Path(..., description="Workflow ID"),
    current_user: User = Depends(get_current_active_user)
) -> WorkflowRead:
    """Get details for a specific workflow"""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    workflow_data = _workflows[workflow_id]
    
    return WorkflowRead(
        id=workflow_id,
        name=workflow_data["name"],
        description=workflow_data["description"],
        status=workflow_data["status"],
        steps=workflow_data["steps"],
        created_at=workflow_data["created_at"],
        updated_at=workflow_data["updated_at"]
    )

@router.post("/{workflow_id}/activate")
async def activate_workflow(
    workflow_id: str = Path(..., description="Workflow ID"),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Activate a workflow (admin only)"""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    workflow_data = _workflows[workflow_id]
    
    if workflow_data["status"] == WorkflowStatus.ACTIVE:
        return {
            "status": "success",
            "message": f"Workflow {workflow_id} is already active"
        }
        
    workflow_data["status"] = WorkflowStatus.ACTIVE
    workflow_data["is_active"] = True
    workflow_data["updated_at"] = datetime.now()
    
    return {
        "status": "success",
        "message": f"Workflow {workflow_id} activated successfully"
    }

@router.post("/{workflow_id}/deactivate")
async def deactivate_workflow(
    workflow_id: str = Path(..., description="Workflow ID"),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Deactivate a workflow (admin only)"""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    workflow_data = _workflows[workflow_id]
    
    if workflow_data["status"] == WorkflowStatus.DISABLED:
        return {
            "status": "success", 
            "message": f"Workflow {workflow_id} is already disabled"
        }
        
    workflow_data["status"] = WorkflowStatus.DISABLED
    workflow_data["is_active"] = False
    workflow_data["updated_at"] = datetime.now()
    
    return {
        "status": "success",
        "message": f"Workflow {workflow_id} disabled successfully"
    }

@router.post("/{workflow_id}/execute", response_model=ExecutionResponse)
async def execute_workflow(
    request: ExecutionRequest,
    workflow_id: str = Path(..., description="Workflow ID"),
    current_user: User = Depends(get_current_active_user)
) -> ExecutionResponse:
    """Execute a workflow"""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    workflow_data = _workflows[workflow_id]
    
    if workflow_data["status"] != WorkflowStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Workflow is not active")
        
    execution_id = str(uuid4())
    
    # In a real implementation, this would queue the workflow for execution
    # For now, just store the execution request
    workflow_data["executions"][execution_id] = {
        "id": execution_id,
        "workflow_id": workflow_id,
        "status": "pending",
        "input_data": request.input_data,
        "user_id": current_user.id,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "steps_completed": 0,
        "total_steps": len(workflow_data["steps"]),
        "output_data": {}
    }
    
    return ExecutionResponse(
        execution_id=execution_id,
        workflow_id=workflow_id,
        status="pending",
        timestamp=datetime.now()
    )

@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str = Path(..., description="Workflow ID"),
    current_user: User = Depends(get_current_admin_user)
) -> Dict[str, Any]:
    """Delete a workflow (admin only)"""
    if workflow_id not in _workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    del _workflows[workflow_id]
    
    return {
        "status": "success",
        "message": f"Workflow {workflow_id} deleted successfully"
    }
