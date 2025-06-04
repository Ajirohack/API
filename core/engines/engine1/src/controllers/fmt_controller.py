"""
Format Template Controller for managing template operations
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class FMTController:
    """
    Controller class for Format Template operations
    """
    
    def __init__(self):
        """Initialize the FMT controller"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("FMT Controller initialized")
    
    def apply_template(self, template_str: str, variables: Dict[str, Any]) -> str:
        """
        Apply variables to a format template
        
        Args:
            template_str: The template string with placeholders
            variables: Dictionary of variables to substitute
            
        Returns:
            Formatted string with variables applied
        """
        try:
            return template_str.format(**variables)
        except KeyError as e:
            self.logger.error(f"Missing variable in template: {e}")
            return f"Error: Missing variable {e}"
        except Exception as e:
            self.logger.error(f"Error applying template: {e}")
            return f"Error applying template: {str(e)}"
    
    def validate_template(self, template_str: str) -> Dict[str, Any]:
        """
        Validate a template string and extract required variables
        
        Args:
            template_str: The template string to validate
            
        Returns:
            Dictionary with validation results
        """
        import re
        
        # Extract variable names from curly braces
        var_pattern = r'\{([^{}]*)\}'
        matches = re.findall(var_pattern, template_str)
        
        required_vars = []
        for match in matches:
            # Remove format specifiers
            var_name = match.split(':')[0].strip()
            if var_name and var_name not in required_vars:
                required_vars.append(var_name)
        
        return {
            "is_valid": True,
            "required_variables": required_vars
        }
