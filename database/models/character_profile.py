"""
Character profile model for storing character data
"""
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, JSON, Integer, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from database.connection import Base

class CharacterProfile(Base):
    """Character profile database model"""
    __tablename__ = "character_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    archetype = Column(String(100), nullable=True)
    background = Column(Text, nullable=True)
    personality = Column(JSON, nullable=True)
    appearance = Column(Text, nullable=True)
    goals = Column(JSON, nullable=True)
    relationships = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    fmt_template_id = Column(UUID(as_uuid=True), ForeignKey("fmt_templates.id"), nullable=True)
    version = Column(Integer, default=1)
    
    # Relationships
    creator = relationship("User", back_populates="characters")
    fmt_template = relationship("FMTTemplate", back_populates="characters")
    
    def __repr__(self):
        return f"<CharacterProfile {self.name}>"
