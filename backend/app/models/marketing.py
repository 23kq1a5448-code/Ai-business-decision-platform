from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class CampaignStatus(str, enum.Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MarketingCampaign(Base):
    __tablename__ = "marketing_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    budget = Column(Numeric(12, 2))
    actual_cost = Column(Numeric(12, 2))
    status = Column(Enum(CampaignStatus), default=CampaignStatus.PLANNED)
    campaign_type = Column(String(50))  # email, social_media, paid_ads, etc.
    target_audience = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    business = relationship("Business", back_populates="campaigns")
    interactions = relationship("CustomerInteraction", back_populates="campaign")

    def __repr__(self):
        return f"<MarketingCampaign(id={self.id}, name={self.name}, status={self.status})>"


class InteractionType(str, enum.Enum):
    EMAIL = "email"
    PHONE = "phone"
    MEETING = "meeting"
    SOCIAL_MEDIA = "social_media"
    OTHER = "other"


class CustomerInteraction(Base):
    __tablename__ = "customer_interactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    campaign_id = Column(Integer, ForeignKey("marketing_campaigns.id"))
    interaction_type = Column(Enum(InteractionType), nullable=False)
    interaction_date = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text)
    outcome = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="interactions")
    campaign = relationship("MarketingCampaign", back_populates="interactions")

    def __repr__(self):
        return f"<CustomerInteraction(id={self.id}, customer_id={self.customer_id}, type={self.interaction_type})>"
