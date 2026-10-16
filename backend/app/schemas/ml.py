from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime
from decimal import Decimal
from app.models.ml import ModelType


class ModelRunCreate(BaseModel):
    model_type: ModelType
    model_name: str
    algorithm: str
    training_start_date: Optional[datetime] = None
    training_end_date: Optional[datetime] = None
    hyperparameters: Optional[Dict[str, Any]] = None


class ModelRunResponse(BaseModel):
    id: int
    business_id: int
    model_type: ModelType
    model_name: str
    model_version: Optional[str]
    algorithm: str
    training_start_date: Optional[datetime]
    training_end_date: Optional[datetime]
    training_samples: Optional[int]
    metrics: Optional[Dict[str, Any]]
    hyperparameters: Optional[Dict[str, Any]]
    feature_importance: Optional[Dict[str, Any]]
    model_path: Optional[str]
    scaler_path: Optional[str]
    status: str
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PredictionResponse(BaseModel):
    id: int
    model_run_id: int
    entity_type: Optional[str]
    entity_id: Optional[int]
    prediction_date: datetime
    predicted_value: Optional[Decimal]
    prediction_label: Optional[str]
    prediction_probability: Optional[Decimal]
    confidence: Optional[Decimal]
    features: Optional[Dict[str, Any]]
    prediction_metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True
