from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.marketing import CampaignStatus, InteractionType


class MarketingCampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[Decimal] = None
    campaign_type: Optional[str] = None
    target_audience: Optional[str] = None


class MarketingCampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[Decimal] = None
    actual_cost: Optional[Decimal] = None
    status: Optional[CampaignStatus] = None
    campaign_type: Optional[str] = None
    target_audience: Optional[str] = None


class MarketingCampaignResponse(BaseModel):
    id: int
    business_id: int
    name: str
    description: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    budget: Optional[Decimal]
    actual_cost: Optional[Decimal]
    status: CampaignStatus
    campaign_type: Optional[str]
    target_audience: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CustomerInteractionCreate(BaseModel):
    customer_id: int
    campaign_id: Optional[int] = None
    interaction_type: InteractionType
    notes: Optional[str] = None
    outcome: Optional[str] = None


class CustomerInteractionResponse(BaseModel):
    id: int
    customer_id: int
    campaign_id: Optional[int]
    interaction_type: InteractionType
    interaction_date: datetime
    notes: Optional[str]
    outcome: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
