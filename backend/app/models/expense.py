from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class ExpenseCategory(str, enum.Enum):
    RENT = "rent"
    UTILITIES = "utilities"
    SALARIES = "salaries"
    MARKETING = "marketing"
    SUPPLIES = "supplies"
    TRAVEL = "travel"
    EQUIPMENT = "equipment"
    SOFTWARE = "software"
    INSURANCE = "insurance"
    OTHER = "other"


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    category = Column(Enum(ExpenseCategory), nullable=False)
    description = Column(String(500))
    expense_date = Column(DateTime(timezone=True), nullable=False)
    payment_method = Column(String(50))
    vendor = Column(String(255))
    receipt_number = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    business = relationship("Business", back_populates="expenses")

    def __repr__(self):
        return f"<Expense(id={self.id}, amount={self.amount}, category={self.category}, date={self.expense_date})>"
