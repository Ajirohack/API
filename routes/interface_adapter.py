"""
Conversational Interface Adapter API for Archivist
- Receives chat messages from UI and routes to event bus
- Streams responses from event bus to UI
"""
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, Header, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from core.integration.interface_adapters import ConversationalAdapter
from core.enhanced_event_bus import EventBus
import asyncio
from typing import List, Dict, Any, Optional
import time
import uuid
from database.connection import get_db_session
from sqlalchemy.orm import Session
from api.security import validate_ws_token, get_ws_user

router = APIRouter(tags=["interface"])
event_bus = EventBus()
adapter = ConversationalAdapter(event_bus)

# In-memory message history and queue for demonstration
message_history: List[dict] = []
message_queue: List[dict] = []
# Track authenticated WebSocket connections
authenticated_connections: Dict[str, Dict[str, Any]] = {}

@router.post("/api/interface/chat/send")
async def chat_send(data: dict):
    message = data.get("message")
    user = data.get("user", "anonymous")
    if not message:
        return JSONResponse({"error": "No message provided"}, status_code=400)
    # Store in history and queue
    msg_obj = {"user": user, "content": message, "timestamp": time.time()}
    message_history.append(msg_obj)
    message_queue.append(msg_obj)
    adapter.receive(message)
    return {"status": "ok"}

@router.get("/api/interface/chat/history")
async def chat_history():
    # Return the last 50 messages
    return {"history": message_history[-50:]}

@router.websocket("/api/interface/chat/ws")
async def chat_ws(websocket: WebSocket, db: Session = Depends(get_db_session)):
    """
    WebSocket endpoint for real-time chat with JWT authentication.
    Client must provide a valid JWT token as a query parameter or in the Authorization header.
    """
    # Extract token from query parameters or headers
    token = websocket.query_params.get("token") or websocket.headers.get("Authorization", "")
    if token.startswith("Bearer "):
        token = token[7:]
        
    if not token:
        # Close with unauthorized status if no token provided
        await websocket.close(code=1008, reason="Unauthorized: No token provided")
        return
        
    try:
        # Validate token and get user information
        user_payload = await get_ws_user(token, db)
        user_id = user_payload.get("sub")
        if not user_id:
            await websocket.close(code=1008, reason="Unauthorized: Invalid user ID")
            return
            
        # Accept the connection now that we've validated the token
        await websocket.accept()
        
        # Generate a unique connection ID and track it
        connection_id = str(uuid.uuid4())
        authenticated_connections[connection_id] = {
            "user_id": user_id,
            "connected_at": time.time(),
            "user_payload": user_payload,
            "websocket": websocket
        }
        
        try:
            while True:
                # Send queued messages in real-time
                if message_queue:
                    msg = message_queue.pop(0)
                    await websocket.send_json(msg)
                    
                # Handle incoming messages
                try:
                    # Set a short timeout to avoid blocking
                    text = await asyncio.wait_for(websocket.receive_text(), timeout=0.5)
                    # Process the message
                    message = {"user_id": user_id, "content": text, "timestamp": time.time()}
                    message_history.append(message)
                    # Send to event bus for processing
                    adapter.receive(text, user_id=user_id)
                except asyncio.TimeoutError:
                    # This is expected, just continue the loop
                    pass
                
                await asyncio.sleep(0.5)  # Small delay to prevent CPU overuse
        except WebSocketDisconnect:
            # Clean up on disconnect
            authenticated_connections.pop(connection_id, None)
    except HTTPException as e:
        # Handle authentication errors
        await websocket.close(code=1008, reason=str(e.detail))
    except Exception as e:
        # Handle unexpected errors
        await websocket.close(code=1011, reason=f"Internal error: {str(e)}")

@router.get("/api/interface/chat/stream")
async def chat_stream():
    async def event_stream():
        last_idx = 0
        # For demo: poll outgoing events
        while True:
            await asyncio.sleep(1)
            events = event_bus.poll('interface.outgoing')
            for event in events:
                if event.get('type') == 'text':
                    yield f"data: {event['content']}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")

# SDK Adapter with API key authentication
@router.post("/api/interface/sdk/command", tags=["sdk"])
async def sdk_command(data: dict, x_api_key: str = Header(None)):
    """
    Execute SDK command. Requires API key authentication.
    ---
    - x_api_key: API key for SDK user
    - data: Command payload
    """
    # TODO: Validate API key, check permissions
    if not x_api_key:
        return JSONResponse({"error": "Missing API key"}, status_code=401)
    command = data.get("command")
    if not command:
        return JSONResponse({"error": "Missing command"}, status_code=400)
    # Placeholder for command execution logic
    try:
        # Simulate command execution
        result = {"executed": True, "command": command}
        return {"status": "executed", "result": result}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# Example usage:
# curl -X POST "http://localhost:8000/api/interface/sdk/command" -H "x-api-key: YOUR_KEY" -d '{"command": "do_something"}'

# Visual Adapter stub
@router.get("/api/interface/visual/dashboard")
async def visual_dashboard():
    # Placeholder for dashboard data
    return {"dashboard": {"status": "ok", "widgets": []}}

# --- Dashboard UI Endpoints ---

@router.get("/api/interface/dashboard/status")
async def dashboard_status():
    """Return system status for dashboard UI (health, metrics, plugin summary)"""
    from api.control_center.monitoring.health_utils import get_system_health_status
    status = get_system_health_status()
    return {"status": "ok", "system": status.get("system"), "plugins": status.get("plugins")}

@router.get("/api/interface/dashboard/plugins")
async def dashboard_plugins():
    """Return plugin health and metadata for dashboard UI"""
    from api.control_center.monitoring.health_utils import get_plugin_health_status
    plugin_health = get_plugin_health_status()
    # Optionally, add more plugin metadata here
    return {"status": "ok", "plugin_health": plugin_health}

@router.websocket("/api/interface/dashboard/plugins/ws")
async def dashboard_plugins_ws(websocket: WebSocket, db: Session = Depends(get_db_session)):
    """WebSocket for real-time plugin health updates with JWT authentication"""
    # Extract token from query parameters or headers
    token = websocket.query_params.get("token") or websocket.headers.get("Authorization", "")
    if token.startswith("Bearer "):
        token = token[7:]
        
    if not token:
        # Close with unauthorized status if no token provided
        await websocket.close(code=1008, reason="Unauthorized: No token provided")
        return
        
    try:
        # Validate token and get user information
        user_payload = await get_ws_user(token, db)
        user_id = user_payload.get("sub")
        
        # Check if user has appropriate role for dashboard access
        user_roles = user_payload.get("roles", [])
        if not any(role in ["admin", "dashboard_user"] for role in user_roles):
            await websocket.close(code=1008, reason="Forbidden: Insufficient permissions")
            return
            
        # Accept the connection now that we've validated the token
        await websocket.accept()
        
        from api.control_center.monitoring.health_utils import get_plugin_health_status
        
        try:
            while True:
                plugin_health = get_plugin_health_status()
                await websocket.send_json({"plugin_health": plugin_health, "timestamp": time.time()})
                await asyncio.sleep(2)
        except WebSocketDisconnect:
            pass
    except HTTPException as e:
        # Handle authentication errors
        await websocket.close(code=1008, reason=str(e.detail))
    except Exception as e:
        # Handle unexpected errors
        await websocket.close(code=1011, reason=f"Internal error: {str(e)}")
