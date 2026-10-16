from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.business import MembershipRole


class BusinessCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    description: Optional[str] = None


class BusinessResponse(BaseModel):
    id: int
    name: str
    industry: Optional[str]
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class BusinessMembershipCreate(BaseModel):
    business_id: int
    role: MembershipRole = MembershipRole.MEMBER
