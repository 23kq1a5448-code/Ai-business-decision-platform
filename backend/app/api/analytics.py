from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from app.db.database import get_db
from app.models.sale import Sale, SaleItem
from app.models.expense import Expense
from app.models.product import Product
from app.core.deps import get_current_user, get_current_business
from app.schemas.analytics import FinancialAnalytics, SalesAnalytics

router = APIRouter()


@router.get("/financial", response_model=FinancialAnalytics)
def get_financial_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get financial analytics including revenue, costs, and profit."""
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Total revenue
    total_revenue = db.query(func.sum(Sale.total_amount)).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == "completed"
    ).scalar() or Decimal('0')

    # Total cost (from sales)
    total_cost = db.query(func.sum(Sale.total_cost)).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == "completed"
    ).scalar() or Decimal('0')

    # Gross profit
    gross_profit = total_revenue - total_cost

    # Operating expenses
    operating_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.business_id == current_business.id,
        Expense.expense_date >= start_date,
        Expense.expense_date <= end_date
    ).scalar() or Decimal('0')

    # Net profit
    net_profit = gross_profit - operating_expenses

    # Profit margin
    profit_margin = Decimal('0')
    if total_revenue > 0:
        profit_margin = (net_profit / total_revenue) * 100

    # Monthly trends
    monthly_trends = db.query(
        func.strftime('%Y-%m', Sale.sale_date).label('month'),
        func.sum(Sale.total_amount).label('revenue'),
        func.sum(Sale.total_cost).label('cost'),
        func.sum(Sale.total_profit).label('profit')
    ).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == "completed"
    ).group_by(func.strftime('%Y-%m', Sale.sale_date)).order_by(
        func.strftime('%Y-%m', Sale.sale_date)
    ).all()

    monthly_trends_data = [
        {
            "month": m.month,
            "revenue": float(m.revenue),
            "cost": float(m.cost),
            "profit": float(m.profit)
        } for m in monthly_trends
    ]

    # Product profitability
    product_profitability = db.query(
        Product.name,
        func.sum(SaleItem.total_price).label('revenue'),
        func.sum(SaleItem.total_cost).label('cost'),
        func.sum(SaleItem.total_profit).label('profit')
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
        func.sum(SaleItem.total_profit).desc()
    ).limit(20).all()

    product_profitability_data = [
        {
            "name": p.name,
            "revenue": float(p.revenue),
            "cost": float(p.cost),
            "profit": float(p.profit)
        } for p in product_profitability
    ]

    # Expense categories
    expense_categories = db.query(
        Expense.category,
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.business_id == current_business.id,
        Expense.expense_date >= start_date,
        Expense.expense_date <= end_date
    ).group_by(Expense.category).all()

    expense_categories_data = [
        {"category": e.category.value, "total": float(e.total)} for e in expense_categories
    ]

    return FinancialAnalytics(
        total_revenue=total_revenue,
        total_cost=total_cost,
        gross_profit=gross_profit,
        operating_expenses=operating_expenses,
        net_profit=net_profit,
        profit_margin=profit_margin,
        monthly_trends=monthly_trends_data,
        product_profitability=product_profitability_data,
        expense_categories=expense_categories_data
    )


@router.get("/sales", response_model=SalesAnalytics)
def get_sales_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Get sales analytics including regional and category breakdowns."""
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Total sales
    total_sales = db.query(func.sum(Sale.total_amount)).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == "completed"
    ).scalar() or Decimal('0')

    # Total orders
    total_orders = db.query(func.count(Sale.id)).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == "completed"
    ).scalar() or 0

    # Average order value
    average_order_value = Decimal('0')
    if total_orders > 0:
        average_order_value = total_sales / total_orders

    # Sales by region
    sales_by_region = db.query(
        Sale.region,
        func.sum(Sale.total_amount).label('total'),
        func.count(Sale.id).label('orders')
    ).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == "completed"
    ).group_by(Sale.region).all()

    sales_by_region_data = [
        {
            "region": r.region or "Unknown",
            "total": float(r.total),
            "orders": r.orders
        } for r in sales_by_region
    ]

    # Sales by category
    from app.models.product import Category
    sales_by_category = db.query(
        Category.name,
        func.sum(SaleItem.total_price).label('total'),
        func.count(Sale.id).label('orders')
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
        {
            "category": c.name,
            "total": float(c.total),
            "orders": c.orders
        } for c in sales_by_category
    ]

    # Top products
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

    # Monthly sales
    monthly_sales = db.query(
        func.strftime('%Y-%m', Sale.sale_date).label('month'),
        func.sum(Sale.total_amount).label('total'),
        func.count(Sale.id).label('orders')
    ).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == "completed"
    ).group_by(func.strftime('%Y-%m', Sale.sale_date)).order_by(
        func.strftime('%Y-%m', Sale.sale_date)
    ).all()

    monthly_sales_data = [
        {
            "month": m.month,
            "total": float(m.total),
            "orders": m.orders
        } for m in monthly_sales
    ]

    return SalesAnalytics(
        total_sales=total_sales,
        total_orders=total_orders,
        average_order_value=average_order_value,
        sales_by_region=sales_by_region_data,
        sales_by_category=sales_by_category_data,
        top_products=top_products_data,
        monthly_sales=monthly_sales_data
    )
