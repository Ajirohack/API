"""
Logging middleware for request/response tracking.
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import Message

from core.logging import get_request_logger

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging request and response details.
    """
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Get logger with request context
        logger = get_request_logger(request_id)
        
        # Log request
        await self._log_request(request, logger)
        
        # Process request and measure timing
        start_time = time.time()
        try:
            response = await call_next(request)
            # Log response
            await self._log_response(response, request, time.time() - start_time, logger)
            return response
        except Exception as e:
            # Log error
            logger.error(
                "Request failed",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            raise
    
    async def _log_request(self, request: Request, logger: Callable) -> None:
        """Log request details"""
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.json()
            except:
                body = await request.body()
        
        logger.info(
            f"{request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_host": request.client.host if request.client else None,
                "body": body
            }
        )
    
    async def _log_response(
        self,
        response: Response,
        request: Request,
        duration: float,
        logger: Callable
    ) -> None:
        """Log response details"""
        logger.info(
            f"Response {response.status_code}",
            extra={
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "content_type": response.headers.get("content-type"),
                "content_length": response.headers.get("content-length")
            }
        )
