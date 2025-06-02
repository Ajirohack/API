"""
Logging configuration and utilities.
"""
import logging
import logging.handlers
import os
import json
from datetime import datetime
from typing import Any, Dict

class JSONFormatter(logging.Formatter):
    """
    Custom formatter for JSON-structured logs.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if they exist
        if hasattr(record, "extra"):
            log_data.update(record.extra)
            
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": str(record.exc_info[0].__name__),
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
            
        return json.dumps(log_data)

def setup_logging(
    log_level: str = "INFO",
    log_file: str = "api.log",
    max_size: int = 10_000_000,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Configure application logging with both file and console handlers.
    
    Args:
        log_level: Minimum log level to record
        log_file: Path to the log file
        max_size: Maximum size of each log file in bytes
        backup_count: Number of backup files to keep
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Create JSON formatter
    json_formatter = JSONFormatter()
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=max_size,
        backupCount=backup_count
    )
    file_handler.setFormatter(json_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    root_logger.addHandler(console_handler)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

class LoggerAdapter(logging.LoggerAdapter):
    """
    Custom logger adapter that adds context to log messages.
    """
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Process the logging message and keyword arguments."""
        extra = kwargs.get("extra", {})
        if self.extra:
            extra.update(self.extra)
        kwargs["extra"] = extra
        return msg, kwargs

def get_request_logger(request_id: str) -> LoggerAdapter:
    """
    Get a logger that includes request context.
    
    Args:
        request_id: Unique request identifier
        
    Returns:
        LoggerAdapter instance with request context
    """
    logger = get_logger("api.request")
    return LoggerAdapter(logger, {"request_id": request_id})
