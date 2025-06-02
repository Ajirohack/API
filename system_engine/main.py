"""
Main FastAPI application for the system-engine service.
This service handles backend processes, agents, and workflows.
"""
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.configuration import config
from api.docs import custom_openapi_schema

app = FastAPI(
    title="SpaceNew System API",
    description="System API for the SpaceNew platform's backend processes",
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
from api.system_engine import health
from api.system_engine.routes import agents, workflows
app.include_router(health.router)
app.include_router(agents.router)
app.include_router(workflows.router)
# Will add these as they're implemented
# app.include_router(rag.router)

# Custom OpenAPI schema
app.openapi = lambda: custom_openapi_schema(
    app=app,
    title="SpaceNew System API",
    version="0.1.0"
)

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
    print(f"Starting system-engine in {config.environment} mode")

@app.on_event("shutdown")
async def shutdown():
    """Execute tasks on application shutdown"""
    print("Shutting down system-engine")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "system-engine",
        "version": "0.1.0",
        "status": "online"
    }
