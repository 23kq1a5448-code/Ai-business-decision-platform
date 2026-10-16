from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.expense import ExpenseCategory


class ExpenseCreate(BaseModel):
    amount: Decimal
    category: ExpenseCategory
    description: Optional[str] = None
    expense_date: datetime
    payment_method: Optional[str] = None
    vendor: Optional[str] = None
    receipt_number: Optional[str] = None
    notes: Optional[str] = None


class ExpenseUpdate(BaseModel):
    amount: Optional[Decimal] = None
    category: Optional[ExpenseCategory] = None
    description: Optional[str] = None
    expense_date: Optional[datetime] = None
    payment_method: Optional[str] = None
    vendor: Optional[str] = None
    receipt_number: Optional[str] = None
    notes: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: int
    business_id: int
    amount: Decimal
    category: ExpenseCategory
    description: Optional[str]
    expense_date: datetime
    payment_method: Optional[str]
    vendor: Optional[str]
    receipt_number: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
