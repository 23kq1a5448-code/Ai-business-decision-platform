from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from decimal import Decimal


class CustomerCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class CustomerResponse(BaseModel):
    id: int
    business_id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    segment: Optional[str]
    churn_risk: Optional[str]
    churn_probability: Optional[Decimal]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
