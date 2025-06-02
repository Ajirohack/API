"""
Format Template model for database storage.
"""
from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean
from sqlalchemy.sql import func
from database.connection import Base

class FMTTemplate(Base):
    """Format Template model"""
    __tablename__ = "fmt_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String)
    format_string = Column(String, nullable=False)
    variables = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
