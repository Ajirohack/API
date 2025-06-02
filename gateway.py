"""
API Gateway for routing, authentication, context, event-driven integration, and real-time WebSocket support.
Production-optimized: structured logging, error handling, OpenAPI docs, configuration management, and rate limiting.
"""
from fastapi import APIRouter, Request, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Cookie
from fastapi.responses import JSONResponse
from core.logging import log_context
from api.security import get_current_user
from api.models import BaseResponse, ErrorResponse
import time
import asyncio
import uuid
from functools import wraps
from core.enhanced_event_bus import EventBus
import jwt
import os
import redis
from config.configuration import config
import logging
from fastapi.openapi.utils import get_openapi
from starlette.websockets import WebSocketState

router = APIRouter()

# Structured logging setup
logger = logging.getLogger("api.gateway")

# Redis-backed rate limiting
RATE_LIMITS = {
    "admin": 1000,
    "user": 100,
    "guest": 20
}

def rate_limiter(user_id: str, role: str):
    now = int(time.time() / 60)
    key = f"ratelimit:{role}:{user_id}:{now}"
    limit = RATE_LIMITS.get(role, 20)
    count = redis_client.get(key)
    if count is None:
        redis_client.set(key, 1, ex=60)
        count = 1
    else:
        count = int(count) + 1
        redis_client.set(key, count, ex=60)
    if count > limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    return limit, count

def api_response(data=None, message="", status_code=200):
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "success" if status_code < 400 else "error",
            "data": data,
            "message": message,
            "errors": [] if status_code < 400 else [message],
        },
    )

# --- Error Handling Middleware ---
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

# Example: global exception handler for improved error context
app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return PlainTextResponse(str(exc), status_code=500)

# --- OpenAPI Documentation Customization ---
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Space-0.2 API Gateway",
        version="1.0.0",
        description="API Gateway for Space-0.2: routing, authentication, event-driven integration, and real-time WebSocket support.",
        routes=router.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema
app.openapi = custom_openapi

# --- Configuration Management ---
# Use environment variables and config files for secrets, feature flags, and environment-specific settings.
# Example: os.environ.get("ENV", "development")

# --- API Versioning Example ---
API_VERSION = "v1"

# Centralized routing logic (stub for future expansion)
def route_request(path: str, method: str, data=None, user=None):
    # Here you would dispatch to the correct handler based on path/method
    # For now, just echo the request for demonstration
    return {
        "path": path,
        "method": method,
        "data": data,
        "user": user,
        "routed": True
    }

# Centralized request entry point with auth and rate limiting
@router.api_route(f"/api/{API_VERSION}/gateway/{{path:path}}", methods=["GET", "POST", "PUT", "DELETE"], tags=["gateway"], summary="Centralized API Gateway Endpoint", response_description="Routed API response")
def gateway(request: Request, user=Depends(get_current_user)):
    """Centralized API gateway endpoint with authentication, rate limiting, and routing."""
    user_id = user.get("user_id", "anonymous")
    role = user.get("role", "guest")
    session_id = request.headers.get("X-Session-Id")
    request_id = request.headers.get("X-Request-Id")
    log_context("Gateway request received", user_id, session_id, request_id)
    # Redis-backed rate limiting
    limit, count = rate_limiter(user_id, role)
    # Centralized routing logic
    path = request.path_params.get("path", "")
    method = request.method
    data = None
    if method in ("POST", "PUT"):
        try:
            data = request.json() if hasattr(request, 'json') else None
        except Exception:
            data = None
    result = route_request(path, method, data, user)
    response = api_response(result, message="Gateway routed request")
    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = str(max(0, limit - count))
    return response

# --- WebSocket Endpoint Preparation ---
event_bus = EventBus()

# Redis for connection tracking and pub/sub
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL)

# JWT secret and algorithm
SECRET_KEY = config.get("auth", {}).get("secret_key", "CHANGE_THIS_TO_A_RANDOM_SECRET_IN_PRODUCTION")
ALGORITHM = "HS256"

# Track active WebSocket connections
active_ws_connections = {}

# Import the enhanced JWT validation function from security.py
from api.security import validate_ws_token, get_ws_user
from database.connection import get_db_session
import asyncio

# CSRF token validation utility
def validate_csrf(websocket: WebSocket, csrf_token: str):
    cookie_token = websocket.cookies.get("csrftoken")
    if not cookie_token or cookie_token != csrf_token:
        raise HTTPException(status_code=403, detail="CSRF token invalid or missing.")

# Example: channel authorization check
async def is_user_authorized_for_channel(user_id, channel_id, db):
    # Replace with real DB check for user-channel membership/role
    # For demo, allow all channels
    return True

