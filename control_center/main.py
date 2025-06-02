"""
Control Center API main module.
Provides central management dashboard, system monitoring and plugin administration.
"""
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.models import DataResponse
from api.auth import get_current_active_user
from database.models.user import User
from api.config.settings import settings

from . import monitoring, dashboard, system_settings

app = FastAPI(
    title="SpaceNew Control Center API",
    description="Central management and monitoring API for SpaceNew platform",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(monitoring.router)
app.include_router(dashboard.router)
app.include_router(system_settings.router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for all unhandled exceptions"""
    # Log the exception
    print(f"Unhandled exception in Control Center: {exc}")
    
    # Return appropriate error response
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    # For all other exceptions
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/", response_model=DataResponse)
async def root(current_user: User = Depends(get_current_active_user)):
    """Root endpoint for the Control Center API"""
    return DataResponse(
        status="success",
        message="Welcome to the SpaceNew Control Center API",
        data={
            "version": "0.1.0",
            "environment": config.environment,
            "modules": ["plugins", "monitoring", "dashboard", "system_settings"]
        }
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup():
    """Execute tasks on application startup"""
    print(f"Starting Control Center in {config.environment} mode")

@app.on_event("shutdown")
async def shutdown():
    """Execute tasks on application shutdown"""
    print("Shutting down Control Center")
