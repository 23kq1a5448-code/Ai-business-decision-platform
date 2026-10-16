from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.sale import Sale, SaleItem, SaleStatus
from app.models.product import Product
from app.models.customer import Customer
from app.schemas.sale import SaleCreate, SaleUpdate, SaleResponse, SaleItemCreate
from app.core.deps import get_current_user, get_current_business
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=SaleResponse)
def create_sale(
    sale_data: SaleCreate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Create a new sale with items."""
    # Validate invoice number uniqueness
    existing = db.query(Sale).filter(
        Sale.invoice_number == sale_data.invoice_number
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice number already exists"
        )

    # Validate customer if provided
    if sale_data.customer_id:
        customer = db.query(Customer).filter(
            Customer.id == sale_data.customer_id,
            Customer.business_id == current_business.id
        ).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )

    # Calculate totals and validate products
    total_amount = 0
    total_cost = 0
    validated_items = []

    for item in sale_data.items:
        product = db.query(Product).filter(
            Product.id == item.product_id,
            Product.business_id == current_business.id
        ).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} not found"
            )

        # Check stock
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product {product.name}. Available: {product.stock_quantity}, Requested: {item.quantity}"
            )

        item_total_price = item.quantity * item.unit_price
        item_total_cost = item.quantity * item.unit_cost
        total_amount += item_total_price
        total_cost += item_total_cost

        validated_items.append({
            "product": product,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "unit_cost": item.unit_cost,
            "total_price": item_total_price,
            "total_cost": item_total_cost
        })

    total_profit = total_amount - total_cost

    # Create sale
    new_sale = Sale(
        business_id=current_business.id,
        invoice_number=sale_data.invoice_number,
        sale_date=sale_data.sale_date,
        customer_id=sale_data.customer_id,
        total_amount=total_amount,
        total_cost=total_cost,
        total_profit=total_profit,
        status=sale_data.status if sale_data.status else SaleStatus.COMPLETED,
        payment_method=sale_data.payment_method,
        region=sale_data.region,
        notes=sale_data.notes
    )
    db.add(new_sale)
    db.flush()

    # Create sale items and update inventory
    for item_data in validated_items:
        product = item_data["product"]

        # Create sale item
        sale_item = SaleItem(
            sale_id=new_sale.id,
            product_id=product.id,
            customer_id=sale_data.customer_id,
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            unit_cost=item_data["unit_cost"],
            total_price=item_data["total_price"],
            total_cost=item_data["total_cost"],
            total_profit=item_data["total_price"] - item_data["total_cost"]
        )
        db.add(sale_item)

        # Update product stock
        product.stock_quantity -= item_data["quantity"]

        # Create inventory movement
        from app.models.inventory import InventoryMovement, MovementType
        movement = InventoryMovement(
            product_id=product.id,
            movement_type=MovementType.SALE,
            quantity=item_data["quantity"],
            quantity_before=product.stock_quantity + item_data["quantity"],
            quantity_after=product.stock_quantity,
            unit_cost=item_data["unit_cost"],
            reference_type="sale",
            reference_id=new_sale.id
        )
        db.add(movement)

    db.commit()
    db.refresh(new_sale)

    return SaleResponse.model_validate(new_sale)


@router.get("/", response_model=List[SaleResponse])
def get_sales(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    customer_id: Optional[int] = None,
    product_id: Optional[int] = None,
    region: Optional[str] = None,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get sales with filtering options."""
    query = db.query(Sale).filter(Sale.business_id == current_business.id)

    if start_date:
        query = query.filter(Sale.sale_date >= start_date)
    if end_date:
        query = query.filter(Sale.sale_date <= end_date)
    if customer_id:
        query = query.filter(Sale.customer_id == customer_id)
    if region:
        query = query.filter(Sale.region == region)
    if product_id:
        query = query.join(SaleItem).filter(SaleItem.product_id == product_id)

    sales = query.order_by(Sale.sale_date.desc()).offset(skip).limit(limit).all()
    return [SaleResponse.model_validate(sale) for sale in sales]


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(
    sale_id: int,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get a specific sale by ID."""
    sale = db.query(Sale).filter(
        Sale.id == sale_id,
        Sale.business_id == current_business.id
    ).first()
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found"
        )
    return SaleResponse.model_validate(sale)


@router.put("/{sale_id}", response_model=SaleResponse)
def update_sale(
    sale_id: int,
    sale_data: SaleUpdate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Update a sale (limited fields)."""
    sale = db.query(Sale).filter(
        Sale.id == sale_id,
        Sale.business_id == current_business.id
    ).first()
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found"
        )

    # Update allowed fields
    update_data = sale_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sale, field, value)

    db.commit()
    db.refresh(sale)
    return SaleResponse.model_validate(sale)


@router.delete("/{sale_id}")
def delete_sale(
    sale_id: int,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Delete a sale (and restore inventory)."""
    sale = db.query(Sale).filter(
        Sale.id == sale_id,
        Sale.business_id == current_business.id
    ).first()
    if not sale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sale not found"
        )

    # Restore inventory for each item
    for item in sale.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock_quantity += item.quantity

            # Create inventory movement for return
            from app.models.inventory import InventoryMovement, MovementType
            movement = InventoryMovement(
                product_id=product.id,
                movement_type=MovementType.RETURN,
                quantity=item.quantity,
                quantity_before=product.stock_quantity - item.quantity,
                quantity_after=product.stock_quantity,
                unit_cost=item.unit_cost,
                reference_type="sale_return",
                reference_id=sale.id
            )
            db.add(movement)

    db.delete(sale)
    db.commit()

    return {"message": "Sale deleted successfully"}
