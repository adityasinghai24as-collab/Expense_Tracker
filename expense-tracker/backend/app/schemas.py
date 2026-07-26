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
    # 2. Inherit from UserBase, add any fields needed specifically for creation
    password: str


class UserResponse(UserBase):
    """Schema for user responses"""
    id: int
    is_active: bool
    is_verified: bool
    role: str
    features_enabled: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating a user profile"""
    username: Optional[str] = None
    full_name: Optional[str] = None


class CategoryBase(BaseModel):
    """Base category schema"""
    name: str
    color: Optional[str] = None
    icon: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a category"""
    pass


class CategoryResponse(CategoryBase):
    """Schema for category responses"""
    id: int
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryUpdate(BaseModel):
    """Schema for updating a category"""
    name: Optional[str] = None
    color: Optional[str] = None


class ExpenseBase(BaseModel):
    """Base expense schema"""
    amount: float
    description: Optional[str] = None
    category_id: Optional[int] = None


class ExpenseCreate(ExpenseBase):
    """Schema for creating an expense"""
    pass


class ExpenseResponse(ExpenseBase):
    """Schema for expense responses"""
    id: int
    user_id: int
    category: Optional[CategoryResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExpenseUpdate(BaseModel):
    """Schema for updating an expense"""
    amount: Optional[float] = None
    description: Optional[str] = None
    category_id: Optional[int] = None


# 1. Add UserLogin schema (email, password)
# 2. Add TokenResponse schema (access_token, refresh_token, token_type)
# 3. Add TokenRefreshRequest schema (refresh_token)
# 4. Update UserCreate (above) to include a 'password' field (plain text string)

class UserLogin(BaseModel):
    """Schema for user login"""
    username_or_email: str
    password: str

class TokenResponse(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefreshRequest(BaseModel):
    """Schema for requesting a new access token via refresh token"""
    refresh_token: str

class OTPVerifyRequest(BaseModel):
    """Schema for OTP verification"""
    email: EmailStr
    otp_code: str

class OTPResendRequest(BaseModel):
    """Schema for requesting a new OTP"""
    email: EmailStr
