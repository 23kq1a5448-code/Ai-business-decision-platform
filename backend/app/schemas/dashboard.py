from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


class DashboardMetrics(BaseModel):
    total_revenue: Decimal
    total_profit: Decimal
    total_orders: int
    total_customers: int
    sales_growth: Optional[Decimal]
    profit_margin: Decimal
    previous_period_revenue: Optional[Decimal]
    previous_period_profit: Optional[Decimal]


class DashboardAnalytics(BaseModel):
    revenue_trends: List[Dict[str, Any]]
    sales_by_category: List[Dict[str, Any]]
    top_selling_products: List[Dict[str, Any]]
    recent_transactions: List[Dict[str, Any]]
    inventory_warnings: List[Dict[str, Any]]
    ai_insights: List[str]
