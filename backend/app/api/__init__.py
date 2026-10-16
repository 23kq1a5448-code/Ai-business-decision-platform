from fastapi import APIRouter
from app.api import auth, users, businesses, dashboard, sales, customers, products, inventory, expenses, analytics, ml, recommendations, chat, reports, alerts

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(businesses.router, prefix="/businesses", tags=["Businesses"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(sales.router, prefix="/sales", tags=["Sales"])
api_router.include_router(customers.router, prefix="/customers", tags=["Customers"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(ml.router, prefix="/ml", tags=["Machine Learning"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
