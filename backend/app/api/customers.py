from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from app.db.database import get_db
from app.models.customer import Customer
from app.models.sale import Sale, SaleItem
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.core.deps import get_current_user, get_current_business
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=CustomerResponse)
def create_customer(
    customer_data: CustomerCreate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Create a new customer."""
    new_customer = Customer(
        business_id=current_business.id,
        **customer_data.model_dump()
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return CustomerResponse.model_validate(new_customer)


@router.get("/", response_model=List[CustomerResponse])
def get_customers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    segment: Optional[str] = None,
    churn_risk: Optional[str] = None,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get customers with filtering options."""
    query = db.query(Customer).filter(Customer.business_id == current_business.id)

    if search:
        query = query.filter(
            or_(
                Customer.name.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%"),
                Customer.phone.ilike(f"%{search}%")
            )
        )
    if segment:
        query = query.filter(Customer.segment == segment)
    if churn_risk:
        query = query.filter(Customer.churn_risk == churn_risk)

    customers = query.order_by(Customer.created_at.desc()).offset(skip).limit(limit).all()
    return [CustomerResponse.model_validate(customer) for customer in customers]


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get a specific customer by ID."""
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.business_id == current_business.id
    ).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return CustomerResponse.model_validate(customer)


@router.get("/{customer_id}/purchase-history")
def get_customer_purchase_history(
    customer_id: int,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get purchase history for a customer."""
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.business_id == current_business.id
    ).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    # Get sales for this customer
    sales = db.query(Sale).filter(
        Sale.customer_id == customer_id,
        Sale.business_id == current_business.id,
        Sale.status == "completed"
    ).order_by(Sale.sale_date.desc()).all()

    # Calculate RFM metrics
    total_spending = db.query(func.sum(Sale.total_amount)).filter(
        Sale.customer_id == customer_id,
        Sale.business_id == current_business.id,
        Sale.status == "completed"
    ).scalar() or 0

    total_orders = db.query(func.count(Sale.id)).filter(
        Sale.customer_id == customer_id,
        Sale.business_id == current_business.id,
        Sale.status == "completed"
    ).scalar() or 0

    last_sale = db.query(Sale).filter(
        Sale.customer_id == customer_id,
        Sale.business_id == current_business.id,
        Sale.status == "completed"
    ).order_by(Sale.sale_date.desc()).first()

    last_purchase_date = last_sale.sale_date if last_sale else None

    return {
        "customer_id": customer_id,
        "customer_name": customer.name,
        "total_spending": float(total_spending),
        "total_orders": total_orders,
        "last_purchase_date": str(last_purchase_date) if last_purchase_date else None,
        "segment": customer.segment,
        "churn_risk": customer.churn_risk,
        "churn_probability": float(customer.churn_probability) if customer.churn_probability else None,
        "recent_sales": [
            {
                "id": s.id,
                "invoice_number": s.invoice_number,
                "sale_date": str(s.sale_date),
                "total_amount": float(s.total_amount)
            } for s in sales[:10]
        ]
    }


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Update a customer."""
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.business_id == current_business.id
    ).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    update_data = customer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return CustomerResponse.model_validate(customer)


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Delete a customer."""
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.business_id == current_business.id
    ).first()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    db.delete(customer)
    db.commit()

    return {"message": "Customer deleted successfully"}
