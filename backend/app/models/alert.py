from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class AlertType(str, enum.Enum):
    LOW_STOCK = "low_stock"
    SALES_ANOMALY = "sales_anomaly"
    HIGH_CHURN_RISK = "high_churn_risk"
    REVENUE_DROP = "revenue_drop"
    EXPENSE_SPIKE = "expense_spike"
    OTHER = "other"


class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), default=AlertSeverity.WARNING)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    entity_type = Column(String(50))  # product, customer, etc.
    entity_id = Column(Integer)
    metric_value = Column(String(255))
    threshold_value = Column(String(255))
    metadata = Column(JSON)
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE)
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    business = relationship("Business", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(id={self.id}, type={self.alert_type}, severity={self.severity}, title={self.title})>"
