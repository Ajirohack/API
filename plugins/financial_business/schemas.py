"""
Pydantic schemas for Financial Business App plugin.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

# --- Account Schemas ---
class AccountBase(BaseModel):
    account_number: str
    balance: float
    owner_id: int

class AccountCreate(AccountBase):
    pass

class Account(AccountBase):
    id: int
    
    # Updated to use modern Pydantic v2 syntax
    model_config = ConfigDict(from_attributes=True)

# --- AdminUser Schemas ---
class AdminUserBase(BaseModel):
    name: str
    email: str

class AdminUserCreate(AdminUserBase):
    password: str # Plain password, will be hashed in the route

class AdminUser(AdminUserBase):
    id: int
    
    # Updated to use modern Pydantic v2 syntax
    model_config = ConfigDict(from_attributes=True)
    
# For responses that include related accounts
class AdminUserWithAccounts(AdminUser):
    accounts: List[Account] = []

# --- Transaction Schemas ---
class TransactionBase(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float
    description: Optional[str] = None
    
class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    timestamp: datetime
    status: str
    
    model_config = ConfigDict(from_attributes=True)

# Transfer Request Schema (for more user-friendly API)
class TransferCreate(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float
    description: Optional[str] = None

# Transfer Response Schema
class TransferResponse(BaseModel):
    status: str
    transaction_id: int
    from_balance: float
    to_balance: float