@router.websocket(f"/api/{API_VERSION}/ws")
async def websocket_endpoint(websocket: WebSocket, csrf_token: Optional[str] = None):
    """Production-ready WebSocket endpoint with JWT authentication and Redis pub/sub integration."""
    # Accept token in query or header
    token = websocket.query_params.get("token") or websocket.headers.get("Authorization")
    if not token:
        await websocket.close(code=1008, reason="Unauthorized: No token provided")
        return
        
    if token.startswith("Bearer "):
        token = token[7:]
        
    # Get database session
    db = next(get_db_session())
    
    try:
        # Validate token using our enhanced security module
        user_payload = validate_ws_token(token, db)
        user_id = user_payload.get("sub")
        roles = user_payload.get("roles", [])
        
        if not user_id:
            await websocket.close(code=1008, reason="Unauthorized: Invalid token payload")
            return
            
        # CSRF protection (for browser clients)
        if csrf_token:
            try:
                validate_csrf(websocket, csrf_token)
            except HTTPException as e:
                await websocket.close(code=4401, reason=e.detail)
                return
        
        # Accept the WebSocket connection
        await websocket.accept()
        
        # Track connection with more metadata
        connection_id = str(uuid.uuid4())
        active_ws_connections[user_id] = {
            "websocket": websocket,
            "connection_id": connection_id,
            "connected_at": time.time(),
            "user_id": user_id,
            "roles": roles,
            "last_activity": time.time()
        }
        
        # Log connection
        logger.info(f"WebSocket connection established for user {user_id}", 
                   extra={"user_id": user_id, "connection_id": connection_id})
        
        # Subscribe to user-specific Redis pub/sub channel
        pubsub = redis_client.pubsub()
        channel = f"user:{user_id}:realtime"
        pubsub.subscribe(channel)
        
        # Also subscribe to role-based channels
        for role in roles:
            role_channel = f"role:{role}:broadcasts"
            pubsub.subscribe(role_channel)
        
        try:
            while True:
                # Check for Redis messages
                message = pubsub.get_message(timeout=1)
                if message and message["type"] == "message":
                    await websocket.send_text(message["data"].decode())
                
                # Handle incoming messages from client
                try:
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                    # Channel-specific authorization example
                    import json
                    msg = json.loads(data)
                    if msg.get("type") == "join_channel":
                        channel_id = msg.get("channel_id")
                        if not await is_user_authorized_for_channel(user_id, channel_id, db):
                            await websocket.send_json({"type": "error", "error": "Not authorized for this channel."})
                            continue
                    # Update last activity timestamp
                    active_ws_connections[user_id]["last_activity"] = time.time()
                    
                    # Process message (could be a ping, command, etc.)
                    await process_ws_message(data, user_id, websocket)
                except asyncio.TimeoutError:
                    # This is expected behavior when client hasn't sent anything
                    pass
                except Exception as msg_err:
                    # Send error back to client
                    error_msg = {"error": str(msg_err)}
                    await websocket.send_json(error_msg)
                    logger.error(f"Error processing WebSocket message: {str(msg_err)}", 
                                exc_info=True, extra={"user_id": user_id})
                # Implement ping/pong for connection health check
                if (time.time() - active_ws_connections[user_id]["last_activity"]) > 30:
                    try:
                        # Send ping to verify connection is still alive
                        await websocket.send_json({"type": "ping", "timestamp": time.time()})
                        # Reset last activity timestamp
                        active_ws_connections[user_id]["last_activity"] = time.time()
                    except Exception:
                        # Connection may be dead, break the loop
                        break
                
                # Small delay to prevent CPU overuse
                await asyncio.sleep(0.05)
                
        except WebSocketDisconnect:
            # Normal disconnection
            logger.info(f"WebSocket disconnected for user {user_id}", 
                       extra={"user_id": user_id, "connection_id": connection_id})
        except Exception as e:
            # Unexpected error
            logger.error(f"WebSocket error: {str(e)}", exc_info=True, 
                        extra={"user_id": user_id, "connection_id": connection_id})
            if websocket.application_state != WebSocketState.DISCONNECTED:
                await websocket.close(code=1011, reason=f"Internal error: {str(e)}")
        finally:
            # Clean up subscriptions and tracked connections
            pubsub.unsubscribe(channel)
            for role in roles:
                pubsub.unsubscribe(f"role:{role}:broadcasts")
            pubsub.close()
            active_ws_connections.pop(user_id, None)
    except HTTPException as e:
        # Authentication error
        await websocket.close(code=1008, reason=str(e.detail))
        logger.warning(f"WebSocket authentication failed: {e.detail}")
    except Exception as e:
        # Unexpected error during setup
        logger.error(f"WebSocket setup error: {str(e)}", exc_info=True)
        await websocket.close(code=1011, reason=f"Internal error: {str(e)}")
    finally:
        # Ensure database session is closed
        db.close()
        
async def process_ws_message(data: str, user_id: str, websocket: WebSocket):
    """Process incoming WebSocket messages from clients"""
    try:
        # Try to parse as JSON
        import json
        message = json.loads(data)
        
        # Handle message types
        if message.get("type") == "ping":
            # Respond to ping with pong
            await websocket.send_json({"type": "pong", "timestamp": time.time()})
        elif message.get("type") == "command":
            # Handle commands
            command = message.get("command")
            command_id = message.get("command_id")
            # Process command (placeholder for actual implementation)
            response = {"type": "command_result", "command_id": command_id, "status": "processed"}
            await websocket.send_json(response)
        else:
            # Unknown message type
            await websocket.send_json({"type": "error", "error": "Unknown message type"})
    except json.JSONDecodeError:
        # Not JSON, treat as plain text
        # Echo back the message (placeholder for actual implementation)
        await websocket.send_text(f"Received: {data}")
