"""
API routes and application factory.
Creates and configures FastAPI applications for all API modules.

This file also serves as an initialization for all route modules.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html

# Import route modules for API initialization
# These modules will be imported when the routes package is imported
# from . import character_profiles  # Temporarily disabled
from . import fmt_templates
from . import health
from . import metrics
# from . import engine  # Temporarily disabled due to missing dependencies
from . import plugin_system
from . import auth

try:
    from docs import custom_openapi_schema
except ImportError:
    # Handle case where docs module doesn't exist
    custom_openapi_schema = None

def create_api() -> FastAPI:
    """
    Create a FastAPI application that includes all API modules.
    
    Returns:
        Configured FastAPI application
    """
    # Create main app
    app = FastAPI(
        title="SpaceNew API",
        description="API for the SpaceNew platform",
        version="0.1.0",
        docs_url=None,  # Disable default docs URLs
        redoc_url=None,  # We'll create custom ones
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Update this for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Import API modules
    # from frontend_engine.main import app as frontend_app
    # from control_center.main import app as control_center_app  # Temporarily disabled
    # Import additional modules once they're created
    
    # Mount API modules
    # app.mount("/api/frontend-engine", frontend_app)
    # app.mount("/api/control-center", control_center_app)  # Temporarily disabled
    # Mount additional modules once they're created
    
    # Add custom docs route
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url="/api/openapi.json",
            title="SpaceNew API - Documentation",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        )
    
    # Set custom OpenAPI schema
    app.openapi = lambda: custom_openapi_schema(
        app, "SpaceNew API", "0.1.0"
    )
    
    return app

# Create application instance
app = create_api()
