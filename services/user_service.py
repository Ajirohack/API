"""
User service for the Space API.

This service encapsulates all user-related business logic, including:
- User authentication
- User registration
- User profile management
"""
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext

from database.models.user import User
from models.auth import UserCreate, UserUpdate, UserRead, Token
from config.settings import settings
import jwt

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    """
    Service for user-related operations
    """
    def __init__(self, db: Session):
        self.db = db
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify that a plain password matches a hashed password.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if passwords match
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """
        Hash a password using the current hashing algorithm.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return pwd_context.hash(password)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: Username to look up
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.
        
        Args:
            email: Email to look up
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: User ID to look up
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user by username and password.
        
        Args:
            username: Username to authenticate
            password: Password to verify
            
        Returns:
            User object if authentication succeeded, None otherwise
        """
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user object
            
        Raises:
            HTTPException: If username or email already exists
        """
        # Check if username already exists
        if self.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        if self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        hashed_password = self.get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            role="user"  # Default role
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def update_user(self, user_id: str, user_data: UserUpdate) -> User:
        """
        Update a user.
        
        Args:
            user_id: ID of the user to update
            user_data: User update data
            
        Returns:
            Updated user object
            
        Raises:
            HTTPException: If user not found or email already exists
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if email is being updated and already exists
        if user_data.email and user_data.email != user.email:
            if self.get_user_by_email(user_data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            user.email = user_data.email
        
        # Update other fields
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        
        if user_data.password:
            user.hashed_password = self.get_password_hash(user_data.password)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Optional expiration time delta
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """
        Create a JWT refresh token.
        
        Args:
            data: Data to encode in the token
            
        Returns:
            Encoded JWT token
        """
        expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        return self.create_access_token(data, expires_delta=expires)
    
    def generate_tokens(self, user: User) -> Token:
        """
        Generate access and refresh tokens for a user.
        
        Args:
            user: User to generate tokens for
            
        Returns:
            Token object with access and refresh tokens
        """
        token_data = {"sub": user.username}
        
        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)
        
        # Calculate expiration time in seconds for client reference
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in
        )


# Dependency to get the user service
def get_user_service(db: Session) -> UserService:
    """
    Get a UserService instance.
    
    Args:
        db: Database session
        
    Returns:
        UserService instance
    """
    return UserService(db)
