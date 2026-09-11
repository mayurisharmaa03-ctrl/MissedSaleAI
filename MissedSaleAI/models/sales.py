"""
Sales and Customer Behavior tracking models.
"""

from datetime import datetime, timezone
from models import db

class Sale(db.Model):
    __tablename__ = "sales"
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="COMPLETED")  # COMPLETED, PENDING, CANCELLED, RECOVERED
    sale_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "customer_name": self.customer.name if self.customer else "Unknown",
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else "Unknown",
            "amount": round(self.amount, 2),
            "status": self.status,
            "sale_date": self.sale_date.strftime("%Y-%m-%d %H:%M") if self.sale_date else None
        }

class CustomerBehavior(db.Model):
    __tablename__ = "customer_behavior"
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True, index=True)
    page_views = db.Column(db.Integer, default=1)
    product_views = db.Column(db.Integer, default=1)
    cart_added = db.Column(db.Integer, default=0)
    checkout_started = db.Column(db.Boolean, default=False)
    purchased = db.Column(db.Boolean, default=False)
    session_duration = db.Column(db.Float, default=60.0)  # in seconds
    last_activity = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "customer_name": self.customer.name if self.customer else None,
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else "Various Items",
            "page_views": self.page_views,
            "product_views": self.product_views,
            "cart_added": self.cart_added,
            "checkout_started": self.checkout_started,
            "purchased": self.purchased,
            "session_duration": round(self.session_duration, 1),
            "last_activity": self.last_activity.strftime("%Y-%m-%d %H:%M") if self.last_activity else None
        }
