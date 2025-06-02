"""
Workflow integration hooks for Financial Business plugin.
Provides event handlers and workflow triggers to integrate with the SpaceNew plugin system.
"""
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import decimal
import json
import os
import asyncio
from pathlib import Path

# Set up logger
logger = logging.getLogger("financial_business.workflow")

class FinancialBusinessWorkflowHooks:
    """
    Workflow hooks for Financial Business integration with SpaceNew plugin system.
    Implements hooks for event subscription, workflow triggers, and context contributions.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize workflow hooks with optional configuration"""
        self.config = config or {}
        self.event_bus = None
        
        # Load workflow definitions
        self.workflows = self._load_workflow_definitions()
        logger.info(f"Financial Business workflow hooks initialized with {len(self.workflows)} workflows")
    
    def _load_workflow_definitions(self) -> List[Dict[str, Any]]:
        """Load workflow definitions from JSON files"""
        workflows = []
        workflows_dir = Path(__file__).parent / "workflows"
        
        if not workflows_dir.exists():
            logger.warning(f"Workflows directory not found: {workflows_dir}")
            return []
            
        for file_path in workflows_dir.glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    workflow = json.load(f)
                    workflows.append(workflow)
                    logger.debug(f"Loaded workflow from {file_path}: {workflow.get('id')}")
            except Exception as e:
                logger.error(f"Error loading workflow from {file_path}: {str(e)}")
                
        return workflows
    
    def register_event_bus(self, event_bus):
        """Register the event bus for publishing/subscribing to events"""
        self.event_bus = event_bus
        logger.info("Event bus registered with Financial Business workflow hooks")
    
    async def on_transaction_completed(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle transaction completed event
        
        Args:
            transaction_data: Transaction data
            
        Returns:
            Enriched transaction data
        """
        logger.info(f"Processing transaction completion for transaction {transaction_data.get('transaction_id')}")
        
        # Add metadata to transaction data
        transaction_data["processed_at"] = datetime.utcnow().isoformat()
        
        # Determine amount range for metrics
        amount = transaction_data.get("amount", 0)
        if amount < 100:
            transaction_data["amount_range"] = "small"
        elif amount < 1000:
            transaction_data["amount_range"] = "medium"
        else:
            transaction_data["amount_range"] = "large"
        
        # Publish event if available
        if self.event_bus:
            self.event_bus.publish("financial_business.transaction.completed", transaction_data)
            logger.debug("Published transaction.completed event")
        
        return transaction_data
    
    async def on_account_created(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle account created event
        
        Args:
            account_data: Account data
            
        Returns:
            Enriched account data
        """
        logger.info(f"Processing account creation for account {account_data.get('account_number')}")
        
        # Publish event if available
        if self.event_bus:
            self.event_bus.publish("financial_business.account.created", account_data)
            logger.debug("Published account.created event")
        
        return account_data
    
    async def on_admin_action(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle admin action event
        
        Args:
            action_data: Admin action data
            
        Returns:
            Processed action data
        """
        logger.info(f"Processing admin action: {action_data.get('action')}")
        
        # Add audit trail
        action_data["audit_trail"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "action_id": f"admin_{action_data.get('action')}_{id(action_data)}"
        }
        
        # Publish event if available
        if self.event_bus:
            self.event_bus.publish("financial_business.admin.action", action_data)
            logger.debug("Published admin.action event")
        
        return action_data
    
    def get_workflow_triggers(self) -> List[Dict[str, Any]]:
        """
        Define workflow triggers that Financial Business provides to the SpaceNew workflow engine
        
        Returns:
            List of workflow trigger definitions
        """
        return [
            {
                "id": "financial_business.transaction.completed",
                "name": "Transaction Completed",
                "description": "Triggered when a transaction is completed",
                "parameters": {
                    "transaction_type": {
                        "type": "string",
                        "enum": ["transfer", "deposit", "withdrawal"],
                        "description": "Type of transaction"
                    },
                    "amount_threshold": {
                        "type": "number",
                        "default": 0,
                        "description": "Minimum amount to trigger the workflow"
                    }
                }
            },
            {
                "id": "financial_business.account.created",
                "name": "Account Created",
                "description": "Triggered when a new account is created",
                "parameters": {
                    "account_type": {
                        "type": "string",
                        "enum": ["checking", "savings", "investment"],
                        "description": "Type of account created"
                    }
                }
            },
            {
                "id": "financial_business.admin.login",
                "name": "Admin Login",
                "description": "Triggered when an admin user logs in",
                "parameters": {
                    "role": {
                        "type": "string",
                        "enum": ["admin", "manager", "auditor"],
                        "description": "Role of the admin user"
                    }
                }
            }
        ]
    
    def get_context_contributions(self) -> Dict[str, Any]:
        """
        Define context data that Financial Business contributes to the global app context
        
        Returns:
            Dict of context contributions
        """
        return {
            "financial_business": {
                "version": "1.0.0",
                "capabilities": ["account_management", "transfers", "admin_portal"],
                "supported_currencies": ["USD", "EUR", "GBP", "JPY"],
                "workflows": [w.get("id") for w in self.workflows]
            }
        }
    
    # Helper class for JSON serialization of decimal values
    class DecimalEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, decimal.Decimal):
                return float(obj)
            return super(FinancialBusinessWorkflowHooks.DecimalEncoder, self).default(obj)
