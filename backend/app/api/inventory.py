from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.inventory import InventoryMovement, MovementType
from app.models.product import Product
from app.schemas.inventory import InventoryMovementCreate, InventoryMovementResponse
from app.core.deps import get_current_user, get_current_business
from app.models.user import User

router = APIRouter()


@router.post("/movements/", response_model=InventoryMovementResponse)
def create_inventory_movement(
    movement_data: InventoryMovementCreate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Create an inventory movement (purchase, adjustment, etc.)."""
    product = db.query(Product).filter(
        Product.id == movement_data.product_id,
        Product.business_id == current_business.id
    ).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    quantity_before = product.stock_quantity

    # Calculate new stock based on movement type
    if movement_data.movement_type == MovementType.PURCHASE:
        product.stock_quantity += movement_data.quantity
    elif movement_data.movement_type == MovementType.SALE:
        if product.stock_quantity < movement_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock for sale"
            )
        product.stock_quantity -= movement_data.quantity
    elif movement_data.movement_type == MovementType.RETURN:
        product.stock_quantity += movement_data.quantity
    elif movement_data.movement_type == MovementType.ADJUSTMENT:
        product.stock_quantity = movement_data.quantity
    elif movement_data.movement_type == MovementType.TRANSFER:
        if product.stock_quantity < movement_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock for transfer"
            )
        product.stock_quantity -= movement_data.quantity

    quantity_after = product.stock_quantity

    new_movement = InventoryMovement(
        product_id=movement_data.product_id,
        movement_type=movement_data.movement_type,
        quantity=movement_data.quantity,
        quantity_before=quantity_before,
        quantity_after=quantity_after,
        unit_cost=movement_data.unit_cost,
        reference_type=movement_data.reference_type,
        reference_id=movement_data.reference_id,
        notes=movement_data.notes
    )
    db.add(new_movement)
    db.commit()
    db.refresh(new_movement)
    return InventoryMovementResponse.model_validate(new_movement)


@router.get("/movements/", response_model=List[InventoryMovementResponse])
def get_inventory_movements(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = None,
    movement_type: Optional[MovementType] = None,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get inventory movements with filtering."""
    query = db.query(InventoryMovement).join(Product).filter(
        Product.business_id == current_business.id
    )

    if product_id:
        query = query.filter(InventoryMovement.product_id == product_id)
    if movement_type:
        query = query.filter(InventoryMovement.movement_type == movement_type)

    movements = query.order_by(InventoryMovement.created_at.desc()).offset(skip).limit(limit).all()
    return [InventoryMovementResponse.model_validate(movement) for movement in movements]


@router.get("/low-stock/")
def get_low_stock_products(
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get products with low stock."""
    products = db.query(Product).filter(
        Product.business_id == current_business.id,
        Product.stock_quantity <= Product.low_stock_threshold
    ).all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "stock_quantity": p.stock_quantity,
            "low_stock_threshold": p.low_stock_threshold,
            "predicted_demand": p.predicted_demand,
            "suggested_reorder": p.suggested_reorder
        } for p in products
    ]
