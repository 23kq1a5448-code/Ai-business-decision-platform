from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class MovementType(str, enum.Enum):
    PURCHASE = "purchase"
    SALE = "sale"
    RETURN = "return"
    ADJUSTMENT = "adjustment"
    TRANSFER = "transfer"


class InventoryMovement(Base):
    __tablename__ = "inventory_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    movement_type = Column(Enum(MovementType), nullable=False)
    quantity = Column(Integer, nullable=False)
    quantity_before = Column(Integer, nullable=False)
    quantity_after = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(10, 2))
    reference_type = Column(String(50))  # sale, purchase_order, etc.
    reference_id = Column(Integer)
    notes = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="inventory_movements")

    def __repr__(self):
        return f"<InventoryMovement(id={self.id}, product_id={self.product_id}, type={self.movement_type}, quantity={self.quantity})>"
