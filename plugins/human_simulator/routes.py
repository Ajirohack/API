"""
FastAPI routes for Human Simulator plugin with CRUD operations for admissions and calendar.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from database.connections.base import db
from .models import Admission, CalendarEvent
from .services import human_simulator_service

# Configure logging
logger = logging.getLogger("api.plugins.human_simulator.routes")

router = APIRouter(prefix="/api/plugins/human_simulator", tags=["Human Simulator"])

# Pydantic schemas
class AdmissionCreate(BaseModel):
    applicant_name: str

class AdmissionUpdate(BaseModel):
    status: str

class AdmissionOut(BaseModel):
    id: int
    applicant_name: str
    status: str
    submitted_at: datetime

    class Config:
        from_attributes = True

class CalendarEventCreate(BaseModel):
    event_name: str
    start_time: datetime
    end_time: datetime

class CalendarEventUpdate(BaseModel):
    event_name: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]

class CalendarEventOut(BaseModel):
    id: int
    event_name: str
    start_time: datetime
    end_time: datetime
    created_at: datetime

    class Config:
        orm_mode = True

# Health check endpoint with backend verification
@router.get("/health")
async def health():
    """Check health and connectivity to the Human Simulator backend"""
    try:
        # Check database connectivity
        async with db.session() as session:
            await session.execute("SELECT 1")
        
        # Check backend connectivity
        backend_status = await human_simulator_service._request("GET", "/health")
        
        return {
            "status": "ok",
            "database": "connected",
            "backend": backend_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Admissions CRUD with backend integration
@router.post("/admissions", response_model=AdmissionOut)
async def create_admission(adm: AdmissionCreate):
    """Create a new admission and sync with Human Simulator backend"""
    async with db.session() as session:
        # Create local record
        admission = Admission(applicant_name=adm.applicant_name)
        session.add(admission)
        await session.flush()
        await session.refresh(admission)
        
        # Sync with backend 
        try:
            await human_simulator_service.create_scenario({
                "name": f"Admission for {adm.applicant_name}",
                "description": f"Admission scenario for {adm.applicant_name}",
                "category": "admission",
                "difficulty": 1,
                "context": {"admission_id": admission.id, "applicant_name": adm.applicant_name},
                "characters": []
            })
        except Exception as e:
            # Log the error but continue
            logger.error(f"Error syncing with backend: {str(e)}")
        
        return admission

@router.get("/admissions", response_model=List[AdmissionOut])
async def list_admissions():
    """Get all admissions"""
    async with db.session() as session:
        result = await session.execute(db.engine.select(Admission))
        return result.scalars().all()

@router.get("/admissions/{id}", response_model=AdmissionOut)
async def get_admission(id: int):
    """Get a specific admission by ID"""
    async with db.session() as session:
        admission = await session.get(Admission, id)
        if not admission:
            raise HTTPException(status_code=404, detail="Admission not found")
        return admission

@router.put("/admissions/{id}", response_model=AdmissionOut)
async def update_admission(id: int, adm: AdmissionUpdate):
    """Update admission status and sync with Human Simulator backend"""
    async with db.session() as session:
        admission = await session.get(Admission, id)
        if not admission:
            raise HTTPException(status_code=404, detail="Admission not found")
        
        # Update local record
        admission.status = adm.status
        session.add(admission)
        await session.flush()
        
        # Try to sync with backend
        try:
            await human_simulator_service.update_scenario(
                f"admission-{id}",
                {"status": adm.status}
            )
        except Exception as e:
            # Log the error but continue
            logger.error(f"Error updating backend: {str(e)}")
        
        return admission

@router.delete("/admissions/{id}")
async def delete_admission(id: int):
    """Delete an admission"""
    async with db.session() as session:
        admission = await session.get(Admission, id)
        if not admission:
            raise HTTPException(status_code=404, detail="Admission not found")
        
        # Try to delete from backend
        try:
            await human_simulator_service.delete_scenario(f"admission-{id}")
        except Exception as e:
            # Log the error but continue
            logger.error(f"Error deleting from backend: {str(e)}")
            
        await session.delete(admission)
        return {"deleted": True}

# Calendar CRUD
@router.post("/calendar", response_model=CalendarEventOut)
async def create_event(evt: CalendarEventCreate):
    """Create a new calendar event"""
    async with db.session() as session:
        event = CalendarEvent(
            event_name=evt.event_name,
            start_time=evt.start_time,
            end_time=evt.end_time
        )
        session.add(event)
        await session.flush()
        await session.refresh(event)
        return event

@router.get("/calendar", response_model=List[CalendarEventOut])
async def list_events():
    """Get all calendar events"""
    async with db.session() as session:
        result = await session.execute(db.engine.select(CalendarEvent))
        return result.scalars().all()

@router.get("/calendar/{id}", response_model=CalendarEventOut)
async def get_event(id: int):
    """Get a specific calendar event by ID"""
    async with db.session() as session:
        event = await session.get(CalendarEvent, id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return event

@router.put("/calendar/{id}", response_model=CalendarEventOut)
async def update_event(id: int, evt: CalendarEventUpdate):
    """Update a calendar event"""
    async with db.session() as session:
        event = await session.get(CalendarEvent, id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Update fields if provided
        if evt.event_name is not None:
            event.event_name = evt.event_name
        if evt.start_time is not None:
            event.start_time = evt.start_time
        if evt.end_time is not None:
            event.end_time = evt.end_time
        
        session.add(event)
        await session.flush()
        return event

@router.delete("/calendar/{id}")
async def delete_event(id: int):
    """Delete a calendar event"""
    async with db.session() as session:
        event = await session.get(CalendarEvent, id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        await session.delete(event)
        return {"deleted": True}

# Human Simulator Backend Direct Access
@router.get("/scenarios")
async def get_scenarios():
    """Get scenarios from the Human Simulator backend"""
    return await human_simulator_service.get_scenarios()

@router.post("/analyze-message")
async def analyze_message(message: dict):
    """Send message for analysis by Human Simulator"""
    return await human_simulator_service.analyze_message(message)

@router.get("/personas")
async def get_personas():
    """Get personas from the Human Simulator backend"""
    return await human_simulator_service.get_personas()
