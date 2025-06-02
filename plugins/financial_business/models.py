"""
SQLAlchemy models for the Financial Business App plugin.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, unique=True, index=True, nullable=False)
    balance = Column(Float, nullable=False, default=0.0)
    owner_id = Column(Integer, ForeignKey("admin_users.id")) # Assuming admin_users are owners for now

    owner = relationship("AdminUser", back_populates="accounts")
    outgoing_transactions = relationship("Transaction", foreign_keys="Transaction.from_account_id", back_populates="from_account")
    incoming_transactions = relationship("Transaction", foreign_keys="Transaction.to_account_id", back_populates="to_account")

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String) # Store hashed passwords, not plain text

    accounts = relationship("Account", back_populates="owner")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    from_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    to_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="completed")
    description = Column(String, nullable=True)
    
    from_account = relationship("Account", foreign_keys=[from_account_id], back_populates="outgoing_transactions")
    to_account = relationship("Account", foreign_keys=[to_account_id], back_populates="incoming_transactions")
