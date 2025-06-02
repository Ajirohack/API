"""
Test application for unit tests.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from tests.test_models import User, Base, UserRole

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    """Dependency for getting test database session"""
    raise NotImplementedError("This should be overridden in tests")

@app.post("/api/auth/register")
async def register(
    username: str,
    email: str,
    password: str,
    role: UserRole = UserRole.USER,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    user = User(
        username=username,
        email=email,
        hashed_password="hashed_" + password,  # Simplified for testing
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }

@app.post("/api/auth/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login to get access token"""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or user.hashed_password != "hashed_" + form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    return {
        "access_token": "test_token",  # Simplified for testing
        "token_type": "bearer"
    }

@app.get("/api/users/me")
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get current user details"""
    # Simplified for testing - in real app would validate token
    user = db.query(User).filter(User.username == "testuser").first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }
