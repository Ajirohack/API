"""
Authentication routes for the Space API.

These routes handle user authentication, including:
- User login
- Token refresh
- Token revocation
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
import jwt
from datetime import datetime

from database.connection import get_db_session
from models import SuccessResponse
from models.auth import Token, User, UserRead, UserCreate
from services.user_service import UserService, get_user_service
from config.settings import settings

router = APIRouter(tags=["authentication"])

# Dependency to get UserService with proper database injection
def get_user_service_dependency(db: Session = Depends(get_db_session)) -> UserService:
    return get_user_service(db)

# Dependency to get the current user from a token
async def get_current_user(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="/auth/token")),
    user_service: UserService = Depends(get_user_service_dependency)
) -> User:
    """
    Get the current authenticated user from a token.
    
    Args:
        token: JWT token
        user_service: User service
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode token
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
    except jwt.PyJWTError:
        raise credentials_exception
        
    # Get user from database
    user = user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get the current admin user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

@router.post("/auth/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service_dependency)
):
    """
    Authenticate user and issue access and refresh tokens
    
    - **username**: Username or email
    - **password**: User password
    
    Returns:
        Access and refresh tokens
    """
    # Authenticate user
    user = user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Generate tokens
    tokens = user_service.generate_tokens(user)
    
    return tokens

@router.post("/auth/refresh", response_model=Token)
async def refresh_token(
    token: str = Body(..., embed=True),
    user_service: UserService = Depends(get_user_service_dependency)
):
    """
    Get a new access token using a refresh token
    
    - **token**: Refresh token
    
    Returns:
        New access token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode token
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY.get_secret_value(), 
            algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
        # Check token expiration
        exp = payload.get("exp")
        if exp is None or datetime.utcnow().timestamp() > exp:
            raise credentials_exception
            
    except jwt.PyJWTError:
        raise credentials_exception
        
    # Get user
    user = user_service.get_user_by_username(username)
    if user is None or not user.is_active:
        raise credentials_exception
        
    # Generate new tokens
    tokens = user_service.generate_tokens(user)
    
    return tokens

@router.post("/auth/revoke")
async def revoke_token(
    token: str = Body(..., embed=True),
    db: Session = Depends(get_db_session)
):
    """
    Revoke a JWT token
    
    - **token**: JWT token to revoke
    
    Note: This is a placeholder for token revocation. In a production system,
    you would typically store revoked tokens in a fast database like Redis
    with an expiration time matching the token's expiration.
    """
    # In a real implementation, you would add the token to a blacklist
    # For now, we'll just return a success message
    return {"status": "success", "message": "Token revoked"}

@router.get("/auth/me", response_model=UserRead)
async def get_current_user_profile(
    user: User = Depends(get_current_active_user)
):
    """
    Get the current authenticated user's profile
    
    Returns:
        User profile
    """
    return user

@router.post("/auth/register", response_model=UserRead)
async def register_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service_dependency)
):
    """
    Register a new user
    
    - **username**: Unique username
    - **email**: User email address
    - **password**: User password
    - **role**: User role (defaults to 'user')
    
    Returns:
        User profile information
    """
    # Check if user already exists
    existing_user = user_service.get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    existing_email = user_service.get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = user_service.create_user(user_data)
    return user
