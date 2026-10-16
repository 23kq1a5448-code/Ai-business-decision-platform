from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.ml import ModelRun, ModelType
from app.models.sale import Sale
from app.schemas.ml import ModelRunCreate, ModelRunResponse, PredictionResponse
from app.core.deps import get_current_user, get_current_business
from app.models.user import User
from app.ml.sales_prediction import SalesPredictor
from app.ml.churn_prediction import ChurnPredictor
from app.ml.demand_forecasting import DemandForecaster
from app.ml.segmentation import CustomerSegmenter
from app.ml.anomaly_detection import AnomalyDetector
import pandas as pd
import os

router = APIRouter()

# Ensure models directory exists
os.makedirs("models", exist_ok=True)


@router.post("/sales-forecast/train", response_model=ModelRunResponse)
def train_sales_forecast(
    model_data: ModelRunCreate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Train a sales prediction model."""
    # Get sales data
    sales = db.query(Sale).filter(
        Sale.business_id == current_business.id,
        Sale.status == "completed"
    ).all()

    if len(sales) < 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient sales data. Need at least 30 completed sales."
        )

    # Convert to DataFrame
    df = pd.DataFrame([{
        'sale_date': s.sale_date,
        'total_amount': float(s.total_amount)
    } for s in sales])

    # Create model run
    new_model_run = ModelRun(
        business_id=current_business.id,
        model_type=ModelType.SALES_PREDICTION,
        model_name=model_data.model_name,
        algorithm=model_data.algorithm,
        training_start_date=min(s.sale_date for s in sales),
        training_end_date=max(s.sale_date for s in sales),
        hyperparameters=model_data.hyperparameters,
        status="training"
    )
    db.add(new_model_run)
    db.commit()
    db.refresh(new_model_run)

    try:
        # Train model
        predictor = SalesPredictor()
        metrics = predictor.train(df)

        if 'error' in metrics:
            new_model_run.status = "failed"
            new_model_run.error_message = metrics['error']
        else:
            # Save model
            model_path = f"models/sales_prediction_{new_model_run.id}.pkl"
            predictor.save_model(model_path)

            new_model_run.status = "completed"
            new_model_run.metrics = metrics
            new_model_run.model_path = model_path
            new_model_run.model_version = "1.0"
            new_model_run.training_samples = metrics.get('training_samples', len(df))

        db.commit()
    except Exception as e:
        new_model_run.status = "failed"
        new_model_run.error_message = str(e)
        db.commit()

    return ModelRunResponse.model_validate(new_model_run)


@router.post("/churn-prediction/train", response_model=ModelRunResponse)
def train_churn_prediction(
    model_data: ModelRunCreate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Train a customer churn prediction model."""
    from app.models.customer import Customer
    from app.models.sale import Sale

    # Get customer data with purchase history
    customers = db.query(Customer).filter(
        Customer.business_id == current_business.id
    ).all()

    if len(customers) < 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient customer data. Need at least 20 customers."
        )

    # Prepare customer data
    customer_data = []
    for customer in customers:
        # Get purchase statistics
        total_orders = db.query(func.count(Sale.id)).filter(
            Sale.customer_id == customer.id,
            Sale.status == "completed"
        ).scalar() or 0

        total_spending = db.query(func.sum(Sale.total_amount)).filter(
            Sale.customer_id == customer.id,
            Sale.status == "completed"
        ).scalar() or 0

        last_sale = db.query(Sale).filter(
            Sale.customer_id == customer.id,
            Sale.status == "completed"
        ).order_by(Sale.sale_date.desc()).first()

        customer_data.append({
            'customer_id': customer.id,
            'total_orders': total_orders,
            'total_spending': float(total_spending),
            'last_purchase_date': last_sale.sale_date if last_sale else None,
            'created_at': customer.created_at
        })

    df = pd.DataFrame(customer_data)

    # Create model run
    new_model_run = ModelRun(
        business_id=current_business.id,
        model_type=ModelType.CHURN_PREDICTION,
        model_name=model_data.model_name,
        algorithm=model_data.algorithm,
        hyperparameters=model_data.hyperparameters,
        status="training"
    )
    db.add(new_model_run)
    db.commit()
    db.refresh(new_model_run)

    try:
        # Train model
        predictor = ChurnPredictor()
        metrics = predictor.train(df)

        if 'error' in metrics:
            new_model_run.status = "failed"
            new_model_run.error_message = metrics['error']
        else:
            # Save model
            model_path = f"models/churn_prediction_{new_model_run.id}.pkl"
            predictor.save_model(model_path)

            new_model_run.status = "completed"
            new_model_run.metrics = metrics
            new_model_run.model_path = model_path
            new_model_run.model_version = "1.0"
            new_model_run.training_samples = metrics.get('training_samples', len(df))

        db.commit()
    except Exception as e:
        new_model_run.status = "failed"
        new_model_run.error_message = str(e)
        db.commit()

    return ModelRunResponse.model_validate(new_model_run)


