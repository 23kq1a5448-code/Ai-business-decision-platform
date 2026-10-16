from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class SaleStatus(str, enum.Enum):
    COMPLETED = "completed"
    PENDING = "pending"
    CANCELLED = "cancelled"


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    invoice_number = Column(String(100), unique=True, nullable=False)
    sale_date = Column(DateTime(timezone=True), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    total_amount = Column(Numeric(12, 2), nullable=False)
    total_cost = Column(Numeric(12, 2), nullable=False)
    total_profit = Column(Numeric(12, 2), nullable=False)
    status = Column(Enum(SaleStatus), default=SaleStatus.COMPLETED, nullable=False)
    payment_method = Column(String(50))
    region = Column(String(100))
    notes = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    business = relationship("Business", back_populates="sales")
    customer = relationship("Customer")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Sale(id={self.id}, invoice_number={self.invoice_number}, total_amount={self.total_amount})>"


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    unit_cost = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False)
    total_cost = Column(Numeric(12, 2), nullable=False)
    total_profit = Column(Numeric(12, 2), nullable=False)

    # Relationships
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")
    customer = relationship("Customer", back_populates="sale_items")

    def __repr__(self):
        return f"<SaleItem(id={self.id}, sale_id={self.sale_id}, product_id={self.product_id}, quantity={self.quantity})>"
