"""
Token model for storing revoked tokens.
Used for implementing JWT token blacklisting.
"""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base

class RevokedToken(Base):
    """
    Model for storing revoked JWT tokens to implement a token blacklist.
    This provides persistent storage of revoked tokens even if Redis is unavailable.
    """
    __tablename__ = "revoked_tokens"

    id = Column(String, primary_key=True, index=True)
    jti = Column(String, unique=True, index=True, nullable=False)  # JWT token ID
    user_id = Column(Integer, nullable=False)  # User who owned the token
    revoked_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)  # When the token would have expired
    reason = Column(String, nullable=True)  # Optional reason for revocation

    def __repr__(self):
        return f"<RevokedToken jti={self.jti} user_id={self.user_id}>"