@router.post("/demand-forecast/train", response_model=ModelRunResponse)
def train_demand_forecast(
    model_data: ModelRunCreate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Train a product demand forecasting model."""
    from app.models.sale import SaleItem
    from app.models.sale import Sale

    # Get sales items data
    sale_items = db.query(SaleItem).join(Sale).filter(
        Sale.business_id == current_business.id,
        Sale.status == "completed"
    ).all()

    if len(sale_items) < 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient sales data. Need at least 30 sale items."
        )

    # Convert to DataFrame
    df = pd.DataFrame([{
        'sale_date': item.sale.sale_date,
        'product_id': item.product_id,
        'quantity': item.quantity
    } for item in sale_items])

    # Create model run
    new_model_run = ModelRun(
        business_id=current_business.id,
        model_type=ModelType.DEMAND_FORECAST,
        model_name=model_data.model_name,
        algorithm=model_data.algorithm,
        hyperparameters=model_data.hyperparameters,
        status="training"
    )
    db.add(new_model_run)
    db.commit()
    db.refresh(new_model_run)

    try:
        # Train model
        forecaster = DemandForecaster()
        metrics = forecaster.train(df)

        if 'error' in metrics:
            new_model_run.status = "failed"
            new_model_run.error_message = metrics['error']
        else:
            # Save model
            model_path = f"models/demand_forecast_{new_model_run.id}.pkl"
            forecaster.save_model(model_path)

            new_model_run.status = "completed"
            new_model_run.metrics = metrics
            new_model_run.model_path = model_path
            new_model_run.model_version = "1.0"
            new_model_run.training_samples = metrics.get('training_samples', len(df))

        db.commit()
    except Exception as e:
        new_model_run.status = "failed"
        new_model_run.error_message = str(e)
        db.commit()

    return ModelRunResponse.model_validate(new_model_run)


@router.post("/segmentation/train", response_model=ModelRunResponse)
def train_segmentation(
    model_data: ModelRunCreate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Train a customer segmentation model."""
    from app.models.customer import Customer
    from app.models.sale import Sale

    # Get customer data
    customers = db.query(Customer).filter(
        Customer.business_id == current_business.id
    ).all()

    if len(customers) < 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient customer data. Need at least 20 customers."
        )

    # Prepare customer data
    customer_data = []
    for customer in customers:
        total_orders = db.query(func.count(Sale.id)).filter(
            Sale.customer_id == customer.id,
            Sale.status == "completed"
        ).scalar() or 0

        total_spending = db.query(func.sum(Sale.total_amount)).filter(
            Sale.customer_id == customer.id,
            Sale.status == "completed"
        ).scalar() or 0

        last_sale = db.query(Sale).filter(
            Sale.customer_id == customer.id,
            Sale.status == "completed"
        ).order_by(Sale.sale_date.desc()).first()

        customer_data.append({
            'customer_id': customer.id,
            'total_orders': total_orders,
            'total_spending': float(total_spending),
            'last_purchase_date': last_sale.sale_date if last_sale else None,
            'created_at': customer.created_at
        })

    df = pd.DataFrame(customer_data)

    # Create model run
    new_model_run = ModelRun(
        business_id=current_business.id,
        model_type=ModelType.SEGMENTATION,
        model_name=model_data.model_name,
        algorithm=model_data.algorithm,
        hyperparameters=model_data.hyperparameters,
        status="training"
    )
    db.add(new_model_run)
    db.commit()
    db.refresh(new_model_run)

    try:
        # Train model
        segmenter = CustomerSegmenter()
        metrics = segmenter.train(df, n_clusters=4)

        if 'error' in metrics:
            new_model_run.status = "failed"
            new_model_run.error_message = metrics['error']
        else:
            # Save model
            model_path = f"models/segmentation_{new_model_run.id}.pkl"
            segmenter.save_model(model_path)

            new_model_run.status = "completed"
            new_model_run.metrics = metrics
            new_model_run.model_path = model_path
            new_model_run.model_version = "1.0"
            new_model_run.training_samples = metrics.get('training_samples', len(df))

        db.commit()
    except Exception as e:
        new_model_run.status = "failed"
        new_model_run.error_message = str(e)
        db.commit()

    return ModelRunResponse.model_validate(new_model_run)


