"""
API endpoints for accessing and managing Format Templates (FMTs)
"""
from typing import List, Dict, Any, Optional
import json
import os
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from database.connection import get_db_session
from database.models.fmt_template import FMTTemplate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/fmt", tags=["fmt_templates"])

# Models
class FMTBase(BaseModel):
    name: str
    description: str
    category: str
    template_text: str
    
class FMTCreate(FMTBase):
    character_id: Optional[str] = None
    tags: List[str] = []
    step_number: Optional[int] = None
    
class FMTResponse(FMTBase):
    id: str
    character_id: Optional[str] = None
    tags: List[str] = []
    step_number: Optional[int] = None

    class Config:
        orm_mode = True

@router.get("", response_model=List[FMTResponse])
async def get_fmt_templates(
    character_id: Optional[str] = None,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db_session),
):
    """
    Get FMT templates with optional filtering
    """
    query = db.query(FMTTemplate)
    
    if character_id:
        query = query.filter(FMTTemplate.character_id == character_id)
    
    if category:
        query = query.filter(FMTTemplate.category == category)
    
    if tag:
        query = query.filter(FMTTemplate.tags.contains([tag]))
    
    templates = query.all()
    return templates

@router.get("/{fmt_id}", response_model=FMTResponse)
async def get_fmt_template(
    fmt_id: str,
    db: Session = Depends(get_db_session),
):
    """
    Get a specific FMT template by ID
    """
    template = db.query(FMTTemplate).filter(FMTTemplate.id == fmt_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"FMT template with ID {fmt_id} not found",
        )
    return template

@router.post("", response_model=FMTResponse)
async def create_fmt_template(
    fmt: FMTCreate,
    db: Session = Depends(get_db_session),
):
    """
    Create a new FMT template
    """
    template = FMTTemplate(
        name=fmt.name,
        description=fmt.description,
        category=fmt.category,
        template_text=fmt.template_text,
        character_id=fmt.character_id,
        tags=fmt.tags,
        step_number=fmt.step_number,
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return template

@router.post("/import", response_model=List[FMTResponse])
async def import_fmt_templates(
    character_id: str, 
    db: Session = Depends(get_db_session)
):
    """
    Import FMT templates for a character from the reference system
    """
    # In a real implementation, this would read from the reference files
    # For now, we'll create some example templates based on the reference structure
    
    templates = [
        FMTTemplate(
            name="Introduction Phase",
            description="Initial contact and introduction",
            category="Friendship Path Process",
            template_text=(
                "Hello {{target.name}}, I'm {{character.name}}. "
                "I noticed your profile and {{customReason}}. "
                "Would love to connect with a fellow {{sharedInterest}}."
            ),
            character_id=character_id,
            tags=["introduction", "initial-contact"],
            step_number=1,
        ),
        FMTTemplate(
            name="Trust Builder",
            description="Building initial trust through shared interests",
            category="Friendship Path Process",
            template_text=(
                "It's great to connect with you! I've been {{character.activity}} "
                "for the past {{timeframe}}. What about you? Have you always been "
                "interested in {{target.interest}}? I find it fascinating because {{reason}}."
            ),
            character_id=character_id,
            tags=["trust-building", "connection"],
            step_number=2,
        ),
        FMTTemplate(
            name="Personal Story Sharing",
            description="Sharing personal stories to deepen connection",
            category="Friendship Path Process",
            template_text=(
                "I wanted to share something with you that happened to me recently. "
                "{{character.personalStory}}\n\n"
                "I'm curious if you've had any similar experiences?"
            ),
            character_id=character_id,
            tags=["personal", "story-sharing"],
            step_number=3,
        ),
        FMTTemplate(
            name="Follow Up - Missing You",
            description="Re-engagement message for when conversation has stalled",
            category="Follow Up",
            template_text=(
                "Hey {{target.name}}, I noticed we haven't spoken in a while. "
                "I've been thinking about our conversation about {{previousTopic}} "
                "and wanted to check in. How have you been? {{personalQuestion}}"
            ),
            character_id=character_id,
            tags=["follow-up", "re-engagement"],
            step_number=None,
        ),
    ]
    
    for template in templates:
        db.add(template)
    
    db.commit()
    
    for template in templates:
        db.refresh(template)
    
    return templates

@router.get("/{fmt_id}/recommendations", response_model=Dict[str, Any])
async def get_fmt_recommendations(
    fmt_id: str,
    target_info: Dict[str, Any],
    conversation_history: List[Dict[str, Any]],
    db: Session = Depends(get_db_session),
):
    """
    Get recommendations for FMT template usage based on target profile and conversation history
    """
    # In a real implementation, this would analyze the conversation and target
    # to make recommendations. For now, we'll return a simulated response
    
    return {
        "recommended_variables": {
            "customReason": "your interest in international affairs",
            "sharedInterest": "global diplomacy enthusiast",
            "timeframe": "5 years",
            "reason": "it offers unique insights into cultural dynamics",
            "previousTopic": "your travel experiences",
            "personalQuestion": "Did you ever make it to that museum you mentioned?",
        },
        "fit_score": 85,
        "sentiment_analysis": {
            "target_sentiment": "positive",
            "engagement_level": "high",
            "trust_level": "growing",
        },
        "next_steps": [
            "Share more personal details about your work",
            "Ask about their personal goals",
            "Suggest a potential meetup scenario"
        ]
    }
