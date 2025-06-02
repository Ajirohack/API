"""
API documentation utilities and configuration.
"""
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI
from typing import Dict, Any

def custom_openapi_schema(app: FastAPI, title: str, version: str):
    """
    Generate a custom OpenAPI schema for the application.
    
    Args:
        app: FastAPI application instance
        title: API title
        version: API version
        
    Returns:
        Custom OpenAPI schema
    """
    if app.openapi_schema:
        return app.openapi_schema
        
    openapi_schema = get_openapi(
        title=title,
        version=version,
        description="API documentation for the SpaceNew platform",
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token"
        }
    }
    
    # Apply security globally
    openapi_schema["security"] = [{"bearerAuth": []}]
    
    # Add custom documentation info
    openapi_schema["info"]["contact"] = {
        "name": "API Support",
        "email": "api-support@spacenew.com",
        "url": "https://docs.spacenew.com"
    }
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://spacenew.com/logo.png"
    }
    
    # Add server environments
    openapi_schema["servers"] = [
        {
            "url": "https://api.spacenew.com",
            "description": "Production server"
        },
        {
            "url": "https://staging-api.spacenew.com",
            "description": "Staging server"
        },
        {
            "url": "http://localhost:8000",
            "description": "Local development server"
        }
    ]
    
    # Add examples and additional documentation
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            if "security" not in operation:
                operation["security"] = [{"bearerAuth": []}]

    # Add custom documentation sections
    openapi_schema["tags"] = [
        {
            "name": "auth",
            "description": "Authentication and authorization endpoints"
        },
        {
            "name": "mcp",
            "description": "Model Context Protocol integration endpoints"
        },
        {
            "name": "plugins",
            "description": "Plugin system management endpoints"
        },
        {
            "name": "metrics",
            "description": "System metrics and monitoring endpoints"
        },
        {
            "name": "health",
            "description": "Health check and system status endpoints"
        }
    ]

    # Cache the schema
    app.openapi_schema = openapi_schema
    return app.openapi_schema
