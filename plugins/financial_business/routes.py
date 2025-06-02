"""
API routes for Financial Business App plugin
"""
from fastapi import APIRouter, Body, Query, Depends, HTTPException
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import logging
import time
import asyncio

# Handle missing SQLAlchemy imports gracefully
try:
    from sqlalchemy import select, update
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import joinedload
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    logging.warning("SQLAlchemy not available, using mock implementations")
    select = lambda *args: None
    update = lambda *args: None
    class AsyncSession: pass
    joinedload = lambda *args: None
    SQLALCHEMY_AVAILABLE = False

from . import models, schemas

# Handle missing database connection
try:
    from database.connections.base import db
    DB_AVAILABLE = True
except ImportError:
    logging.warning("Database connection not available, using mock implementations")
    class MockDB:
        async def session(self):
            class MockSession:
                async def __aenter__(self): return self
                async def __aexit__(self, *args): pass
                async def commit(self): pass
                async def refresh(self, obj): pass
                async def get(self, model, id): 
                    if model == models.Account:
                        return models.Account(id=id, account_number=f"ACC{id}", balance=1000.0, owner_id=1)
                    elif model == models.AdminUser:
                        return models.AdminUser(id=id, name=f"User {id}", email=f"user{id}@example.com")
                    return None
                async def execute(self, query):
                    class Result:
                        def scalars(self):
                            class Scalars:
                                def all(self): return []
                            return Scalars()
                    return Result()
                def add(self, obj): pass
                async def flush(self): pass
                async def begin(self): return self
                
            return MockSession()
    
    db = MockDB()
    DB_AVAILABLE = False

router = APIRouter()

# Import and include metrics router
from .metrics import router as metrics_router
router.include_router(metrics_router, prefix="/metrics", tags=["monitoring"])

# Dependency to get DB session
async def get_db():
    async with db.session() as session:
        yield session

# All route handlers below must be async and use AsyncSession

@router.post("/accounts/", response_model=schemas.Account)
async def create_account(account: schemas.AccountCreate, db: AsyncSession = Depends(get_db)):
    db_account = models.Account(account_number=account.account_number, balance=account.balance, owner_id=account.owner_id)
    db.add(db_account)
    await db.commit()
    await db.refresh(db_account)
    return db_account

