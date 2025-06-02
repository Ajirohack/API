"""
Metrics endpoint for Financial Business Plugin
"""
from fastapi import APIRouter
from starlette.responses import Response
import logging

# Import our monitoring module
from .monitoring import PROMETHEUS_AVAILABLE

router = APIRouter()
logger = logging.getLogger("financial_business.metrics")

@router.get("/metrics", summary="Prometheus metrics endpoint for Financial Business Plugin")
def metrics():
    """Returns Prometheus metrics for the Financial Business Plugin"""
    if PROMETHEUS_AVAILABLE:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
    else:
        logger.warning("Prometheus client not available, returning empty metrics")
        return {"metrics": "Prometheus client not available"}
