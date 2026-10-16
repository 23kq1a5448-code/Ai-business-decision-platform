from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.models.sale import SaleStatus


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal
    unit_cost: Decimal


class SaleCreate(BaseModel):
    invoice_number: str
    sale_date: datetime
    customer_id: Optional[int] = None
    payment_method: Optional[str] = None
    region: Optional[str] = None
    notes: Optional[str] = None
    items: List[SaleItemCreate]


class SaleUpdate(BaseModel):
    customer_id: Optional[int] = None
    status: Optional[SaleStatus] = None
    payment_method: Optional[str] = None
    region: Optional[str] = None
    notes: Optional[str] = None


class SaleResponse(BaseModel):
    id: int
    business_id: int
    invoice_number: str
    sale_date: datetime
    customer_id: Optional[int]
    total_amount: Decimal
    total_cost: Decimal
    total_profit: Decimal
    status: SaleStatus
    payment_method: Optional[str]
    region: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
