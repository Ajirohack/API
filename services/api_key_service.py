"""
API Key Management Service
Handles integration management and API key operations
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from api.models.api_keys import APIKeyManager, IntegrationConfig, DeploymentEnvironment
from database.connection import get_db_session
import uuid
import json
import os
from datetime import datetime


class APIKeyService:
    """Service for managing API keys and integrations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_api_key(
        self,
        service_name: str,
        service_category: str,
        api_key: str,
        configuration: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None
    ) -> APIKeyManager:
        """Create a new API key entry"""
        
        # Check if key already exists for this service
        existing = self.db.query(APIKeyManager).filter(
            APIKeyManager.service_name == service_name
        ).first()
        
        if existing:
            # Update existing key
            existing.set_api_key(api_key)
            existing.configuration = configuration or {}
            existing.description = description
            existing.updated_at = datetime.utcnow()
            existing.is_active = True
            self.db.commit()
            return existing
        
        # Create new key
        api_key_entry = APIKeyManager(
            id=str(uuid.uuid4()),
            service_name=service_name,
            service_category=service_category,
            configuration=configuration or {},
            description=description,
            is_active=True
        )
        api_key_entry.set_api_key(api_key)
        
        self.db.add(api_key_entry)
        self.db.commit()
        self.db.refresh(api_key_entry)
        
        return api_key_entry
    
    def get_api_key(self, service_name: str) -> Optional[str]:
        """Get decrypted API key for a service"""
        entry = self.db.query(APIKeyManager).filter(
            APIKeyManager.service_name == service_name,
            APIKeyManager.is_active == True
        ).first()
        
        if entry:
            return entry.get_api_key()
        return None
    
    def get_service_config(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a service"""
        entry = self.db.query(APIKeyManager).filter(
            APIKeyManager.service_name == service_name,
            APIKeyManager.is_active == True
        ).first()
        
        if entry:
            return entry.configuration
        return None
    
    def list_api_keys(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all API keys (without exposing the actual keys)"""
        query = self.db.query(APIKeyManager).filter(APIKeyManager.is_active == True)
        
        if category:
            query = query.filter(APIKeyManager.service_category == category)
        
        entries = query.all()
        
        return [
            {
                "id": entry.id,
                "service_name": entry.service_name,
                "service_category": entry.service_category,
                "description": entry.description,
                "has_key": bool(entry.api_key),
                "configuration": entry.configuration,
                "created_at": entry.created_at,
                "updated_at": entry.updated_at
            }
            for entry in entries
        ]
    
    def delete_api_key(self, service_name: str) -> bool:
        """Delete an API key"""
        entry = self.db.query(APIKeyManager).filter(
            APIKeyManager.service_name == service_name
        ).first()
        
        if entry:
            entry.is_active = False
            self.db.commit()
            return True
        return False
    
    def create_integration_config(
        self,
        integration_name: str,
        required_keys: List[str],
        environment_mappings: Dict[str, str],
        configuration: Optional[Dict[str, Any]] = None
    ) -> IntegrationConfig:
        """Create or update integration configuration"""
        
        existing = self.db.query(IntegrationConfig).filter(
            IntegrationConfig.integration_name == integration_name
        ).first()
        
        if existing:
            existing.required_keys = required_keys
            existing.environment_mappings = environment_mappings
            existing.configuration = configuration or {}
            existing.updated_at = datetime.utcnow()
            self.db.commit()
            return existing
        
        config = IntegrationConfig(
            id=str(uuid.uuid4()),
            integration_name=integration_name,
            required_keys=required_keys,
            environment_mappings=environment_mappings,
            configuration=configuration or {},
            is_enabled=False
        )
        
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        
        return config
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations"""
        configs = self.db.query(IntegrationConfig).all()
        api_keys = self.db.query(APIKeyManager).filter(APIKeyManager.is_active == True).all()
        
        # Create lookup for available API keys
        available_keys = {key.service_name: True for key in api_keys}
        
        status = {}
        for config in configs:
            required_keys_status = {}
            for key_name in config.required_keys:
                required_keys_status[key_name] = key_name in available_keys
            
            all_keys_available = all(required_keys_status.values())
            
            status[config.integration_name] = {
                "enabled": config.is_enabled,
                "ready": all_keys_available,
                "required_keys": required_keys_status,
                "configuration": config.configuration
            }
        
        return status
    
    def enable_integration(self, integration_name: str) -> bool:
        """Enable an integration"""
        config = self.db.query(IntegrationConfig).filter(
            IntegrationConfig.integration_name == integration_name
        ).first()
        
        if config:
            config.is_enabled = True
            config.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def disable_integration(self, integration_name: str) -> bool:
        """Disable an integration"""
        config = self.db.query(IntegrationConfig).filter(
            IntegrationConfig.integration_name == integration_name
        ).first()
        
        if config:
            config.is_enabled = False
            config.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def generate_env_file(self, environment: str = "production") -> str:
        """Generate .env file with all configured API keys"""
        
        # Get base environment configuration
        env_config = self.db.query(DeploymentEnvironment).filter(
            DeploymentEnvironment.name == environment
        ).first()
        
        base_config = env_config.configuration if env_config else {}
        
        # Get all active API keys
        api_keys = self.db.query(APIKeyManager).filter(
            APIKeyManager.is_active == True
        ).all()
        
        # Get all integration configs
        integrations = self.db.query(IntegrationConfig).filter(
            IntegrationConfig.is_enabled == True
        ).all()
        
        env_lines = [
            f"# Space Project {environment.title()} Environment Configuration",
            f"# Generated on {datetime.utcnow().isoformat()}",
            "",
            "# === Base Configuration ===",
        ]
        
        # Add base configuration
        for key, value in base_config.items():
            env_lines.append(f"{key}={value}")
        
        env_lines.extend([
            "",
            "# === API Keys and Integrations ===",
        ])
        
        # Add API keys
        for api_key in api_keys:
            decrypted_key = api_key.get_api_key()
            env_lines.append(f"{api_key.service_name.upper()}_API_KEY={decrypted_key}")
            
            # Add any additional configuration
            if api_key.configuration:
                for config_key, config_value in api_key.configuration.items():
                    env_name = f"{api_key.service_name.upper()}_{config_key.upper()}"
                    env_lines.append(f"{env_name}={config_value}")
        
        env_lines.extend([
            "",
            "# === Integration Configurations ===",
        ])
        
        # Add integration-specific environment variables
        for integration in integrations:
            env_lines.append(f"# {integration.integration_name.title()} Integration")
            env_lines.append(f"ENABLE_{integration.integration_name.upper()}=true")
            
            # Add environment mappings
            for env_var, config_key in integration.environment_mappings.items():
                if config_key in integration.configuration:
                    value = integration.configuration[config_key]
                    env_lines.append(f"{env_var}={value}")
            
            env_lines.append("")
        
        return "\n".join(env_lines)


# Pre-defined integration configurations
INTEGRATION_DEFINITIONS = {
    "openai": {
        "required_keys": ["openai"],
        "environment_mappings": {
            "OPENAI_API_BASE_URL": "base_url",
            "ENABLE_OPENAI_API": "enabled"
        },
        "configuration": {
            "base_url": "https://api.openai.com/v1",
            "enabled": True,
            "models": ["gpt-4", "gpt-3.5-turbo", "dall-e-3"]
        }
    },
    "anthropic": {
        "required_keys": ["anthropic"],
        "environment_mappings": {
            "ANTHROPIC_API_BASE_URL": "base_url",
            "ENABLE_ANTHROPIC_API": "enabled"
        },
        "configuration": {
            "base_url": "https://api.anthropic.com",
            "enabled": True,
            "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
        }
    },
    "google_search": {
        "required_keys": ["google_pse", "google_pse_engine_id"],
        "environment_mappings": {
            "GOOGLE_PSE_API_KEY": "api_key",
            "GOOGLE_PSE_ENGINE_ID": "engine_id"
        },
        "configuration": {
            "enabled": True,
            "search_type": "web"
        }
    },
    "bing_search": {
        "required_keys": ["bing_search_v7"],
        "environment_mappings": {
            "BING_SEARCH_V7_SUBSCRIPTION_KEY": "api_key",
            "BING_SEARCH_V7_ENDPOINT": "endpoint"
        },
        "configuration": {
            "endpoint": "https://api.bing.microsoft.com/v7.0/search",
            "enabled": True
        }
    },
    "azure_storage": {
        "required_keys": ["azure_storage"],
        "environment_mappings": {
            "AZURE_STORAGE_KEY": "api_key",
            "AZURE_STORAGE_ENDPOINT": "endpoint",
            "AZURE_STORAGE_CONTAINER_NAME": "container"
        },
        "configuration": {
            "enabled": True
        }
    },
    "tavily_search": {
        "required_keys": ["tavily"],
        "environment_mappings": {
            "TAVILY_API_KEY": "api_key"
        },
        "configuration": {
            "enabled": True,
            "extract_depth": "basic"
        }
    },
    "brave_search": {
        "required_keys": ["brave_search"],
        "environment_mappings": {
            "BRAVE_SEARCH_API_KEY": "api_key"
        },
        "configuration": {
            "enabled": True
        }
    },
    "serpapi": {
        "required_keys": ["serpapi"],
        "environment_mappings": {
            "SERPAPI_API_KEY": "api_key",
            "SERPAPI_ENGINE": "engine"
        },
        "configuration": {
            "engine": "google",
            "enabled": True
        }
    },
    "firecrawl": {
        "required_keys": ["firecrawl"],
        "environment_mappings": {
            "FIRECRAWL_API_KEY": "api_key",
            "FIRECRAWL_API_BASE_URL": "base_url"
        },
        "configuration": {
            "base_url": "https://api.firecrawl.dev",
            "enabled": True
        }
    },
    "perplexity": {
        "required_keys": ["perplexity"],
        "environment_mappings": {
            "PERPLEXITY_API_KEY": "api_key"
        },
        "configuration": {
            "enabled": True
        }
    },
    "groq": {
        "required_keys": ["groq"],
        "environment_mappings": {
            "GROQ_API_KEY": "api_key"
        },
        "configuration": {
            "enabled": True
        }
    }
}
