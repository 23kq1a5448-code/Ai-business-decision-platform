from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    contact_person = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    address = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    products = relationship("Product", back_populates="supplier")

    def __repr__(self):
        return f"<Supplier(id={self.id}, name={self.name})>"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    name = Column(String(255), nullable=False)
    sku = Column(String(100), unique=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    description = Column(Text)
    selling_price = Column(Numeric(10, 2), nullable=False)
    cost_price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0)
    low_stock_threshold = Column(Integer, default=10)
    predicted_demand = Column(Integer)  # Forecasted demand
    suggested_reorder = Column(Integer)  # Suggested reorder quantity
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    business = relationship("Business", back_populates="products")
    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    sale_items = relationship("SaleItem", back_populates="product")
    inventory_movements = relationship("InventoryMovement", back_populates="product")

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, sku={self.sku})>"
