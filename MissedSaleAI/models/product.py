"""
Product model representing inventory items.
"""

from datetime import datetime, timezone
from models import db

class Product(db.Model):
    __tablename__ = "products"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(80), nullable=False, default="General")
    price = db.Column(db.Float, nullable=False, default=0.0)
    stock = db.Column(db.Integer, nullable=False, default=100)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    sales = db.relationship("Sale", backref="product", lazy="dynamic")
    behaviors = db.relationship("CustomerBehavior", backref="product", lazy="dynamic")
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price": round(self.price, 2),
            "stock": self.stock,
            "created_at": self.created_at.strftime("%Y-%m-%d") if self.created_at else None
        }
