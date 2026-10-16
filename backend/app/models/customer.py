from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    segment = Column(String(50))  # RFM segment: loyal, high-value, new, at-risk
    churn_risk = Column(String(20))  # low, medium, high
    churn_probability = Column(Numeric(5, 4))  # 0.0000 to 1.0000
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    business = relationship("Business", back_populates="customers")
    sale_items = relationship("SaleItem", back_populates="customer")
    interactions = relationship("CustomerInteraction", back_populates="customer")

    def __repr__(self):
        return f"<Customer(id={self.id}, name={self.name}, business_id={self.business_id})>"
