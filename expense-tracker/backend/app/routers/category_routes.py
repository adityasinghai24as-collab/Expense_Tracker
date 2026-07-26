from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_

from app.database import get_db
from app.models import Category, User, Expense
from app.schemas import CategoryCreate, CategoryResponse, CategoryUpdate
from app.auth import get_current_user

router = APIRouter()


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new custom category for the authenticated user.
    """
    new_category = Category(
        **category.model_dump(),
        user_id=current_user.id
    )
    db.add(new_category)
    await db.commit()
    await db.refresh(new_category)
    return new_category


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List categories available to the user.
    This includes global categories (user_id is None) and their custom categories.
    """
    stmt = select(Category).where(
        or_(Category.user_id == None, Category.user_id == current_user.id)
    ).order_by(Category.name.asc())
    
    result = await db.execute(stmt)
    categories = result.scalars().all()
    return categories


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a custom category.
    Users can only update their own categories.
    """
    stmt = select(Category).where(Category.id == category_id)
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        
    if category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Cannot edit a global category or someone else's category"
        )
        
    update_data = category_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
        
    await db.commit()
    await db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a custom category.
    Fails if the category is currently used by any expenses.
    """
    stmt = select(Category).where(Category.id == category_id)
    result = await db.execute(stmt)
    category = result.scalar_one_or_none()
    
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        
    if category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Cannot delete a global category or someone else's category"
        )
    
    # Check if category is used
    expense_stmt = select(Expense).where(Expense.category_id == category_id).limit(1)
    expense_result = await db.execute(expense_stmt)
    if expense_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cannot delete category because it is currently linked to one or more expenses"
        )

    await db.delete(category)
    await db.commit()
    return None