@router.post("/anomalies/train", response_model=ModelRunResponse)
def train_anomaly_detection(
    model_data: ModelRunCreate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Train an anomaly detection model."""
    # Get sales data
    sales = db.query(Sale).filter(
        Sale.business_id == current_business.id,
        Sale.status == "completed"
    ).all()

    if len(sales) < 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient sales data. Need at least 30 completed sales."
        )

    # Convert to DataFrame
    df = pd.DataFrame([{
        'sale_date': s.sale_date,
        'total_amount': float(s.total_amount)
    } for s in sales])

    # Create model run
    new_model_run = ModelRun(
        business_id=current_business.id,
        model_type=ModelType.ANOMALY_DETECTION,
        model_name=model_data.model_name,
        algorithm=model_data.algorithm,
        hyperparameters=model_data.hyperparameters,
        status="training"
    )
    db.add(new_model_run)
    db.commit()
    db.refresh(new_model_run)

    try:
        # Train model
        detector = AnomalyDetector()
        contamination = model_data.hyperparameters.get('contamination', 0.05) if model_data.hyperparameters else 0.05
        metrics = detector.train(df, contamination=contamination)

        if 'error' in metrics:
            new_model_run.status = "failed"
            new_model_run.error_message = metrics['error']
        else:
            # Save model
            model_path = f"models/anomaly_detection_{new_model_run.id}.pkl"
            detector.save_model(model_path)

            new_model_run.status = "completed"
            new_model_run.metrics = metrics
            new_model_run.model_path = model_path
            new_model_run.model_version = "1.0"
            new_model_run.training_samples = metrics.get('training_samples', len(df))

        db.commit()
    except Exception as e:
        new_model_run.status = "failed"
        new_model_run.error_message = str(e)
        db.commit()

    return ModelRunResponse.model_validate(new_model_run)


@router.get("/models/", response_model=List[ModelRunResponse])
def get_model_runs(
    model_type: Optional[ModelType] = None,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get all model runs for the business."""
    query = db.query(ModelRun).filter(ModelRun.business_id == current_business.id)

    if model_type:
        query = query.filter(ModelRun.model_type == model_type)

    model_runs = query.order_by(ModelRun.created_at.desc()).all()
    return [ModelRunResponse.model_validate(run) for run in model_runs]


@router.get("/models/{model_id}", response_model=ModelRunResponse)
def get_model_run(
    model_id: int,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get a specific model run by ID."""
    model_run = db.query(ModelRun).filter(
        ModelRun.id == model_id,
        ModelRun.business_id == current_business.id
    ).first()
    if not model_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model run not found"
        )
    return ModelRunResponse.model_validate(model_run)


@router.get("/models/{model_id}/predictions", response_model=List[PredictionResponse])
def get_predictions(
    model_id: int,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get predictions for a specific model run."""
    model_run = db.query(ModelRun).filter(
        ModelRun.id == model_id,
        ModelRun.business_id == current_business.id
    ).first()
    if not model_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model run not found"
        )

    predictions = db.query(model_run.predictions).all()
    return [PredictionResponse.model_validate(pred) for pred in predictions]
