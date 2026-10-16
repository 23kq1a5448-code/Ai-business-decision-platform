from pydantic import BaseModel
from typing import Optional, Any, Dict
from datetime import datetime
from app.models.recommendation import ImpactCategory, RecommendationStatus


class RecommendationCreate(BaseModel):
    title: str
    description: str
    evidence: Optional[Dict[str, Any]] = None
    impact_category: ImpactCategory = ImpactCategory.MEDIUM
    confidence: str = "medium"
    suggested_action: Optional[str] = None
    related_page: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None


class RecommendationUpdate(BaseModel):
    status: Optional[RecommendationStatus] = None


class RecommendationResponse(BaseModel):
    id: int
    business_id: int
    title: str
    description: str
    evidence: Optional[Dict[str, Any]]
    impact_category: ImpactCategory
    confidence: str
    suggested_action: Optional[str]
    related_page: Optional[str]
    related_entity_type: Optional[str]
    related_entity_id: Optional[int]
    status: RecommendationStatus
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
