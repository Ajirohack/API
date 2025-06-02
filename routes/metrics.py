"""
Metrics endpoints for monitoring and analytics.
"""
from fastapi import APIRouter, Depends, Query, Response, WebSocket
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models import SuccessResponse, DataResponse, PaginationParams
from database.connection import get_db_session
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Gauge, Counter, Histogram
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Gauge, Counter, Histogram
import psutil
import asyncio

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/metrics")
def metrics():
    """Expose Prometheus metrics for scraping."""
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)

# Example: business and system metrics summary
@router.get("/metrics/summary")
def metrics_summary():
    # Example: return system and business metrics
    summary = {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "active_users": 42,  # Placeholder
        "messages_today": 1234,  # Placeholder
    }
    return summary

# Example: Prometheus health gauge
HEALTH_GAUGE = Gauge('archivist_health_status', 'Overall health status (1=healthy, 0=unhealthy)')
@router.get("/metrics/health")
def metrics_health():
    # For demo, always healthy
    HEALTH_GAUGE.set(1)
    return {"status": "healthy"}

# Business metrics
MESSAGES_SENT = Counter('archivist_messages_sent', 'Number of chat messages sent')
SDK_COMMANDS_EXECUTED = Counter('archivist_sdk_commands_executed', 'Number of SDK commands executed')
RESPONSE_TIME = Histogram('archivist_response_time_seconds', 'API response time in seconds')

@router.get("/metrics/dashboard")
def metrics_dashboard():
    """Return metrics for dashboard UI (business, performance, system)"""
    return {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "messages_sent": MESSAGES_SENT._value.get(),
        "sdk_commands": SDK_COMMANDS_EXECUTED._value.get(),
        "response_time_avg": RESPONSE_TIME._sum.get() / RESPONSE_TIME._count.get() if RESPONSE_TIME._count.get() else 0
    }

@router.websocket("/metrics/dashboard/ws")
async def metrics_dashboard_ws(websocket: WebSocket):
    """WebSocket for real-time metrics updates"""
    await websocket.accept()
    try:
        while True:
            metrics = {
                "cpu": psutil.cpu_percent(),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage('/').percent,
                "messages_sent": MESSAGES_SENT._value.get(),
                "sdk_commands": SDK_COMMANDS_EXECUTED._value.get(),
                "response_time_avg": RESPONSE_TIME._sum.get() / RESPONSE_TIME._count.get() if RESPONSE_TIME._count.get() else 0
            }
            await websocket.send_json(metrics)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass

@router.get("/usage", response_model=DataResponse)
async def get_usage_metrics(
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    db: Session = Depends(get_db_session)
):
    """Get API usage metrics for a time period"""
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=7)
    if not end_date:
        end_date = datetime.utcnow()

    # TODO: Implement actual metrics collection
    # This is a placeholder that returns sample data
    metrics = {
        "total_requests": 1000,
        "average_response_time": 150,  # ms
        "error_rate": 0.02,
        "endpoints": {
            "/api/health": 100,
            "/api/users": 250,
            "/api/documents": 650
        }
    }
    
    return DataResponse(
        status="success",
        message="Usage metrics retrieved successfully",
        data=metrics
    )

@router.get("/performance", response_model=DataResponse)
async def get_performance_metrics(db: Session = Depends(get_db_session)):
    """Get current system performance metrics"""
    import psutil
    
    cpu = psutil.cpu_percent(interval=1, percpu=True)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    metrics = {
        "cpu": {
            "overall": sum(cpu) / len(cpu),
            "per_cpu": cpu
        },
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }
    }
    
    return DataResponse(
        status="success",
        message="Performance metrics retrieved successfully",
        data=metrics
    )

@router.get("/errors", response_model=DataResponse)
async def get_error_metrics(
    timeframe: str = Query("1h", description="Timeframe (1h, 24h, 7d, 30d)"),
    db: Session = Depends(get_db_session)
):
    """Get error metrics for a specific timeframe"""
    # TODO: Implement actual error metrics collection
    # This is a placeholder that returns sample data
    metrics = {
        "total_errors": 45,
        "error_types": {
            "4xx": 30,
            "5xx": 15
        },
        "most_common": [
            {"status": 404, "count": 20, "endpoint": "/api/missing"},
            {"status": 500, "count": 10, "endpoint": "/api/error"}
        ]
    }
    
    return DataResponse(
        status="success",
        message="Error metrics retrieved successfully",
        data=metrics
    )