@router.get("/accounts/{account_id}", response_model=schemas.Account)
async def read_account(account_id: int, db: AsyncSession = Depends(get_db)):
    db_account = await db.get(models.Account, account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@router.get("/accounts/", response_model=List[schemas.Account])
async def read_accounts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    if SQLALCHEMY_AVAILABLE:
        result = await db.execute(
            select(models.Account).offset(skip).limit(limit)
        )
        accounts = result.scalars().all()
        return accounts
    # Fallback for when SQLAlchemy isn't available
    return [
        models.Account(id=1, account_number="ACC001", balance=5000.0, owner_id=1),
        models.Account(id=2, account_number="ACC002", balance=7500.0, owner_id=2)
    ]

@router.post("/admin_users/", response_model=schemas.AdminUser)
async def create_admin_user(user: schemas.AdminUserCreate, db: AsyncSession = Depends(get_db)):
    db_user = models.AdminUser(name=user.name, email=user.email, hashed_password=user.password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

@router.get("/admin_users/{user_id}", response_model=schemas.AdminUser)
async def read_admin_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await db.get(models.AdminUser, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Admin user not found")
    return db_user

@router.get("/admin_users/", response_model=List[schemas.AdminUser])
async def list_admin_users_db(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    if SQLALCHEMY_AVAILABLE:
        result = await db.execute(
            select(models.AdminUser).offset(skip).limit(limit)
        )
        users = result.scalars().all()
        return users
    # Fallback for when SQLAlchemy isn't available
    return [
        models.AdminUser(id=1, name="Alice Admin", email="alice@example.com"),
        models.AdminUser(id=2, name="Bob Admin", email="bob@example.com")
    ]

# Import monitoring tools from our local monitoring module
from .monitoring import (
    FINANCIAL_TRANSFER_COUNT, 
    FINANCIAL_TRANSFER_AMOUNT, 
    FINANCIAL_TRANSFER_ERRORS, 
    DB_QUERY_LATENCY,
    PROMETHEUS_AVAILABLE
)

# Set flag for whether monitoring is available
MONITORING_AVAILABLE = PROMETHEUS_AVAILABLE
if not MONITORING_AVAILABLE:
    logging.warning("Prometheus monitoring not available, using mock metrics")

# New transfer endpoint using transactions with enhanced monitoring and logging
@router.post("/transfers/", response_model=schemas.TransferResponse, summary="Transfer funds between accounts")
async def create_transfer(transfer: schemas.TransferCreate, db: AsyncSession = Depends(get_db)):
    """
    Transfer funds between accounts with transaction support
    
    Args:
        transfer: Transfer details including source and destination accounts and amount
        db: Database session
        
    Returns:
        Transfer status, transaction ID, and updated balances
        
    Raises:
        HTTPException: For validation errors (404 if accounts not found, 400 if insufficient funds)
    """
    logger = logging.getLogger("financial_business.transfers")
    
    # Log the transfer request
    logger.info(f"Transfer request from account {transfer.from_account_id} to {transfer.to_account_id} for amount {transfer.amount}")
    
    # Increment transfer count metric if monitoring is available
    if MONITORING_AVAILABLE:
        FINANCIAL_TRANSFER_COUNT.inc()
        FINANCIAL_TRANSFER_AMOUNT.observe(transfer.amount)
    
    # Start timing the transaction
    start_time = time.time()
    
    try:
        # Use a transaction to ensure atomicity
        if hasattr(db, 'begin'):
            async with db.begin():
                # Get both accounts
                query_start = time.time()
                from_acc = await db.get(models.Account, transfer.from_account_id)
                to_acc = await db.get(models.Account, transfer.to_account_id)
                query_time = time.time() - query_start
                
                # Record query latency if monitoring available
                if MONITORING_AVAILABLE:
                    DB_QUERY_LATENCY.observe(query_time)
                
                # Check if accounts exist
                if from_acc is None:
                    error_msg = f"Sender account {transfer.from_account_id} not found"
                    logger.warning(f"Transfer failed: {error_msg}")
                    if MONITORING_AVAILABLE:
                        FINANCIAL_TRANSFER_ERRORS.labels(error_type="account_not_found").inc()
                    raise HTTPException(status_code=404, detail=error_msg)
                    
                if to_acc is None:
                    error_msg = f"Receiver account {transfer.to_account_id} not found"
                    logger.warning(f"Transfer failed: {error_msg}")
                    if MONITORING_AVAILABLE:
                        FINANCIAL_TRANSFER_ERRORS.labels(error_type="account_not_found").inc()
                    raise HTTPException(status_code=404, detail=error_msg)
                
                # Check sufficient funds
                if from_acc.balance < transfer.amount:
                    error_msg = "Insufficient funds"
                    logger.warning(f"Transfer failed: {error_msg} - Account {transfer.from_account_id} has {from_acc.balance}, needed {transfer.amount}")
                    if MONITORING_AVAILABLE:
                        FINANCIAL_TRANSFER_ERRORS.labels(error_type="insufficient_funds").inc()
                    raise HTTPException(status_code=400, detail=error_msg)
                
                # Update balances
                from_acc.balance -= transfer.amount
                to_acc.balance += transfer.amount
                
                # Create transaction record
                transaction = models.Transaction(
                    from_account_id=transfer.from_account_id,
                    to_account_id=transfer.to_account_id,
                    amount=transfer.amount,
                    description=transfer.description,
                    timestamp=datetime.utcnow(),
                    status="completed"
                )
                db.add(transaction)
                
                # Commit everything in the transaction
                await db.flush()
                
                # Log successful transfer
                logger.info(f"Transfer completed: {transfer.amount} from account {transfer.from_account_id} to {transfer.to_account_id}, transaction ID: {transaction.id}")
                
                return {
                    "status": "success",
                    "transaction_id": transaction.id,
                    "from_balance": from_acc.balance,
                    "to_balance": to_acc.balance
                }
        else:
            # Mock implementation when database transaction isn't available
            logger.info("Using mock implementation for transfer (database transactions not available)")
            
            # Add a small delay to simulate processing
            await asyncio.sleep(0.1)
            
            return {
                "status": "success",
                "transaction_id": 12345,
                "from_balance": 900,
                "to_balance": 1100
            }
    except HTTPException:
        # Re-raise HTTP exceptions for proper API error response
        raise
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error during transfer: {str(e)}", exc_info=True)
        
        # Record error metric if monitoring is available
        if MONITORING_AVAILABLE:
            FINANCIAL_TRANSFER_ERRORS.labels(error_type="unexpected_error").inc()
            
        # Return a proper error response
        raise HTTPException(status_code=500, detail="An unexpected error occurred during transfer processing")
    finally:
        # Log the total transaction processing time
        processing_time = time.time() - start_time
        logger.debug(f"Transfer processing time: {processing_time:.4f}s")

@router.get("/transactions/", response_model=List[schemas.Transaction])
async def list_transactions(
    account_id: Optional[int] = None,
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    if SQLALCHEMY_AVAILABLE:
        query = select(models.Transaction).offset(skip).limit(limit)
        
        # Filter by account if provided
        if account_id:
            query = query.where(
                (models.Transaction.from_account_id == account_id) | 
                (models.Transaction.to_account_id == account_id)
            )
        
        result = await db.execute(query)
        transactions = result.scalars().all()
        return transactions
    # Fallback for when SQLAlchemy isn't available
    return [
        models.Transaction(
            id=1, 
            from_account_id=1, 
            to_account_id=2, 
            amount=500.0, 
            timestamp=datetime.utcnow(),
            status="completed"
        )
    ]

@router.get("/transactions/{transaction_id}", response_model=schemas.Transaction)
async def get_transaction(transaction_id: int, db: AsyncSession = Depends(get_db)):
    transaction = await db.get(models.Transaction, transaction_id)
    if transaction is None:
        # Fallback mock for testing
        if not SQLALCHEMY_AVAILABLE or not DB_AVAILABLE:
            return models.Transaction(
                id=transaction_id, 
                from_account_id=1, 
                to_account_id=2, 
                amount=500.0, 
                timestamp=datetime.utcnow(),
                status="completed"
            )
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

# Legacy endpoints (non-async, for backward compatibility)
@router.get("/account_summary")
def get_account_summary_original(user_id: str = Query(...)):
    # TODO: Integrate with real backend or mock
    return {"accountNumber": "1234567890", "balance": 1000000}

@router.post("/transfer")
def transfer_funds_original(data: dict = Body(...)):
    # TODO: Integrate with real backend or mock
    return {"success": True, "transactionId": "T123456"}

@router.get("/track_package")
def track_package(tracking_number: str = Query(...)):
    # TODO: Integrate with real backend or mock
    return {"status": "In Transit", "location": "Lagos Hub"}

@router.post("/book_delivery")
def book_delivery(data: dict = Body(...)):
    # TODO: Integrate with real backend or mock
    return {"success": True, "deliveryId": "D123456"}

@router.get("/charity_campaigns")
def get_charity_campaigns():
    # TODO: Integrate with real backend or mock
    return {"campaigns": []}

@router.post("/donate")
def make_donation(data: dict = Body(...)):
    # TODO: Integrate with real backend or mock
    return {"success": True, "donationId": "C123456"}

@router.post("/appointments")
def book_appointment(data: dict = Body(...)):
    # TODO: Integrate with real backend or mock
    return {"success": True, "appointmentId": "A123456"}

@router.get("/doctors")
def get_doctors():
    # TODO: Integrate with real backend or mock
    return {"doctors": []}

@router.post("/admissions")
def apply_admission(data: dict = Body(...)):
    # TODO: Integrate with real backend or mock
    return {"success": True, "studentId": "S123456"}

@router.get("/calendar")
def get_calendar():
    # TODO: Integrate with real backend or mock
    return {"events": []}

# Health check endpoint for the plugin
START_TIME = time.time()

@router.get("/health", summary="Health check")
async def health(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint for Financial Business plugin
    
    Returns:
        Dict containing health status and detailed checks of various components
    """
    from .plugin_manifest import FinancialBusinessPlugin
    
    # Use the plugin's comprehensive health check implementation
    plugin = FinancialBusinessPlugin()
    health_data = plugin.health_check()
    
    # Add database-specific checks using the available database connection
    try:
        if SQLALCHEMY_AVAILABLE and DB_AVAILABLE:
            # Test a simple database query
            start_time = time.time()
            result = await db.execute(select(models.Account).limit(1))
            # Update database latency if already in health status
            if "database" in health_data.get("checks", {}):
                health_data["checks"]["database"]["latency"] = round(time.time() - start_time, 4)
                health_data["checks"]["database"]["query_test"] = "passed"
    except Exception as e:
        logging.error(f"Database health check query failed: {str(e)}")
        if "database" in health_data.get("checks", {}):
            health_data["checks"]["database"]["status"] = "down"
            health_data["checks"]["database"]["error"] = str(e)
        health_data["status"] = "unhealthy"
    
    return health_data

@router.get("/health", summary="Health check for Financial Business plugin")
async def health_plugin(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint for Financial Business plugin
    
    Returns:
        Dict containing health status and detailed checks of various components
    """
    from .plugin_manifest import FinancialBusinessPlugin
    
    # Use the plugin's comprehensive health check implementation
    plugin = FinancialBusinessPlugin()
    health_data = plugin.health_check()
    
    # Add database-specific checks using the available database connection
    try:
        if SQLALCHEMY_AVAILABLE and DB_AVAILABLE:
            # Test a simple database query
            start_time = time.time()
            result = await db.execute(select(models.Account).limit(1))
            # Update database latency if already in health status
            if "database" in health_data.get("checks", {}):
                health_data["checks"]["database"]["latency"] = round(time.time() - start_time, 4)
                health_data["checks"]["database"]["query_test"] = "passed"
    except Exception as e:
        logging.error(f"Database health check query failed: {str(e)}")
        if "database" in health_data.get("checks", {}):
            health_data["checks"]["database"]["status"] = "down"
            health_data["checks"]["database"]["error"] = str(e)
        health_data["status"] = "unhealthy"
    
    return health_data
