from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.inventory import MovementType


class InventoryMovementCreate(BaseModel):
    product_id: int
    movement_type: MovementType
    quantity: int
    unit_cost: Optional[Decimal] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    notes: Optional[str] = None


class InventoryMovementResponse(BaseModel):
    id: int
    product_id: int
    movement_type: MovementType
    quantity: int
    quantity_before: int
    quantity_after: int
    unit_cost: Optional[Decimal]
    reference_type: Optional[str]
    reference_id: Optional[int]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
