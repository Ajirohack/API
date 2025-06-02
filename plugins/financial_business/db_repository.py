"""
Database repository for Financial Business plugin.
Provides database access methods for all Financial Business entities.
"""
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import logging
from decimal import Decimal
import uuid

# Configure logging
logger = logging.getLogger("financial_business.db.repository")

class FinancialBusinessRepository:
    """Database repository for Financial Business plugin that handles all data operations"""
    
    def __init__(self, session):
        """Initialize the repository with a database session"""
        self.session = session
    
    # Account Methods
    
    async def get_account(self, account_id: int) -> Optional[Dict[str, Any]]:
        """
        Get account by ID
        
        Args:
            account_id: Account ID
            
        Returns:
            Account record or None if not found
        """
        try:
            from . import models
            result = await self.session.get(models.Account, account_id)
            
            if not result:
                return None
                
            return self._account_to_dict(result)
            
        except Exception as e:
            logger.error(f"Error retrieving account {account_id}: {str(e)}")
            raise
    
    async def list_accounts(self, owner_id: Optional[int] = None, 
                            limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List accounts with optional filtering
        
        Args:
            owner_id: Optional owner ID filter
            limit: Maximum records to return
            offset: Pagination offset
            
        Returns:
            List of account records
        """
        try:
            from sqlalchemy import select
            from . import models
            
            # Build query based on filters
            query = select(models.Account)
            if owner_id is not None:
                query = query.where(models.Account.owner_id == owner_id)
                
            # Add pagination
            query = query.offset(offset).limit(limit)
            
            # Execute query
            result = await self.session.execute(query)
            accounts = result.scalars().all()
            
            # Convert to dictionaries
            return [self._account_to_dict(account) for account in accounts]
            
        except Exception as e:
            logger.error(f"Error listing accounts: {str(e)}")
            raise
    
    async def create_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new account
        
        Args:
            account_data: Account data
            
        Returns:
            Created account record
        """
        try:
            from . import models
            
            # Generate account number if not provided
            if "account_number" not in account_data:
                account_data["account_number"] = f"ACC{uuid.uuid4().hex[:8].upper()}"
                
            # Set defaults
            if "currency" not in account_data:
                account_data["currency"] = "USD"
                
            if "account_type" not in account_data:
                account_data["account_type"] = "checking"
                
            if "status" not in account_data:
                account_data["status"] = "active"
                
            # Create account object
            account = models.Account(
                account_number=account_data["account_number"],
                balance=account_data["balance"],
                currency=account_data["currency"],
                owner_id=account_data["owner_id"],
                account_type=account_data.get("account_type", "checking"),
                status=account_data.get("status", "active"),
                metadata=account_data.get("metadata")
            )
            
            # Add to session and commit
            self.session.add(account)
            await self.session.commit()
            await self.session.refresh(account)
            
            # Audit the creation
            await self._audit_log(
                action="create",
                entity_type="account",
                entity_id=str(account.id),
                actor_id=account_data.get("created_by"),
                actor_type="user",
                details={"account_number": account.account_number}
            )
            
            return self._account_to_dict(account)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating account: {str(e)}")
            raise
    
    async def update_account(self, account_id: int, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an account
        
        Args:
            account_id: Account ID
            account_data: Account data to update
            
        Returns:
            Updated account record
        """
        try:
            from . import models
            
            # Get the account
            account = await self.session.get(models.Account, account_id)
            if not account:
                raise ValueError(f"Account {account_id} not found")
                
            # Update fields
            if "balance" in account_data:
                account.balance = account_data["balance"]
                
            if "status" in account_data:
                account.status = account_data["status"]
                
            if "metadata" in account_data:
                account.metadata = account_data["metadata"]
                
            # Commit changes
            await self.session.commit()
            await self.session.refresh(account)
            
            # Audit the update
            await self._audit_log(
                action="update",
                entity_type="account",
                entity_id=str(account.id),
                actor_id=account_data.get("updated_by"),
                actor_type="user",
                details={"updated_fields": list(account_data.keys())}
            )
            
            return self._account_to_dict(account)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating account {account_id}: {str(e)}")
            raise
    
    # Transaction Methods
    
    async def create_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new transaction
        
        Args:
            transaction_data: Transaction data
            
        Returns:
            Created transaction record
        """
        try:
            from . import models
            
            # Generate transaction reference
            transaction_ref = transaction_data.get("transaction_ref") or f"TXN{uuid.uuid4().hex[:12].upper()}"
            
            # Create transaction object
            transaction = models.Transaction(
                transaction_ref=transaction_ref,
                source_account_id=transaction_data.get("source_account_id"),
                destination_account_id=transaction_data.get("destination_account_id"),
                amount=transaction_data["amount"],
                currency=transaction_data["currency"],
                transaction_type=transaction_data["transaction_type"],
                status=transaction_data.get("status", "pending"),
                description=transaction_data.get("description"),
                metadata=transaction_data.get("metadata")
            )
            
            # Add to session
            self.session.add(transaction)
            
            # Process the transaction based on type
            if transaction.transaction_type == "transfer" and transaction.source_account_id and transaction.destination_account_id:
                await self._process_transfer(
                    source_id=transaction.source_account_id,
                    destination_id=transaction.destination_account_id,
                    amount=transaction.amount,
                    transaction_id=transaction.id
                )
                transaction.status = "completed"
            
            # Commit changes
            await self.session.commit()
            await self.session.refresh(transaction)
            
            # Audit the transaction
            await self._audit_log(
                action="create",
                entity_type="transaction",
                entity_id=str(transaction.id),
                actor_id=transaction_data.get("created_by"),
                actor_type="user",
                details={
                    "transaction_ref": transaction.transaction_ref,
                    "amount": str(transaction.amount),
                    "transaction_type": transaction.transaction_type
                }
            )
            
            return self._transaction_to_dict(transaction)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating transaction: {str(e)}")
            raise
    
    async def get_transaction(self, transaction_id: int) -> Optional[Dict[str, Any]]:
        """
        Get transaction by ID
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Transaction record or None if not found
        """
        try:
            from . import models
            result = await self.session.get(models.Transaction, transaction_id)
            
            if not result:
                return None
                
            return self._transaction_to_dict(result)
            
        except Exception as e:
            logger.error(f"Error retrieving transaction {transaction_id}: {str(e)}")
            raise
    
    async def list_account_transactions(self, account_id: int, 
                                        limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List transactions for an account
        
        Args:
            account_id: Account ID
            limit: Maximum records to return
            offset: Pagination offset
            
        Returns:
            List of transaction records
        """
        try:
            from sqlalchemy import select, or_
            from . import models
            
            # Build query for transactions where the account is either source or destination
            query = select(models.Transaction).where(
                or_(
                    models.Transaction.source_account_id == account_id,
                    models.Transaction.destination_account_id == account_id
                )
            ).order_by(models.Transaction.created_at.desc()).offset(offset).limit(limit)
            
            # Execute query
            result = await self.session.execute(query)
            transactions = result.scalars().all()
            
            # Convert to dictionaries
            return [self._transaction_to_dict(txn) for txn in transactions]
            
        except Exception as e:
            logger.error(f"Error listing transactions for account {account_id}: {str(e)}")
            raise
    
    # Admin User Methods
    
    async def create_admin_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new admin user
        
        Args:
            user_data: Admin user data
            
        Returns:
            Created admin user record
        """
        try:
            from . import models
            
            # Create admin user object
            admin_user = models.AdminUser(
                name=user_data["name"],
                email=user_data["email"],
                role=user_data.get("role", "admin"),
                hashed_password=user_data["hashed_password"],
                is_active=user_data.get("is_active", True),
                permissions=user_data.get("permissions")
            )
            
            # Add to session and commit
            self.session.add(admin_user)
            await self.session.commit()
            await self.session.refresh(admin_user)
            
            # Audit the creation
            await self._audit_log(
                action="create",
                entity_type="admin_user",
                entity_id=str(admin_user.id),
                actor_id=user_data.get("created_by"),
                actor_type="user",
                details={"email": admin_user.email}
            )
            
            return self._admin_user_to_dict(admin_user)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating admin user: {str(e)}")
            raise
    
    async def get_admin_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get admin user by ID
        
        Args:
            user_id: Admin user ID
            
        Returns:
            Admin user record or None if not found
        """
        try:
            from . import models
            result = await self.session.get(models.AdminUser, user_id)
            
            if not result:
                return None
                
            return self._admin_user_to_dict(result)
            
        except Exception as e:
            logger.error(f"Error retrieving admin user {user_id}: {str(e)}")
            raise
    
    async def list_admin_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List admin users
        
        Args:
            limit: Maximum records to return
            offset: Pagination offset
            
        Returns:
            List of admin user records
        """
        try:
            from sqlalchemy import select
            from . import models
            
            # Build query
            query = select(models.AdminUser).offset(offset).limit(limit)
            
            # Execute query
            result = await self.session.execute(query)
            users = result.scalars().all()
            
            # Convert to dictionaries
            return [self._admin_user_to_dict(user) for user in users]
            
        except Exception as e:
            logger.error(f"Error listing admin users: {str(e)}")
            raise
    
    # Metrics Methods
    
    async def save_metric(self, metric_name: str, metric_value: float, 
                          dimensions: Optional[Dict[str, Any]] = None,
                          expiry: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Save a metric value
        
        Args:
            metric_name: Metric name
            metric_value: Metric value
            dimensions: Optional dimensions
            expiry: Optional expiry timestamp
            
        Returns:
            Saved metric record
        """
        try:
            from . import models
            from sqlalchemy import select
            
            # Check if metric with same name and dimensions exists
            query = select(models.Metric).where(
                models.Metric.metric_name == metric_name
            )
            if dimensions:
                query = query.where(models.Metric.dimensions == dimensions)
                
            result = await self.session.execute(query)
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing metric
                existing.metric_value = metric_value
                existing.expiry = expiry
                existing.timestamp = datetime.utcnow()
                metric = existing
            else:
                # Create new metric
                metric = models.Metric(
                    metric_name=metric_name,
                    metric_value=metric_value,
                    dimensions=dimensions,
                    expiry=expiry
                )
                self.session.add(metric)
                
            # Commit changes
            await self.session.commit()
            await self.session.refresh(metric)
            
            return self._metric_to_dict(metric)
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error saving metric {metric_name}: {str(e)}")
            raise
    
    async def get_metrics(self, metric_name: Optional[str] = None, 
                          dimensions: Optional[Dict[str, Any]] = None,
                          limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get metrics with optional filtering
        
        Args:
            metric_name: Optional metric name filter
            dimensions: Optional dimensions filter
            limit: Maximum records to return
            
        Returns:
            List of metric records
        """
        try:
            from sqlalchemy import select
            from . import models
            
            # Build query based on filters
            query = select(models.Metric)
            if metric_name:
                query = query.where(models.Metric.metric_name == metric_name)
                
            # Add dimensions filter if provided
            if dimensions:
                query = query.where(models.Metric.dimensions == dimensions)
                
            # Add limit
            query = query.limit(limit)
            
            # Execute query
            result = await self.session.execute(query)
            metrics = result.scalars().all()
            
            # Convert to dictionaries
            return [self._metric_to_dict(metric) for metric in metrics]
            
        except Exception as e:
            logger.error(f"Error getting metrics: {str(e)}")
            raise
    
    # Audit Log Methods
    
    async def _audit_log(self, action: str, entity_type: str, entity_id: str,
                        actor_id: Optional[int] = None, actor_type: str = "system",
                        ip_address: Optional[str] = None, 
                        details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create an audit log entry
        
        Args:
            action: Action performed
            entity_type: Type of entity
            entity_id: Entity identifier
            actor_id: ID of actor performing the action
            actor_type: Type of actor (user, system, etc.)
            ip_address: Optional IP address
            details: Optional details
            
        Returns:
            Created audit log record
        """
        try:
            from . import models
            
            # Create audit log object
            audit_entry = models.AuditLog(
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                actor_id=actor_id,
                actor_type=actor_type,
                ip_address=ip_address,
                details=details
            )
            
            # Add to session and commit
            self.session.add(audit_entry)
            await self.session.commit()
            
            return self._audit_to_dict(audit_entry)
            
        except Exception as e:
            # Don't rollback the session here, as this is often called from other methods
            logger.error(f"Error creating audit log: {str(e)}")
            # Just log the error but don't raise, to avoid disrupting the main operation
            return {
                "error": str(e),
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id
            }
    
    # Helper methods to convert models to dictionaries
    
    def _account_to_dict(self, account) -> Dict[str, Any]:
        """Convert Account model to dictionary"""
        return {
            "id": account.id,
            "account_number": account.account_number,
            "balance": float(account.balance) if isinstance(account.balance, Decimal) else account.balance,
            "currency": account.currency,
            "owner_id": account.owner_id,
            "account_type": account.account_type,
            "status": account.status,
            "created_at": account.created_at.isoformat() if account.created_at else None,
            "updated_at": account.updated_at.isoformat() if account.updated_at else None,
            "metadata": account.metadata
        }
    
    def _transaction_to_dict(self, transaction) -> Dict[str, Any]:
        """Convert Transaction model to dictionary"""
        return {
            "id": transaction.id,
            "transaction_ref": transaction.transaction_ref,
            "source_account_id": transaction.source_account_id,
            "destination_account_id": transaction.destination_account_id,
            "amount": float(transaction.amount) if isinstance(transaction.amount, Decimal) else transaction.amount,
            "currency": transaction.currency,
            "transaction_type": transaction.transaction_type,
            "status": transaction.status,
            "description": transaction.description,
            "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
            "updated_at": transaction.updated_at.isoformat() if transaction.updated_at else None,
            "metadata": transaction.metadata
        }
    
    def _admin_user_to_dict(self, admin_user) -> Dict[str, Any]:
        """Convert AdminUser model to dictionary"""
        return {
            "id": admin_user.id,
            "name": admin_user.name,
            "email": admin_user.email,
            "role": admin_user.role,
            "is_active": admin_user.is_active,
            "last_login": admin_user.last_login.isoformat() if admin_user.last_login else None,
            "created_at": admin_user.created_at.isoformat() if admin_user.created_at else None,
            "updated_at": admin_user.updated_at.isoformat() if admin_user.updated_at else None,
            "permissions": admin_user.permissions
        }
    
    def _metric_to_dict(self, metric) -> Dict[str, Any]:
        """Convert Metric model to dictionary"""
        return {
            "id": metric.id,
            "metric_name": metric.metric_name,
            "metric_value": float(metric.metric_value) if isinstance(metric.metric_value, Decimal) else metric.metric_value,
            "dimensions": metric.dimensions,
            "timestamp": metric.timestamp.isoformat() if metric.timestamp else None,
            "expiry": metric.expiry.isoformat() if metric.expiry else None
        }
    
    def _audit_to_dict(self, audit) -> Dict[str, Any]:
        """Convert AuditLog model to dictionary"""
        return {
            "id": audit.id,
            "action": audit.action,
            "entity_type": audit.entity_type,
            "entity_id": audit.entity_id,
            "actor_id": audit.actor_id,
            "actor_type": audit.actor_type,
            "timestamp": audit.timestamp.isoformat() if audit.timestamp else None,
            "ip_address": audit.ip_address,
            "details": audit.details
        }
    
    # Transaction processing
    
    async def _process_transfer(self, source_id: int, destination_id: int, 
                               amount: Union[float, Decimal], transaction_id: int) -> None:
        """
        Process a transfer between accounts
        
        Args:
            source_id: Source account ID
            destination_id: Destination account ID
            amount: Transfer amount
            transaction_id: Transaction ID
        """
        from . import models
        
        # Get the accounts
        source_account = await self.session.get(models.Account, source_id)
        destination_account = await self.session.get(models.Account, destination_id)
        
        if not source_account:
            raise ValueError(f"Source account {source_id} not found")
            
        if not destination_account:
            raise ValueError(f"Destination account {destination_id} not found")
            
        # Check if source account has sufficient funds
        if source_account.balance < amount:
            raise ValueError(f"Insufficient funds in account {source_id}")
            
        # Update balances
        source_account.balance -= amount
        destination_account.balance += amount
        
        # No need to commit here, will be committed by the calling method
