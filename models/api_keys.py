"""
API Key Management Models
Handles storage and management of external service API keys
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from database.connection import Base
from typing import Optional, Dict, Any
import json
from cryptography.fernet import Fernet
import os
import base64


class APIKeyManager(Base):
    """Model for managing external service API keys"""
    
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, index=True)
    service_name = Column(String, nullable=False, index=True)  # e.g., "openai", "anthropic", "google_pse"
    service_category = Column(String, nullable=False, index=True)  # e.g., "ai_models", "search", "storage"
    api_key = Column(Text, nullable=False)  # Encrypted API key
    configuration = Column(JSON, default=dict)  # Additional service configuration
    is_active = Column(Boolean, default=True)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    @staticmethod
    def get_encryption_key() -> bytes:
        """Get or create encryption key for API keys"""
        key_path = "data/encryption.key"
        if os.path.exists(key_path):
            with open(key_path, "rb") as f:
                return f.read()
        else:
            # Create new encryption key
            key = Fernet.generate_key()
            os.makedirs("data", exist_ok=True)
            with open(key_path, "wb") as f:
                f.write(key)
            return key
    
    def encrypt_api_key(self, plain_key: str) -> str:
        """Encrypt API key for storage"""
        if not plain_key:
            return ""
        
        fernet = Fernet(self.get_encryption_key())
        encrypted = fernet.encrypt(plain_key.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_api_key(self) -> str:
        """Decrypt API key for use"""
        if not self.api_key:
            return ""
        
        try:
            fernet = Fernet(self.get_encryption_key())
            encrypted_bytes = base64.b64decode(self.api_key.encode())
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception:
            return ""
    
    def set_api_key(self, plain_key: str):
        """Set API key (automatically encrypts)"""
        self.api_key = self.encrypt_api_key(plain_key)
    
    def get_api_key(self) -> str:
        """Get decrypted API key"""
        return self.decrypt_api_key()


class IntegrationConfig(Base):
    """Model for managing integration configurations"""
    
    __tablename__ = "integration_configs"
    
    id = Column(String, primary_key=True, index=True)
    integration_name = Column(String, nullable=False, unique=True, index=True)
    is_enabled = Column(Boolean, default=False)
    configuration = Column(JSON, default=dict)
    environment_mappings = Column(JSON, default=dict)  # Maps to environment variables
    required_keys = Column(JSON, default=list)  # Required API keys/config
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class DeploymentEnvironment(Base):
    """Model for managing different deployment environments"""
    
    __tablename__ = "deployment_environments"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)  # e.g., "development", "production", "staging"
    description = Column(Text)
    configuration = Column(JSON, default=dict)  # Environment-specific settings
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
