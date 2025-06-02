"""
Authentication models and schemas.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserRead(BaseModel):
    """User read model"""
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserCreate(BaseModel):
    """User creation model"""
    username: str
    email: str
    password: str

class UserUpdate(BaseModel):
    """User update model"""
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None

class User(BaseModel):
    """User model for authentication"""
    id: int
    username: str
    email: str
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
    role: str = "user"  # Added role field
    created_at: datetime
    updated_at: Optional[datetime] = None
