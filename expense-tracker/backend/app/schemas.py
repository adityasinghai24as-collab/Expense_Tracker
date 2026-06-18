"""
Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user"""
    pass


class UserResponse(UserBase):
    """Schema for user responses"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExpenseBase(BaseModel):
    """Base expense schema"""
    amount: float
    description: Optional[str] = None
    category: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    """Schema for creating an expense"""
    pass


class ExpenseResponse(ExpenseBase):
    """Schema for expense responses"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExpenseUpdate(BaseModel):
    """Schema for updating an expense"""
    amount: Optional[float] = None
    description: Optional[str] = None
    category: Optional[str] = None
