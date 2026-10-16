from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from app.db.database import get_db
from app.models.sale import Sale
from app.models.customer import Customer
from app.models.product import Product
from app.models.expense import Expense
from app.core.deps import get_current_user, get_current_business
from app.schemas.dashboard import DashboardMetrics, DashboardAnalytics
from app.models.user import User

router = APIRouter()


@router.get("/metrics", response_model=DashboardMetrics)
def get_dashboard_metrics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get dashboard metrics for the business."""
    # Default to last 30 days if no dates provided
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Calculate previous period for comparison
    period_length = (end_date - start_date).days
    previous_start = start_date - timedelta(days=period_length)
    previous_end = start_date

    # Current period metrics
    current_sales = db.query(func.sum(Sale.total_amount)).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == "completed"
    ).scalar() or Decimal('0')

    current_profit = db.query(func.sum(Sale.total_profit)).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == "completed"
    ).scalar() or Decimal('0')

    current_orders = db.query(func.count(Sale.id)).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == "completed"
    ).scalar() or 0

    total_customers = db.query(func.count(Customer.id)).filter(
        Customer.business_id == current_business.id
    ).scalar() or 0

    # Previous period metrics
    previous_sales = db.query(func.sum(Sale.total_amount)).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= previous_start,
        Sale.sale_date <= previous_end,
        Sale.status == "completed"
    ).scalar() or Decimal('0')

    previous_profit = db.query(func.sum(Sale.total_profit)).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= previous_start,
        Sale.sale_date <= previous_end,
        Sale.status == "completed"
    ).scalar() or Decimal('0')

    # Calculate growth and margin
    sales_growth = None
    if previous_sales > 0:
        sales_growth = ((current_sales - previous_sales) / previous_sales) * 100

    profit_margin = Decimal('0')
    if current_sales > 0:
        profit_margin = (current_profit / current_sales) * 100

    return DashboardMetrics(
        total_revenue=current_sales,
        total_profit=current_profit,
        total_orders=current_orders,
        total_customers=total_customers,
        sales_growth=sales_growth,
        profit_margin=profit_margin,
        previous_period_revenue=previous_sales,
        previous_period_profit=previous_profit
    )


@router.get("/analytics", response_model=DashboardAnalytics)
def get_dashboard_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get dashboard analytics including trends and top items."""
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Revenue trends by day
    revenue_trends = db.query(
        func.date(Sale.sale_date).label('date'),
        func.sum(Sale.total_amount).label('revenue')
    ).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == "completed"
    ).group_by(func.date(Sale.sale_date)).order_by(func.date(Sale.sale_date)).all()

    revenue_trends_data = [
        {"date": str(r.date), "revenue": float(r.revenue)} for r in revenue_trends
    ]

    # Sales by category
    from app.models.sale import SaleItem
    from app.models.product import Product, Category

    sales_by_category = db.query(
        Category.name.label('category'),
        func.sum(SaleItem.total_price).label('total')
    ).join(
        Product, SaleItem.product_id == Product.id
    ).join(
        Category, Product.category_id == Category.id
    ).join(
        Sale, SaleItem.sale_id == Sale.id
    ).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == "completed"
    ).group_by(Category.name).all()

    sales_by_category_data = [
        {"category": s.category, "total": float(s.total)} for s in sales_by_category
    ]

    # Top selling products
    top_products = db.query(
        Product.name,
        func.sum(SaleItem.quantity).label('total_quantity'),
        func.sum(SaleItem.total_price).label('total_revenue')
    ).join(
        SaleItem, Product.id == SaleItem.product_id
    ).join(
        Sale, SaleItem.sale_id == Sale.id
    ).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == "completed"
    ).group_by(Product.id, Product.name).order_by(
        func.sum(SaleItem.total_price).desc()
    ).limit(10).all()

    top_products_data = [
        {
            "name": p.name,
            "total_quantity": p.total_quantity,
            "total_revenue": float(p.total_revenue)
        } for p in top_products
    ]

    # Recent transactions
    recent_transactions = db.query(Sale).filter(
        Sale.business_id == current_business.id
    ).order_by(Sale.created_at.desc()).limit(10).all()

    recent_transactions_data = [
        {
            "id": s.id,
            "invoice_number": s.invoice_number,
            "sale_date": str(s.sale_date),
            "total_amount": float(s.total_amount),
            "status": s.status
        } for s in recent_transactions
    ]

    # Inventory warnings (low stock)
    inventory_warnings = db.query(Product).filter(
        Product.business_id == current_business.id,
        Product.stock_quantity <= Product.low_stock_threshold
    ).all()

    inventory_warnings_data = [
        {
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "stock_quantity": p.stock_quantity,
            "low_stock_threshold": p.low_stock_threshold
        } for p in inventory_warnings
    ]

    # AI insights (placeholder - will be enhanced with ML)
    ai_insights = [
        "Review top-selling products for potential expansion",
        "Monitor inventory levels for low-stock items",
        "Analyze sales trends for seasonal patterns"
    ]

    return DashboardAnalytics(
        revenue_trends=revenue_trends_data,
        sales_by_category=sales_by_category_data,
        top_selling_products=top_products_data,
        recent_transactions=recent_transactions_data,
        inventory_warnings=inventory_warnings_data,
        ai_insights=ai_insights
    )
