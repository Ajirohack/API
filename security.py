"""
JWT/OAuth2 security utilities for API gateway.
- Comprehensive JWT handling with validation, refresh, and revocation
- Supports WebSocket authentication
- Redis-backed token blacklist for improved security
"""
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import jwt
import redis
import logging

from database.connection import get_db_session
from database.models.user import User
from database.models.token import RevokedToken
from .config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

# Redis for token blacklist
REDIS_URL = settings.REDIS_URL or "redis://localhost:6379/0"
redis_client = redis.Redis.from_url(REDIS_URL)

# JWT Settings
SECRET_KEY = settings.JWT_SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
ALGORITHM = "HS256"

# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def create_jwt_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    token_type: str = "access"
) -> str:
    """
    Create a JWT token with standardized claims
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta
        token_type: Token type (access or refresh)
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        if token_type == "refresh":
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add standard claims
    jti = str(uuid.uuid4())  # Unique token ID for revocation
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": jti,
        "type": token_type
    })
    
    # Encode the token
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_jwt_token(token: str, verify_exp: bool = True) -> Dict[str, Any]:
    """
    Decode and validate a JWT token
    
    Args:
        token: JWT token
        verify_exp: Whether to verify token expiration
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        # Decode token
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={"verify_exp": verify_exp}
        )
        
        # Check if token has been revoked
        if is_token_revoked(payload.get("jti"), payload.get("sub")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
            
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

def is_token_revoked(jti: str, user_id: str) -> bool:
    """
    Check if a token has been revoked
    
    Args:
        jti: JWT token ID
        user_id: User ID
        
    Returns:
        True if token is revoked, False otherwise
    """
    # Check in Redis first (for performance)
    redis_key = f"revoked_token:{jti}"
    if redis_client.exists(redis_key):
        return True
        
    return False

def revoke_token(token: str, db: Session) -> None:
    """
    Revoke a JWT token
    
    Args:
        token: JWT token
        db: Database session
    """
    try:
        # Decode without verifying expiration (allows revoking expired tokens)
        payload = decode_jwt_token(token, verify_exp=False)
        
        jti = payload.get("jti")
        user_id = payload.get("sub")
        exp = datetime.fromtimestamp(payload.get("exp")) 
        
        if not jti or not user_id:
            raise ValueError("Token is missing required claims")
            
        # Add to database for persistence
        revoked_token = RevokedToken(
            id=str(uuid.uuid4()),
            jti=jti,
            user_id=user_id,
            expires_at=exp
        )
        db.add(revoked_token)
        db.commit()
        
        # Add to Redis for fast lookups
        # Set TTL until token expiry to automatically clean up
        ttl = max(0, int(exp.timestamp() - time.time()))
        redis_key = f"revoked_token:{jti}"
        redis_client.setex(redis_key, ttl, "1")
        
    except Exception as e:
        logger.error(f"Error revoking token: {str(e)}")
        raise

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db_session)
) -> User:
    """
    Get the current authenticated user from a token
    
    Args:
        token: JWT token
        db: Database session
        
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
        payload = decode_jwt_token(token)
        user_id: str = payload.get("sub")
        
        if not user_id:
            raise credentials_exception
            
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception
            
        return user
    except HTTPException:
        raise
    except Exception:
        raise credentials_exception

def validate_ws_token(token: str, db: Session) -> Dict[str, Any]:
    """
    Validate a token for WebSocket connections
    
    Args:
        token: JWT token
        db: Database session
        
    Returns:
        User payload if valid
        
    Raises:
        HTTPException: If token is invalid
    """
    # Decode and validate token
    try:
        payload = decode_jwt_token(token)
        
        # Check token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type for WebSocket connection"
            )
        
        # Get user from database to verify existence
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid user ID in token"
            )
            
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
            
        return payload
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

async def get_ws_user(token: str, db: Session) -> Dict[str, Any]:
    """
    Get user info from WebSocket token
    
    Args:
        token: JWT token
        db: Database session
        
    Returns:
        User payload
        
    Raises:
        HTTPException: If token is invalid
    """
    if token.startswith('Bearer '):
        token = token[7:]
        
    return validate_ws_token(token, db)

def verify_token_and_permissions(
    token: str, 
    required_roles: List[str] = None, 
    db: Session = None,
) -> Dict[str, Any]:
    """
    Verify token and check if user has required permissions
    
    Args:
        token: JWT token
        required_roles: List of required roles
        db: Database session
        
    Returns:
        Payload if token is valid and user has required permissions
        
    Raises:
        HTTPException: If token is invalid or user lacks permissions
    """
    payload = decode_jwt_token(token)
    user_id = payload.get("sub")
    
    # Check roles if specified
    if required_roles:
        user_roles = payload.get("roles", [])
        if not any(role in required_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
            
    return payload
