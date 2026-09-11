"""
Pytest configuration and fixtures for MissedSale AI.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from app import create_app
from config import Config
from models import db, Customer, Product, Sale, CustomerBehavior, LostSale, RecoveryOpportunity, User

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    DEMO_EMAIL_MODE = True
    RESEND_API_KEY = ""
    LOST_SALE_THRESHOLD = 0.60
    RECOVERY_THRESHOLD_HIGH = 0.70
    RECOVERY_THRESHOLD_MED = 0.40
    MAX_OUTREACH_ATTEMPTS = 2

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        # Seed test product
        product = Product(name="Test ANC Headphones", category="Audio", price=199.99, stock=20)
        db.session.add(product)
        
        # Seed test customer
        customer = Customer(name="Alice Test", email="alice@test.com", phone="+1-555-9999", customer_value="High")
        db.session.add(customer)
        db.session.commit()
        
        # Seed test behavior
        behavior = CustomerBehavior(
            customer_id=customer.id,
            product_id=product.id,
            page_views=5,
            product_views=3,
            cart_added=2,
            checkout_started=True,
            purchased=False,
            session_duration=240.0
        )
        db.session.add(behavior)
        
        # Seed test past completed sale
        sale = Sale(
            customer_id=customer.id,
            product_id=product.id,
            amount=199.99,
            status="COMPLETED"
        )
        db.session.add(sale)
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
