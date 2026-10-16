from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.db.database import get_db
from app.models.product import Product, Category, Supplier
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse,
    CategoryCreate, CategoryResponse,
    SupplierCreate, SupplierResponse
)
from app.core.deps import get_current_user, get_current_business
from app.models.user import User

router = APIRouter()


# Category endpoints
@router.post("/categories/", response_model=CategoryResponse)
def create_category(
    category_data: CategoryCreate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Create a new product category."""
    existing = db.query(Category).filter(Category.name == category_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already exists"
        )

    new_category = Category(**category_data.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return CategoryResponse.model_validate(new_category)


@router.get("/categories/", response_model=List[CategoryResponse])
def get_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all product categories."""
    categories = db.query(Category).offset(skip).limit(limit).all()
    return [CategoryResponse.model_validate(cat) for cat in categories]


# Supplier endpoints
@router.post("/suppliers/", response_model=SupplierResponse)
def create_supplier(
    supplier_data: SupplierCreate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Create a new supplier."""
    new_supplier = Supplier(**supplier_data.model_dump())
    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)
    return SupplierResponse.model_validate(new_supplier)


@router.get("/suppliers/", response_model=List[SupplierResponse])
def get_suppliers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all suppliers."""
    suppliers = db.query(Supplier).offset(skip).limit(limit).all()
    return [SupplierResponse.model_validate(sup) for sup in suppliers]


# Product endpoints
@router.post("/", response_model=ProductResponse)
def create_product(
    product_data: ProductCreate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Create a new product."""
    # Validate SKU uniqueness if provided
    if product_data.sku:
        existing = db.query(Product).filter(Product.sku == product_data.sku).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SKU already exists"
            )

    # Validate category if provided
    if product_data.category_id:
        category = db.query(Category).filter(Category.id == product_data.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

    # Validate supplier if provided
    if product_data.supplier_id:
        supplier = db.query(Supplier).filter(Supplier.id == product_data.supplier_id).first()
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Supplier not found"
            )

    new_product = Product(
        business_id=current_business.id,
        **product_data.model_dump()
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return ProductResponse.model_validate(new_product)


@router.get("/", response_model=List[ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    low_stock_only: bool = False,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get products with filtering options."""
    query = db.query(Product).filter(Product.business_id == current_business.id)

    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.sku.ilike(f"%{search}%")
            )
        )
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if supplier_id:
        query = query.filter(Product.supplier_id == supplier_id)
    if low_stock_only:
        query = query.filter(Product.stock_quantity <= Product.low_stock_threshold)

    products = query.order_by(Product.name).offset(skip).limit(limit).all()
    return [ProductResponse.model_validate(product) for product in products]


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get a specific product by ID."""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.business_id == current_business.id
    ).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Update a product."""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.business_id == current_business.id
    ).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return ProductResponse.model_validate(product)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Delete a product."""
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.business_id == current_business.id
    ).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}
