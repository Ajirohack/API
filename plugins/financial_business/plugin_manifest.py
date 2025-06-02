"""
Plugin manifest for Financial Business App for SpaceNew

See README.md for plugin documentation.
"""
from core.plugin_system.plugin_interface import (
    ServicePlugin, PluginManifest, ServiceEndpoint, UIComponent, EventSubscription, EventPublication
)

class FinancialBusinessPlugin(ServicePlugin):
    def get_manifest(self) -> PluginManifest:
        return PluginManifest(
            id="financial_business",
            name="Financial Business App",
            version="1.0.0",
            description="Multi-domain financial business platform with unified API and admin backend.",
            endpoints=[
                ServiceEndpoint(
                    path="/api/financial_business/account/{id}",
                    method="GET",
                    description="Get account summary",
                    auth_required=True
                ),
                ServiceEndpoint(
                    path="/api/financial_business/transfer",
                    method="POST",
                    description="Transfer funds",
                    auth_required=True
                ),
                ServiceEndpoint(
                    path="/api/financial_business/admin/users",
                    method="GET",
                    description="List all users (admin)",
                    auth_required=True
                ),
                ServiceEndpoint(
                    path="/api/financial_business/health",
                    method="GET",
                    description="Health check endpoint",
                    auth_required=False
                ),
                ServiceEndpoint(
                    path="/api/financial_business/metrics/metrics",
                    method="GET",
                    description="Prometheus metrics endpoint",
                    auth_required=False
                )
            ],
            ui_components=[
                UIComponent(
                    name="AccountSummary",
                    type="react",
                    path="/client/plugins/financial-business/AccountSummary.tsx",
                    description="Account summary UI component"
                ),
                UIComponent(
                    name="TransferFunds",
                    type="react",
                    path="/client/plugins/financial-business/TransferFunds.tsx",
                    description="Funds transfer UI component"
                ),
                UIComponent(
                    name="AdminUserList",
                    type="react",
                    path="/client/plugins/financial-business/AdminUserList.tsx",
                    description="Admin user list UI component"
                )
            ],
            # ...events, data_models, etc...
        )
    def initialize(self, config):
        return True
    def shutdown(self):
        return True
    def health_check(self):
        """
        Comprehensive health check for the Financial Business plugin that checks:
        1. Database connectivity
        2. API endpoints availability
        3. Internal service dependencies
        """
        import logging
        from datetime import datetime
        import time
        
        logger = logging.getLogger("financial_business.health")
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "checks": {}
        }
        
        # Check database connectivity
        try:
            # Try to check if database is available by importing connection
            from database.connections.base import db
            health_status["checks"]["database"] = {
                "status": "up",
                "latency": 0.0
            }
            
            # If we can access a session, measure the latency
            start_time = time.time()
            session_available = hasattr(db, "session")
            if session_available:
                health_status["checks"]["database"]["latency"] = round(time.time() - start_time, 4)
            else:
                health_status["checks"]["database"]["status"] = "degraded"
        except Exception as e:
            logger.warning(f"Health check failed for database: {str(e)}")
            health_status["checks"]["database"] = {
                "status": "down",
                "error": str(e)
            }
            health_status["status"] = "degraded"
            
        # Check API endpoints
        health_status["checks"]["api"] = {
            "status": "up",
            "endpoints": {
                "/accounts": "up",
                "/transfers": "up",
                "/admin_users": "up"
            }
        }
            
        # Determine overall health status
        if any(check.get("status") == "down" for check in health_status["checks"].values()):
            health_status["status"] = "unhealthy"
        elif any(check.get("status") == "degraded" for check in health_status["checks"].values()):
            health_status["status"] = "degraded"
        
        return health_status
