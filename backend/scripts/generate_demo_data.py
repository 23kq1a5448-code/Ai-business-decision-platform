"""
Synthetic Demo Data Generator
Generates realistic business data for testing the platform.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from random import randint, choice, uniform
from decimal import Decimal
from app.db.database import SessionLocal, Base, engine
from app.models import (
    User, Business, BusinessMembership, Customer, Product, Category, Supplier,
    Sale, SaleItem, InventoryMovement, Expense, MarketingCampaign
)
from app.core.security import get_password_hash
from app.models.user import UserRole
from app.models.business import MembershipRole


def generate_demo_data():
    """Generate synthetic demo data for testing."""
    db = SessionLocal()

    print("Generating demo data...")

    # Create demo user
    demo_user = User(
        email="demo@example.com",
        full_name="Demo User",
        hashed_password=get_password_hash("demo123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(demo_user)
    db.flush()

    # Create demo business
    demo_business = Business(
        name="Demo Tech Solutions",
        industry="Technology",
        description="A sample technology business for demonstration"
    )
    db.add(demo_business)
    db.flush()

    # Add user as owner
    membership = BusinessMembership(
        user_id=demo_user.id,
        business_id=demo_business.id,
        role=MembershipRole.OWNER
    )
    db.add(membership)
    db.flush()

    # Create categories
    categories = [
        Category(name="Electronics", description="Electronic devices and accessories"),
        Category(name="Office Supplies", description="Office and desk supplies"),
        Category(name="Software", description="Software licenses and subscriptions"),
        Category(name="Accessories", description="Computer accessories and peripherals")
    ]
    for cat in categories:
        db.add(cat)
    db.flush()

    # Create suppliers
    suppliers = [
        Supplier(name="TechSupply Co", contact_person="John Smith", email="john@techsupply.com", phone="555-0101"),
        Supplier(name="OfficeWorld", contact_person="Jane Doe", email="jane@officeworld.com", phone="555-0102"),
        Supplier(name="SoftServe Inc", contact_person="Bob Johnson", email="bob@softserve.com", phone="555-0103")
    ]
    for sup in suppliers:
        db.add(sup)
    db.flush()

    # Create products
    product_names = [
        ("Laptop Pro 15", 1200.00, 900.00, categories[0].id, suppliers[0].id),
        ("Wireless Mouse", 25.00, 15.00, categories[3].id, suppliers[0].id),
        ("Mechanical Keyboard", 150.00, 100.00, categories[3].id, suppliers[0].id),
        ("Monitor 27\"", 350.00, 250.00, categories[0].id, suppliers[0].id),
        ("Office Chair", 200.00, 140.00, categories[1].id, suppliers[1].id),
        ("Standing Desk", 500.00, 350.00, categories[1].id, suppliers[1].id),
        ("Antivirus License", 50.00, 30.00, categories[2].id, suppliers[2].id),
        ("Cloud Storage 1TB", 100.00, 60.00, categories[2].id, suppliers[2].id),
        ("USB-C Hub", 40.00, 25.00, categories[3].id, suppliers[0].id),
        ("Webcam HD", 80.00, 50.00, categories[0].id, suppliers[0].id),
        ("Printer Paper Box", 30.00, 20.00, categories[1].id, suppliers[1].id),
        ("Ink Cartridge Set", 60.00, 40.00, categories[1].id, suppliers[1].id)
    ]

    products = []
    for i, (name, price, cost, cat_id, sup_id) in enumerate(product_names):
        product = Product(
            business_id=demo_business.id,
            name=name,
            sku=f"SKU-{1000 + i}",
            category_id=cat_id,
            supplier_id=sup_id,
            selling_price=Decimal(str(price)),
            cost_price=Decimal(str(cost)),
            stock_quantity=randint(5, 100),
            low_stock_threshold=10
        )
        db.add(product)
        products.append(product)
    db.flush()

    # Create customers
    first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry", "Ivy", "Jack"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

    customers = []
    for i in range(30):
        customer = Customer(
            business_id=demo_business.id,
            name=f"{choice(first_names)} {choice(last_names)}",
            email=f"customer{i+1}@example.com",
            phone=f"555-{randint(1000, 9999)}",
            address=f"{randint(100, 999)} Main St, City, State",
            segment=choice(["loyal", "high-value", "new", "at-risk", None]),
            churn_risk=choice(["low", "medium", "high", None]),
            churn_probability=Decimal(str(round(uniform(0.1, 0.9), 4))) if choice([True, False]) else None
        )
        db.add(customer)
        customers.append(customer)
    db.flush()

    # Create sales for the last 90 days
    today = datetime.utcnow()
    sales = []

    for day in range(90):
        sale_date = today - timedelta(days=day)
        num_sales = randint(2, 10)

        for _ in range(num_sales):
            invoice_num = f"INV-{sale_date.strftime('%Y%m%d')}-{randint(1000, 9999)}"

            # Select random products
            num_items = randint(1, 4)
            selected_products = choice(products, k=min(num_items, len(products)))

            total_amount = Decimal('0')
            total_cost = Decimal('0')
            items_data = []

            for prod in selected_products:
                quantity = randint(1, 5)
                unit_price = prod.selling_price
                unit_cost = prod.cost_price
                item_total = unit_price * quantity
                item_cost = unit_cost * quantity
                total_amount += item_total
                total_cost += item_cost
                items_data.append((prod, quantity, unit_price, unit_cost, item_total, item_cost))

            total_profit = total_amount - total_cost

            sale = Sale(
                business_id=demo_business.id,
                invoice_number=invoice_num,
                sale_date=sale_date,
                customer_id=choice(customers).id if choice([True, False]) else None,
                total_amount=total_amount,
                total_cost=total_cost,
                total_profit=total_profit,
                status="completed",
                payment_method=choice(["credit_card", "cash", "bank_transfer"]),
                region=choice(["North", "South", "East", "West", None])
            )
            db.add(sale)
            db.flush()

            # Create sale items
            for prod, quantity, unit_price, unit_cost, item_total, item_cost in items_data:
                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=prod.id,
                    customer_id=sale.customer_id,
                    quantity=quantity,
                    unit_price=unit_price,
                    unit_cost=unit_cost,
                    total_price=item_total,
                    total_cost=item_cost,
                    total_profit=item_total - item_cost
                )
                db.add(sale_item)

            sales.append(sale)

    db.flush()

    # Create expenses
    expense_categories = ["rent", "utilities", "salaries", "marketing", "supplies", "travel", "equipment", "software"]
    for month in range(6):
        expense_date = today - timedelta(days=month * 30)
        for _ in range(randint(3, 8)):
            expense = Expense(
                business_id=demo_business.id,
                amount=Decimal(str(round(uniform(100, 5000), 2))),
                category=choice(expense_categories),
                description=f"Monthly {choice(expense_categories)} expense",
                expense_date=expense_date,
                payment_method=choice(["bank_transfer", "credit_card"]),
                vendor=choice(["Vendor A", "Vendor B", "Vendor C"]),
                receipt_number=f"REC-{randint(10000, 99999)}"
            )
            db.add(expense)

    # Create marketing campaigns
    campaigns = [
        MarketingCampaign(
            business_id=demo_business.id,
            name="Summer Sale Campaign",
            description="Summer promotional campaign",
            start_date=today - timedelta(days=60),
            end_date=today - timedelta(days=30),
            budget=Decimal("5000.00"),
            actual_cost=Decimal("4500.00"),
            status="completed",
            campaign_type="email",
            target_audience="Existing customers"
        ),
        MarketingCampaign(
            business_id=demo_business.id,
            name="Q4 Launch",
            description="Product launch campaign for Q4",
            start_date=today - timedelta(days=20),
            end_date=today + timedelta(days=40),
            budget=Decimal("10000.00"),
            status="active",
            campaign_type="social_media",
            target_audience="New customers"
        )
    ]
    for campaign in campaigns:
        db.add(campaign)

    db.commit()

    print(f"Demo data generated successfully!")
    print(f"Demo user: demo@example.com / demo123")
    print(f"Business: {demo_business.name}")
    print(f"Products: {len(products)}")
    print(f"Customers: {len(customers)}")
    print(f"Sales: {len(sales)}")

    db.close()


if __name__ == "__main__":
    # Create tables
    Base.metadata.create_all(bind=engine)
    generate_demo_data()
