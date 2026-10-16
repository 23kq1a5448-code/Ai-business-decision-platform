from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.expense import Expense, ExpenseCategory
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.core.deps import get_current_user, get_current_business
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=ExpenseResponse)
def create_expense(
    expense_data: ExpenseCreate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Create a new expense."""
    new_expense = Expense(
        business_id=current_business.id,
        **expense_data.model_dump()
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return ExpenseResponse.model_validate(new_expense)


@router.get("/", response_model=List[ExpenseResponse])
def get_expenses(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[ExpenseCategory] = None,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get expenses with filtering options."""
    query = db.query(Expense).filter(Expense.business_id == current_business.id)

    if start_date:
        query = query.filter(Expense.expense_date >= start_date)
    if end_date:
        query = query.filter(Expense.expense_date <= end_date)
    if category:
        query = query.filter(Expense.category == category)

    expenses = query.order_by(Expense.expense_date.desc()).offset(skip).limit(limit).all()
    return [ExpenseResponse.model_validate(expense) for expense in expenses]


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get a specific expense by ID."""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.business_id == current_business.id
    ).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    return ExpenseResponse.model_validate(expense)


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Update an expense."""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.business_id == current_business.id
    ).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    update_data = expense_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)
    return ExpenseResponse.model_validate(expense)


@router.delete("/{expense_id}")
def delete_expense(
    expense_id: int,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Delete an expense."""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.business_id == current_business.id
    ).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )

    db.delete(expense)
    db.commit()

    return {"message": "Expense deleted successfully"}
