from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, Boolean, Float, Text, Enum
from sqlalchemy.types import Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    first_name = Column(String(100))
    username = Column(String(100), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False)
    email = Column(String(100), nullable=True)
    balance = Column(Float, default=0)
    language = Column(Integer, default=None)

    purchases = relationship("Purchase", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    item_id = Column(Integer, ForeignKey('items.id'))
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Integer, default=1)

    user = relationship("User", back_populates="purchases")
    items = relationship("Item", back_populates="purchases")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_type = Column(Integer)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    item_id = Column(Integer, ForeignKey('items.id'), nullable=True)
    amount = Column(Float)
    address = Column(String(100), nullable=True)
    transaction_hash = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Integer, default=1)

    """
    Transaction types:
        0 - Deposit
        1 - Withdraw
        2 - buy item
    
    Statuses:
        1 - Created
        2 - Confirm
        3 - Cancel
    """

    user = relationship("User", back_populates="transactions")
    items = relationship("Item", back_populates="transactions")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(Text)
    price = Column(Float)
    image_url = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="items")
    purchases = relationship("Purchase", back_populates="items")


class BalanceAddRequest(BaseModel):
    user_id: int
    amount: float
