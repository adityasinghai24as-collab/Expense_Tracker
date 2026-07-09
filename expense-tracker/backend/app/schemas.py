"""
Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Base user schema"""
    # TODO: SDE-2 Task 17 - CRUD Request/Response Schemas

    # 1. Add email (EmailStr), username (str), and full_name (Optional[str])
    pass


class UserCreate(UserBase):
    """Schema for creating a user"""
    # 2. Inherit from UserBase, add any fields needed specifically for creation
    password: str


class UserResponse(UserBase):
    """Schema for user responses"""
    # 3. Add id (int), is_active (bool), created_at (datetime), updated_at (datetime)
    # Add inner Config class with from_attributes = True to support ORM models
    pass


class ExpenseBase(BaseModel):
    """Base expense schema"""
    # 4. Add amount (float), description (Optional[str]), category (Optional[str])
    pass


class ExpenseCreate(ExpenseBase):
    """Schema for creating an expense"""
    # 5. Inherit from ExpenseBase, add any specific fields for creationeeded currently
    pass


class ExpenseResponse(ExpenseBase):
    """Schema for expense responses"""
    # 6. Add id (int), user_id (int), created_at (datetime), updated_at (datetime)
    # Add inner Config class with from_attributes = True
    pass


class ExpenseUpdate(BaseModel):
    """Schema for updating an expense"""
    # 7. Add fields that can be updated (amount, description, category)
    # Ensure they are Optional so the user doesn't have to provide all of them
    pass

# TODO: SDE-2 Task 11 - Auth Request/Response Schemas
# 1. Add UserLogin schema (email, password)
# 2. Add TokenResponse schema (access_token, refresh_token, token_type)
# 3. Add TokenRefreshRequest schema (refresh_token)
# 4. Update UserCreate (above) to include a 'password' field (plain text string)

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefreshRequest(BaseModel):
    """Schema for requesting a new access token via refresh token"""
    refresh_token: str
