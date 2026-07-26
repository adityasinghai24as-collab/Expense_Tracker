from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import User
from app.schemas import UserResponse, UserUpdate
from app.auth import get_current_user, RoleChecker

router = APIRouter()

# Dependency for admin only
get_admin_user = RoleChecker(["admin"])

@router.get("", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    List all users.
    Requires admin privileges.
    """
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user's profile"""
    if update_data.username is not None:
        # Check if username is taken
        if update_data.username != current_user.username:
            result = await db.execute(select(User).where(User.username == update_data.username))
            if result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = update_data.username
        
    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name
        
        
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete current user's account and all associated data"""
    await db.delete(current_user)
    await db.commit()
    return None


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific user by ID.
    Users can only fetch their own profile, unless they are an admin.
    """
    # Check if requesting user is the same as target user or is admin
    is_admin = current_user.role == "admin"
    if current_user.id != user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's information"
        )
        
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    return user


@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    role: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Update a user's role (RBAC).
    Requires admin privileges.
    """
    valid_roles = ["user", "pro", "admin"]
    if role not in valid_roles:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role specified")
        
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.role = role
    await db.commit()
    await db.refresh(user)
    
    return user
