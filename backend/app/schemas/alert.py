from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime
from app.models.alert import AlertType, AlertSeverity, AlertStatus


class AlertCreate(BaseModel):
    alert_type: AlertType
    severity: AlertSeverity = AlertSeverity.WARNING
    title: str
    description: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    metric_value: Optional[str] = None
    threshold_value: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None


class AlertResponse(BaseModel):
    id: int
    business_id: int
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: Optional[str]
    entity_type: Optional[str]
    entity_id: Optional[int]
    metric_value: Optional[str]
    threshold_value: Optional[str]
    metadata: Optional[Dict[str, Any]]
    status: AlertStatus
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
