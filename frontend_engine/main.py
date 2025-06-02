"""
Main FastAPI application for the frontend-engine service.
"""
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.configuration import config
from . import health
from .routes.membership import router as membership_router

app = FastAPI(
    title="SpaceNew Frontend API",
    description="Frontend API for the SpaceNew platform",
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
app.include_router(health.router)
app.include_router(membership_router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for all unhandled exceptions"""
    # Log the exception
    print(f"Unhandled exception: {exc}")
    
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

# Startup and shutdown events
@app.on_event("startup")
async def startup():
    """Execute tasks on application startup"""
    print(f"Starting application in {config.environment} mode")

@app.on_event("shutdown")
async def shutdown():
    """Execute tasks on application shutdown"""
    print("Shutting down application")
