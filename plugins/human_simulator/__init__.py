"""
Human Simulator Plugin package initialization.
Registers workflows when the plugin is loaded.
"""
from .plugin_manifest import manifest
from .routes import router

# Register Human Simulator workflows
def register_workflows():
    try:
        from api.plugins.human_simulator.workflows.admission_workflow import register_admission_workflow
        register_admission_workflow()
    except ImportError:
        pass

register_workflows()
