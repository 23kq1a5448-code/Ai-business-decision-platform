from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class ModelType(str, enum.Enum):
    SALES_PREDICTION = "sales_prediction"
    CHURN_PREDICTION = "churn_prediction"
    DEMAND_FORECAST = "demand_forecast"
    SEGMENTATION = "segmentation"
    ANOMALY_DETECTION = "anomaly_detection"


class ModelRun(Base):
    __tablename__ = "model_runs"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    model_type = Column(Enum(ModelType), nullable=False)
    model_name = Column(String(255), nullable=False)
    model_version = Column(String(50))
    algorithm = Column(String(100))  # RandomForest, XGBoost, Prophet, etc.
    training_start_date = Column(DateTime(timezone=True))
    training_end_date = Column(DateTime(timezone=True))
    training_samples = Column(Integer)
    metrics = Column(JSON)  # MAE, RMSE, R2, precision, recall, F1, etc.
    hyperparameters = Column(JSON)
    feature_importance = Column(JSON)
    model_path = Column(String(500))  # Path to saved model file
    scaler_path = Column(String(500))  # Path to saved scaler
    status = Column(String(50), default="completed")  # training, completed, failed
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    business = relationship("Business", back_populates="model_runs")
    predictions = relationship("Prediction", back_populates="model_run")

    def __repr__(self):
        return f"<ModelRun(id={self.id}, model_type={self.model_type}, algorithm={self.algorithm})>"


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    model_run_id = Column(Integer, ForeignKey("model_runs.id"), nullable=False)
    entity_type = Column(String(50))  # product, customer, sale, etc.
    entity_id = Column(Integer)
    prediction_date = Column(DateTime(timezone=True), nullable=False)
    predicted_value = Column(Numeric(15, 4))
    prediction_label = Column(String(100))  # For classification
    prediction_probability = Column(Numeric(5, 4))  # For classification probability
    confidence = Column(Numeric(5, 4))
    features = Column(JSON)  # Input features used for prediction
    prediction_metadata = Column(JSON)  # Additional prediction metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    model_run = relationship("ModelRun", back_populates="predictions")

    def __repr__(self):
        return f"<Prediction(id={self.id}, entity_type={self.entity_type}, entity_id={self.entity_id}, value={self.predicted_value})>"
