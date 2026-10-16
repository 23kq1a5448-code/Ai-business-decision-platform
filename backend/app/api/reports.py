from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
from app.db.database import get_db
from app.models.sale import Sale
from app.models.expense import Expense
from app.models.customer import Customer
from app.models.product import Product
from app.core.deps import get_current_user, get_current_business
from app.models.user import User
import csv
from io import StringIO

router = APIRouter()


@router.get("/sales/summary")
def get_sales_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Generate a sales summary report."""
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    sales = db.query(Sale).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == "completed"
    ).all()

    total_revenue = sum(s.total_amount for s in sales)
    total_profit = sum(s.total_profit for s in sales)
    total_orders = len(sales)

    return {
        "period": {
            "start_date": str(start_date),
            "end_date": str(end_date)
        },
        "summary": {
            "total_revenue": float(total_revenue),
            "total_profit": float(total_profit),
            "total_orders": total_orders,
            "average_order_value": float(total_revenue / total_orders) if total_orders > 0 else 0
        },
        "sales": [
            {
                "invoice_number": s.invoice_number,
                "sale_date": str(s.sale_date),
                "total_amount": float(s.total_amount),
                "total_profit": float(s.total_profit),
                "status": s.status
            } for s in sales
        ]
    }


@router.get("/sales/export")
def export_sales_csv(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Export sales data as CSV."""
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    sales = db.query(Sale).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == "completed"
    ).all()

    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Invoice Number', 'Sale Date', 'Total Amount', 'Total Cost', 'Total Profit', 'Status', 'Payment Method', 'Region'])

    for sale in sales:
        writer.writerow([
            sale.invoice_number,
            str(sale.sale_date),
            float(sale.total_amount),
            float(sale.total_cost),
            float(sale.total_profit),
            sale.status.value,
            sale.payment_method or '',
            sale.region or ''
        ])

    return {
        "filename": f"sales_report_{start_date.date()}_{end_date.date()}.csv",
        "content": output.getvalue()
    }


@router.get("/expenses/summary")
def get_expenses_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Generate an expenses summary report."""
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    expenses = db.query(Expense).filter(
        Expense.business_id == current_business.id,
        Expense.expense_date >= start_date,
        Expense.expense_date <= end_date
    ).all()

    total_expenses = sum(e.amount for e in expenses)

    # Group by category
    from collections import defaultdict
    category_totals = defaultdict(float)
    for expense in expenses:
        category_totals[expense.category.value] += float(expense.amount)

    return {
        "period": {
            "start_date": str(start_date),
            "end_date": str(end_date)
        },
        "summary": {
            "total_expenses": float(total_expenses),
            "category_breakdown": dict(category_totals)
        },
        "expenses": [
            {
                "category": e.category.value,
                "amount": float(e.amount),
                "description": e.description,
                "expense_date": str(e.expense_date),
                "vendor": e.vendor
            } for e in expenses
        ]
    }


@router.get("/customers/summary")
def get_customers_report(
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Generate a customers summary report."""
    customers = db.query(Customer).filter(
        Customer.business_id == current_business.id
    ).all()

    total_customers = len(customers)

    # Segment breakdown
    from collections import defaultdict
    segment_counts = defaultdict(int)
    churn_risk_counts = defaultdict(int)

    for customer in customers:
        if customer.segment:
            segment_counts[customer.segment] += 1
        if customer.churn_risk:
            churn_risk_counts[customer.churn_risk] += 1

    return {
        "summary": {
            "total_customers": total_customers,
            "segment_breakdown": dict(segment_counts),
            "churn_risk_breakdown": dict(churn_risk_counts)
        },
        "customers": [
            {
                "name": c.name,
                "email": c.email,
                "segment": c.segment,
                "churn_risk": c.churn_risk,
                "created_at": str(c.created_at)
            } for c in customers
        ]
    }


@router.get("/executive-summary")
def get_executive_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_business = Depends(get_current_business),
    db: Session = Depends(get_db)
):
    """Generate an executive summary with AI insights."""
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Get key metrics
    total_revenue = db.query(func.sum(Sale.total_amount)).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == "completed"
    ).scalar() or Decimal('0')

    total_profit = db.query(func.sum(Sale.total_profit)).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == "completed"
    ).scalar() or Decimal('0')

    total_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.business_id == current_business.id,
        Expense.expense_date >= start_date,
        Expense.expense_date <= end_date
    ).scalar() or Decimal('0')

    total_orders = db.query(func.count(Sale.id)).filter(
        Sale.business_id == current_business.id,
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date,
        Sale.status == "completed"
    ).scalar() or 0

    total_customers = db.query(func.count(Customer.id)).filter(
        Customer.business_id == current_business.id
    ).scalar() or 0

    # Generate insights
    insights = []

    if total_revenue > 0:
        profit_margin = (total_profit / total_revenue) * 100
        insights.append(f"Profit margin for the period is {profit_margin:.2f}%")

    if total_orders > 0:
        avg_order_value = total_revenue / total_orders
        insights.append(f"Average order value is ${avg_order_value:.2f}")

    low_stock = db.query(Product).filter(
        Product.business_id == current_business.id,
        Product.stock_quantity <= Product.low_stock_threshold
    ).count()
    if low_stock > 0:
        insights.append(f"{low_stock} products are running low on stock")

    high_churn = db.query(Customer).filter(
        Customer.business_id == current_business.id,
        Customer.churn_risk == "high"
    ).count()
    if high_churn > 0:
        insights.append(f"{high_churn} customers are at high risk of churning")

    return {
        "period": {
            "start_date": str(start_date),
            "end_date": str(end_date)
        },
        "metrics": {
            "total_revenue": float(total_revenue),
            "total_profit": float(total_profit),
            "total_expenses": float(total_expenses),
            "total_orders": total_orders,
            "total_customers": total_customers
        },
        "ai_insights": insights
    }
