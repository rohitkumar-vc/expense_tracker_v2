from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


class AccountType(str, enum.Enum):
    BANK = "bank"
    CREDIT_CARD = "credit_card"
    CASH = "cash"


class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class CategoryType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)  # username
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    
    name = Column(String(100))
    email = Column(String(100))
    is_active = Column(Boolean, default=True)
    must_change_password = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")


class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(AccountType), nullable=False)
    name = Column(String(100), nullable=False)
    
    # For bank accounts
    bank_name = Column(String(100))
    account_number = Column(String(50))  # Last 4 digits
    initial_balance = Column(Float, default=0.0)
    current_balance = Column(Float, default=0.0)
    
    # For credit cards
    total_limit = Column(Float, default=0.0)
    used_amount = Column(Float, default=0.0)
    billing_date = Column(Integer)  # Day of month (1-31)
    due_date = Column(Integer)  # Day of month (1-31)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions_as_source = relationship("Transaction", foreign_keys="Transaction.source_account_id", back_populates="source_account")
    transactions_as_dest = relationship("Transaction", foreign_keys="Transaction.dest_account_id", back_populates="dest_account")


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(Enum(CategoryType), nullable=False)
    is_system = Column(Boolean, default=False)  # System categories can't be deleted
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String(200))
    notes = Column(Text)
    
    category_id = Column(Integer, ForeignKey("categories.id"))
    source_account_id = Column(Integer, ForeignKey("accounts.id"))  # Where money comes from
    dest_account_id = Column(Integer, ForeignKey("accounts.id"))    # Where money goes (for transfers)
    
    receipt_path = Column(String(500))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    source_account = relationship("Account", foreign_keys=[source_account_id], back_populates="transactions_as_source")
    dest_account = relationship("Account", foreign_keys=[dest_account_id], back_populates="transactions_as_dest")


class Budget(Base):
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    amount = Column(Float, nullable=False)
    month = Column(Integer, nullable=False)  # 1-12
    year = Column(Integer, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")
