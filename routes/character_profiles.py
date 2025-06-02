"""
API endpoints for character profiles, including FMT (Format Template) integration
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from database.connection import get_db_session
from database.models.character_profile import CharacterProfile
from sqlalchemy.orm import Session
from uuid import UUID
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Import the FMT Controller
from core.engines.engine1.src.controllers.fmt_controller import FMTController

router = APIRouter(prefix="/api/characters", tags=["characters"])

# Models
class CharacterBase(BaseModel):
    name: str
    profession: str
    description: Optional[str]
    backstory: Optional[str]
    personality: Optional[str]
    communicationStyle: Optional[str]
    manipulationLevel: Optional[int] = 50
    targetAudience: Optional[str]
    mode: Optional[str] = "standard"  # standard, archivist, orchestrator
    
class CharacterCreate(CharacterBase):
    pass
    
class CharacterUpdate(CharacterBase):
    pass
    
class CharacterResponse(CharacterBase):
    id: UUID
    avatarUrl: Optional[str]
    
    class Config:
        orm_mode = True

class MessageBase(BaseModel):
    role: str  # user, assistant
    content: str
    timestamp: Optional[str]
    
class AnalyzeConversationRequest(BaseModel):
    characterId: UUID
    messages: List[MessageBase]
    targetProfile: Optional[Dict[str, Any]]

class RecommendFMTRequest(BaseModel):
    characterId: UUID
    conversationId: Optional[str]
    messages: List[MessageBase]
    targetProfile: Optional[Dict[str, Any]]
    
# Initialize FMT Controller
fmt_controller = FMTController()

@router.get("", response_model=List[CharacterResponse])
async def get_characters(
    mode: Optional[str] = None,
    include_default: bool = True,
    db: Session = Depends(get_db_session),
):
    """
    Get all character profiles with optional filtering by mode
    If include_default is True, Diego Camilleri will always be included as the default character
    """
    query = db.query(CharacterProfile)
    
    if mode:
        query = query.filter(CharacterProfile.mode == mode)
    
    characters = query.all()
    
    # If no characters found and include_default is True, try to create Diego as default
    if not characters and include_default:
        try:
            # Import only when needed to avoid circular imports
            from database.samples.diego_camilleri_profile import create_diego_camilleri
            diego = create_diego_camilleri(db)
            characters = [diego]
        except Exception as e:
            logger.error(f"Error creating default character: {str(e)}")
    
    return characters

@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: UUID,
    db: Session = Depends(get_db_session),
):
    """
    Get a specific character profile by ID
    """
    character = db.query(CharacterProfile).filter(CharacterProfile.id == character_id).first()
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found",
        )
    return character

@router.post("", response_model=CharacterResponse)
async def create_character(
    character: CharacterCreate,
    db: Session = Depends(get_db_session),
):
    """
    Create a new character profile
    """
    db_character = CharacterProfile(
        name=character.name,
        profession=character.profession,
        description=character.description,
        backstory=character.backstory,
        personality=character.personality,
        communicationStyle=character.communicationStyle,
        manipulationLevel=character.manipulationLevel,
        targetAudience=character.targetAudience,
        mode=character.mode,
    )
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character

@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: UUID,
    character: CharacterUpdate,
    db: Session = Depends(get_db_session),
):
    """
    Update a character profile
    """
    db_character = db.query(CharacterProfile).filter(CharacterProfile.id == character_id).first()
    if not db_character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found",
        )
    
    # Update attributes
    for key, value in character.dict(exclude_unset=True).items():
        setattr(db_character, key, value)
    
    db.commit()
    db.refresh(db_character)
    return db_character

@router.delete("/{character_id}")
async def delete_character(
    character_id: UUID,
    db: Session = Depends(get_db_session),
):
    """
    Delete a character profile
    """
    db_character = db.query(CharacterProfile).filter(CharacterProfile.id == character_id).first()
    if not db_character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found",
        )
    
    db.delete(db_character)
    db.commit()
    return {"message": f"Character {character_id} deleted successfully"}

@router.post("/{character_id}/analyze-conversation")
async def analyze_conversation(
    character_id: UUID,
    request: AnalyzeConversationRequest,
    db: Session = Depends(get_db_session),
):
    """
    Analyze a conversation between a character and target
    """
    # Verify character exists
    character = db.query(CharacterProfile).filter(CharacterProfile.id == character_id).first()
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found",
        )
    
    # Convert character to dict for analysis
    character_dict = {
        "id": str(character.id),
        "name": character.name,
        "profession": character.profession,
        "personality": character.personality,
        "communicationStyle": character.communicationStyle,
        "manipulationLevel": character.manipulationLevel,
        "mode": character.mode
    }
    
    # Convert messages to format needed by FMT controller
    messages = [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp
        }
        for msg in request.messages
    ]
    
    # Call FMT controller to analyze conversation
    result = fmt_controller.analyze_conversation(
        messages=messages,
        character_profile=character_dict,
        target_profile=request.targetProfile
    )
    
    return result

@router.post("/{character_id}/build-target-profile")
async def build_target_profile(
    character_id: UUID,
    request: AnalyzeConversationRequest,
    db: Session = Depends(get_db_session),
):
    """
    Build or update a target profile based on conversation history
    """
    # Verify character exists
    character = db.query(CharacterProfile).filter(CharacterProfile.id == character_id).first()
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found",
        )
    
    # Convert messages to format needed by FMT controller
    messages = [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp
        }
        for msg in request.messages
    ]
    
    # Call FMT controller to build target profile
    result = fmt_controller.build_target_profile(messages=messages)
    
    return result

@router.post("/{character_id}/recommend-fmt")
async def recommend_fmt(
    character_id: UUID,
    request: RecommendFMTRequest,
    db: Session = Depends(get_db_session),
):
    """
    Get FMT recommendations for the current conversation state
    """
    # Verify character exists
    character = db.query(CharacterProfile).filter(CharacterProfile.id == character_id).first()
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character with ID {character_id} not found",
        )
    
    # Convert character to dict for analysis
    character_dict = {
        "id": str(character.id),
        "name": character.name,
        "profession": character.profession,
        "personality": character.personality,
        "communicationStyle": character.communicationStyle,
        "manipulationLevel": character.manipulationLevel,
        "mode": character.mode
    }
    
    # Convert messages to format needed by FMT controller
    messages = [
        {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp
        }
        for msg in request.messages
    ]
    
    # Call FMT controller to analyze conversation
    analysis = fmt_controller.analyze_conversation(
        messages=messages,
        character_profile=character_dict,
        target_profile=request.targetProfile
    )
    
    # Return FMT recommendations from the analysis
    return {
        "conversationAnalysis": {
            "metrics": analysis.get("metrics", {}),
            "emotionalAnalysis": analysis.get("emotional_analysis", {}),
            "conversationPhase": analysis.get("conversation_insights", {}).get("conversation_phase", "introduction")
        },
        "recommendations": analysis.get("fmt_recommendations", [])
    }
