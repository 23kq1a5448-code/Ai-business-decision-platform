from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SupplierCreate(BaseModel):
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class SupplierResponse(BaseModel):
    id: int
    name: str
    contact_person: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    sku: Optional[str] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    description: Optional[str] = None
    selling_price: Decimal
    cost_price: Decimal
    stock_quantity: int = 0
    low_stock_threshold: int = 10


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    description: Optional[str] = None
    selling_price: Optional[Decimal] = None
    cost_price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    low_stock_threshold: Optional[int] = None


class ProductResponse(BaseModel):
    id: int
    business_id: int
    name: str
    sku: Optional[str]
    category_id: Optional[int]
    supplier_id: Optional[int]
    description: Optional[str]
    selling_price: Decimal
    cost_price: Decimal
    stock_quantity: int
    low_stock_threshold: int
    predicted_demand: Optional[int]
    suggested_reorder: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
