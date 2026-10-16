from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


class FinancialAnalytics(BaseModel):
    total_revenue: Decimal
    total_cost: Decimal
    gross_profit: Decimal
    operating_expenses: Decimal
    net_profit: Decimal
    profit_margin: Decimal
    monthly_trends: List[Dict[str, Any]]
    product_profitability: List[Dict[str, Any]]
    expense_categories: List[Dict[str, Any]]


class SalesAnalytics(BaseModel):
    total_sales: Decimal
    total_orders: int
    average_order_value: Decimal
    sales_by_region: List[Dict[str, Any]]
    sales_by_category: List[Dict[str, Any]]
    top_products: List[Dict[str, Any]]
    monthly_sales: List[Dict[str, Any]]
