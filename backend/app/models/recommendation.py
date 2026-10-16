from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class ImpactCategory(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecommendationStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DISMISSED = "dismissed"


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(JSON)  # Data supporting the recommendation
    impact_category = Column(Enum(ImpactCategory), default=ImpactCategory.MEDIUM)
    confidence = Column(String(20))  # high, medium, low
    suggested_action = Column(Text)
    related_page = Column(String(100))  # Dashboard, sales, customers, etc.
    related_entity_type = Column(String(50))
    related_entity_id = Column(Integer)
    status = Column(Enum(RecommendationStatus), default=RecommendationStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    business = relationship("Business", back_populates="recommendations")

    def __repr__(self):
        return f"<Recommendation(id={self.id}, title={self.title}, impact={self.impact_category})>"
