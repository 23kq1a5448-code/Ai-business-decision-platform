from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.alert import Alert, AlertType, AlertSeverity, AlertStatus
from app.schemas.alert import AlertCreate, AlertUpdate, AlertResponse
from app.core.deps import get_current_user, get_current_business
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=AlertResponse)
def create_alert(
    alert_data: AlertCreate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Create a new alert."""
    new_alert = Alert(
        business_id=current_business.id,
        **alert_data.model_dump()
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    return AlertResponse.model_validate(new_alert)


@router.get("/", response_model=List[AlertResponse])
def get_alerts(
    skip: int = 0,
    limit: int = 100,
    alert_type: Optional[AlertType] = None,
    severity: Optional[AlertSeverity] = None,
    status: Optional[AlertStatus] = None,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get alerts with filtering."""
    query = db.query(Alert).filter(Alert.business_id == current_business.id)

    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    if severity:
        query = query.filter(Alert.severity == severity)
    if status:
        query = query.filter(Alert.status == status)

    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    return [AlertResponse.model_validate(alert) for alert in alerts]


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: int,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get a specific alert by ID."""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.business_id == current_business.id
    ).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    return AlertResponse.model_validate(alert)


@router.put("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Update an alert (typically status)."""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.business_id == current_business.id
    ).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    update_data = alert_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(alert, field, value)

    # Set timestamps based on status
    from datetime import datetime
    if update_data.get("status") == AlertStatus.ACKNOWLEDGED:
        alert.acknowledged_at = datetime.utcnow()
    elif update_data.get("status") == AlertStatus.RESOLVED:
        alert.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(alert)
    return AlertResponse.model_validate(alert)


@router.delete("/{alert_id}")
def delete_alert(
    alert_id: int,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Delete an alert."""
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.business_id == current_business.id
    ).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )

    db.delete(alert)
    db.commit()

    return {"message": "Alert deleted successfully"}


@router.post("/check-conditions")
def check_alert_conditions(
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Check business conditions and generate alerts automatically."""
    from app.models.product import Product
    from app.models.customer import Customer
    from datetime import datetime

    alerts_created = []

    # Check for low stock
    low_stock_products = db.query(Product).filter(
        Product.business_id == current_business.id,
        Product.stock_quantity <= Product.low_stock_threshold
    ).all()

    for product in low_stock_products:
        existing_alert = db.query(Alert).filter(
            Alert.business_id == current_business.id,
            Alert.alert_type == AlertType.LOW_STOCK,
            Alert.entity_id == product.id,
            Alert.status == AlertStatus.ACTIVE
        ).first()

        if not existing_alert:
            new_alert = Alert(
                business_id=current_business.id,
                alert_type=AlertType.LOW_STOCK,
                severity=AlertSeverity.WARNING,
                title=f"Low Stock: {product.name}",
                description=f"Product {product.name} has only {product.stock_quantity} units remaining (threshold: {product.low_stock_threshold})",
                entity_type="product",
                entity_id=product.id,
                metric_value=str(product.stock_quantity),
                threshold_value=str(product.low_stock_threshold)
            )
            db.add(new_alert)
            alerts_created.append(f"Low stock alert for {product.name}")

    # Check for high churn risk customers
    high_churn_customers = db.query(Customer).filter(
        Customer.business_id == current_business.id,
        Customer.churn_risk == "high"
    ).all()

    for customer in high_churn_customers:
        existing_alert = db.query(Alert).filter(
            Alert.business_id == current_business.id,
            Alert.alert_type == AlertType.HIGH_CHURN_RISK,
            Alert.entity_id == customer.id,
            Alert.status == AlertStatus.ACTIVE
        ).first()

        if not existing_alert:
            new_alert = Alert(
                business_id=current_business.id,
                alert_type=AlertType.HIGH_CHURN_RISK,
                severity=AlertSeverity.WARNING,
                title=f"High Churn Risk: {customer.name}",
                description=f"Customer {customer.name} is at high risk of churning",
                entity_type="customer",
                entity_id=customer.id
            )
            db.add(new_alert)
            alerts_created.append(f"High churn risk alert for {customer.name}")

    db.commit()

    return {
        "message": f"Checked alert conditions",
        "alerts_created": alerts_created,
        "total_created": len(alerts_created)
    }
