from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class MembershipRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    industry = Column(String(255))
    description = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    memberships = relationship("BusinessMembership", back_populates="business", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="business", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="business", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="business", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="business", cascade="all, delete-orphan")
    campaigns = relationship("MarketingCampaign", back_populates="business", cascade="all, delete-orphan")
    model_runs = relationship("ModelRun", back_populates="business", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="business", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="business", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="business", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="business", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Business(id={self.id}, name={self.name})>"


class BusinessMembership(Base):
    __tablename__ = "business_memberships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    role = Column(Enum(MembershipRole), default=MembershipRole.MEMBER, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
    business = relationship("Business", back_populates="memberships")

    def __repr__(self):
        return f"<BusinessMembership(user_id={self.user_id}, business_id={self.business_id}, role={self.role})>"
