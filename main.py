"""
Main entry point for the SpaceNew API
Registers all API routes and configures middleware
"""
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from routes import auth, health, metrics, plugin_system
from core.logging import setup_logging
from core.middleware.logging import RequestLoggingMiddleware
from config.settings import settings

# Configure logging
setup_logging(
    log_level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE
)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events for the application
    """
    # Startup
    logger.info("Starting SpaceNew API...")
    yield
    # Shutdown
    logger.info("Shutting down SpaceNew API...")

# Initialize FastAPI app
app = FastAPI(
    title="SpaceNew API",
    version=settings.API_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Custom exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "code": exc.status_code
        },
    )

# Register routers
app.include_router(auth.router, prefix="/api")
app.include_router(health.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")
# app.include_router(engine.router, prefix="/api")  # Temporarily disabled
app.include_router(plugin_system.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        workers=4
    )
