"""
SQLAlchemy models for Human Simulator plugin.
"""
from sqlalchemy import Column, Integer, String, DateTime, func
from database.base import Base

class Admission(Base):
    __tablename__ = 'admissions'
    id = Column(Integer, primary_key=True)
    applicant_name = Column(String(128), nullable=False)
    status = Column(String(32), nullable=False, default='pending')
    submitted_at = Column(DateTime, server_default=func.now())

class CalendarEvent(Base):
    __tablename__ = 'calendar_events'
    id = Column(Integer, primary_key=True)
    event_name = Column(String(128), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
