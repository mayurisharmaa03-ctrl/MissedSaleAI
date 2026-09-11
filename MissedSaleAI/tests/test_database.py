"""
Tests for Database Connection, Customer CRUD, and Sales CRUD.
"""

from models import db, Customer, Product, Sale, CustomerBehavior

def test_database_connection_and_customer_crud(app):
    with app.app_context():
        # Create
        new_cust = Customer(name="Bob Smith", email="bob@smith.com", customer_value="Medium")
        db.session.add(new_cust)
        db.session.commit()
        assert new_cust.id is not None
        
        # Read
        retrieved = Customer.query.filter_by(email="bob@smith.com").first()
        assert retrieved is not None
        assert retrieved.name == "Bob Smith"
        assert retrieved.customer_value == "Medium"
        
        # Update
        retrieved.customer_value = "High"
        db.session.commit()
        updated = Customer.query.get(retrieved.id)
        assert updated.customer_value == "High"
        
        # Delete
        db.session.delete(updated)
        db.session.commit()
        assert Customer.query.filter_by(email="bob@smith.com").first() is None

def test_sales_crud_and_lifetime_revenue(app):
    with app.app_context():
        customer = Customer.query.filter_by(email="alice@test.com").first()
        product = Product.query.first()
        
        # Initial purchase check from fixture
        assert customer.total_purchases() == 1
        assert customer.lifetime_revenue() == 199.99
        
        # Add another sale
        sale2 = Sale(customer_id=customer.id, product_id=product.id, amount=300.00, status="COMPLETED")
        db.session.add(sale2)
        db.session.commit()
        
        assert customer.total_purchases() == 2
        assert round(customer.lifetime_revenue(), 2) == 499.99
