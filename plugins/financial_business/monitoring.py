"""
Monitoring utilities for Financial Business Plugin
"""
import logging
from typing import Dict, Any, Optional

# Set up logger
logger = logging.getLogger("financial_business.monitoring")

# Mock metrics classes for when Prometheus is not available
class MockCounter:
    def __init__(self, name: str, description: str, labels: Optional[list] = None):
        self.name = name
        self.description = description
        self.labels_schema = labels or []
        self.value = 0
        logger.info(f"Created mock counter: {name}")
    
    def inc(self, value: float = 1):
        self.value += value
        logger.debug(f"Incremented {self.name}: {self.value}")
    
    def labels(self, **kwargs):
        return self

class MockSummary:
    def __init__(self, name: str, description: str, labels: Optional[list] = None):
        self.name = name
        self.description = description
        self.labels_schema = labels or []
        self.values = []
        logger.info(f"Created mock summary: {name}")
    
    def observe(self, value: float):
        self.values.append(value)
        logger.debug(f"Observed {self.name}: {value}")
    
    def labels(self, **kwargs):
        return self

class MockHistogram:
    def __init__(self, name: str, description: str, labels: Optional[list] = None):
        self.name = name
        self.description = description
        self.labels_schema = labels or []
        self.values = []
        logger.info(f"Created mock histogram: {name}")
    
    def observe(self, value: float):
        self.values.append(value)
        logger.debug(f"Observed {self.name}: {value}")
    
    def labels(self, **kwargs):
        return self

class MockGauge:
    def __init__(self, name: str, description: str, labels: Optional[list] = None):
        self.name = name
        self.description = description
        self.labels_schema = labels or []
        self.value = 0
        logger.info(f"Created mock gauge: {name}")
    
    def set(self, value: float):
        self.value = value
        logger.debug(f"Set {self.name}: {value}")
        
    def inc(self, value: float = 1):
        self.value += value
        logger.debug(f"Incremented {self.name}: {self.value}")
        
    def dec(self, value: float = 1):
        self.value -= value
        logger.debug(f"Decremented {self.name}: {self.value}")
    
    def labels(self, **kwargs):
        return self

# Try to import real Prometheus clients, fall back to mocks if not available
try:
    from prometheus_client import Counter, Histogram, Summary, Gauge
    PROMETHEUS_AVAILABLE = True
    logger.info("Using Prometheus metrics")
except ImportError:
    Counter = MockCounter
    Histogram = MockHistogram
    Summary = MockSummary
    Gauge = MockGauge
    PROMETHEUS_AVAILABLE = False
    logger.warning("Prometheus client not available, using mock metrics")

# Financial business specific metrics
FINANCIAL_TRANSFER_COUNT = Counter('financial_transfer_count', 'Number of financial transfers')
FINANCIAL_TRANSFER_AMOUNT = Summary('financial_transfer_amount', 'Transfer amounts')
FINANCIAL_TRANSFER_ERRORS = Counter('financial_transfer_errors', 'Transfer errors', ['error_type'])
DB_QUERY_LATENCY = Summary('db_query_latency_seconds', 'Database query latency')
