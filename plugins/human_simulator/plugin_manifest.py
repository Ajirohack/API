"""
Plugin manifest for Human Simulator plugin.
"""
manifest = {
    "name": "human_simulator",
    "version": "0.1.0",
    "description": "Simulates human admissions and calendar events.",
    "routes_module": "api.plugins.human_simulator.routes",
    "models_module": "api.plugins.human_simulator.models",
    "migrations_path": "api/plugins/human_simulator/migrations",
    "workflows_path": "api/plugins/human_simulator/workflows",
    "health_endpoint": "/api/plugins/human_simulator/health",
    "ui_components": [
        {"name": "AdmissionDashboard", "path": "client/plugins/human_simulator/AdmissionDashboard.tsx", "description": "UI for managing admissions"},
        {"name": "CalendarDashboard", "path": "client/plugins/human_simulator/CalendarDashboard.tsx", "description": "UI for managing calendar events"}
    ]
}
