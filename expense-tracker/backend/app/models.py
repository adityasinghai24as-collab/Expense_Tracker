"""
SQLAlchemy ORM models for Expense Tracker
Add your database models here
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    """User model (placeholder)"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    otp_code = Column(String, nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)
    role = Column(String, nullable=False, default="free") # e.g. "free", "pro", "enterprise", "admin"
    
    @property
    def features_enabled(self):
        """RBAC (Role-Based Access Control) Feature Mapping.
        Even if a feature is globally enabled, the user must have the required role to use it.
        """
        is_pro = self.role in ["pro", "enterprise", "admin"]
        is_enterprise = self.role in ["enterprise", "admin"]
        
        return {
            # Pro Tier Features
            "enable_receipt_scanning": is_pro,
            "enable_data_export": is_pro,
            "enable_budgets": is_pro,
            
            # Enterprise Tier Features (Agentic AI)
            "enable_autonomous_agent": is_enterprise,
            "enable_local_rag": is_enterprise,
            
            # Admin Features
            "is_admin": self.role == "admin"
        }

    hashed_password = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")


class Category(Base):
    """Category model for standard and custom expense categories"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    color = Column(String, nullable=True)
    icon = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Null indicates a global category
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="categories")
    expenses = relationship("Expense", back_populates="category")


class Expense(Base):
    """Expense model representing a transaction"""
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="expenses")
    category = relationship("Category", back_populates="expenses")
