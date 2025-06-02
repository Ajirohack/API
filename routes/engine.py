"""
API endpoints for the Cognitive Synthesis Engine (event processing, inference, synthesis)
"""
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from typing import Any, Dict

router = APIRouter(tags=["engine"])

# Lazy initialization to avoid startup delays
_engine = None

def get_engine():
    """Get the cognitive synthesis engine instance (lazy initialization)."""
    global _engine
    if _engine is None:
        from core.engines.cognitive_synthesis_engine import CognitiveSynthesisEngine
        _engine = CognitiveSynthesisEngine()
    return _engine

@router.post("/engine/event")
def submit_event(event: Dict[str, Any] = Body(...)):
    """Submit an event to the engine's event queue."""
    engine = get_engine()
    engine.event_queue.add_event(event)
    return {"status": "queued", "event": event}

@router.post("/engine/process")
def process_once():
    """Process a single event from the queue (manual trigger)."""
    engine = get_engine()
    result = engine.process()
    return {"status": "processed", "result": result}

@router.post("/engine/start")
def start_engine():
    """Start the autonomous engine cycle."""
    engine.run_autonomous_cycle()
    return {"status": "engine started"}

@router.post("/engine/stop")
def stop_engine():
    """Stop the autonomous engine cycle."""
    engine.stop_autonomous_cycle()
    return {"status": "engine stopped"}

@router.get("/engine/queue_size")
def get_queue_size():
    """Get the current size of the engine event queue."""
    return {"queue_size": len(engine.event_queue.queue)}

@router.get("/engine/last_error")
def get_last_error():
    """Get the last error encountered by the engine."""
    return {"last_error": engine.last_error}

@router.post("/engine/trigger")
def trigger_engine():
    """Manually trigger engine processing (for demo/testing)."""
    engine.process()
    return {"status": "processed"}

@router.get("/engine/queue")
def get_queue():
    """Get the current engine event queue."""
    return {"queue": engine.event_queue.queue}

@router.get("/engine/health")
def engine_health():
    """Get engine health and last error."""
    return {"running": engine.running, "last_error": engine.last_error}
