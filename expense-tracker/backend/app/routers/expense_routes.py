from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Expense, User
from app.schemas import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.auth import get_current_user

router = APIRouter()


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new expense for the authenticated user.
    """
    new_expense = Expense(
        **expense.model_dump(),
        user_id=current_user.id
    )
    db.add(new_expense)
    await db.commit()
    
    # Reload with relationship to return fully populated response
    stmt = select(Expense).where(Expense.id == new_expense.id).options(selectinload(Expense.category))
    result = await db.execute(stmt)
    return result.scalar_one()


@router.get("", response_model=List[ExpenseResponse])
async def list_expenses(
    skip: int = Query(0, ge=0, description="Skip N records (for pagination)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of records to return"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all expenses for the authenticated user.
    Includes optional pagination and category filtering.
    """
    stmt = select(Expense).where(Expense.user_id == current_user.id).options(selectinload(Expense.category))
    
    if category_id is not None:
        stmt = stmt.where(Expense.category_id == category_id)
        
    stmt = stmt.offset(skip).limit(limit).order_by(Expense.created_at.desc())
    
    result = await db.execute(stmt)
    expenses = result.scalars().all()
    return expenses


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific expense by ID.
    The expense must belong to the authenticated user.
    """
    stmt = select(Expense).where(Expense.id == expense_id, Expense.user_id == current_user.id).options(selectinload(Expense.category))
    result = await db.execute(stmt)
    expense = result.scalar_one_or_none()
    
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a specific expense.
    Only provided fields will be updated. The expense must belong to the authenticated user.
    """
    stmt = select(Expense).where(Expense.id == expense_id, Expense.user_id == current_user.id).options(selectinload(Expense.category))
    result = await db.execute(stmt)
    expense = result.scalar_one_or_none()
    
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        
    update_data = expense_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(expense, key, value)
        
    await db.commit()
    await db.refresh(expense)
    
    # Refresh again with the relationship loaded to return properly
    stmt = select(Expense).where(Expense.id == expense.id).options(selectinload(Expense.category))
    result = await db.execute(stmt)
    return result.scalar_one()


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific expense.
    The expense must belong to the authenticated user.
    """
    stmt = select(Expense).where(Expense.id == expense_id, Expense.user_id == current_user.id)
    result = await db.execute(stmt)
    expense = result.scalar_one_or_none()
    
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        
    await db.delete(expense)
    await db.commit()
    return None
