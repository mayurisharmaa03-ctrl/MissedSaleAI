"""
Lost Sale and Recovery Opportunity models for CRM & Sales Recovery pipeline.
"""

from datetime import datetime, timezone
from models import db

class LostSale(db.Model):
    __tablename__ = "lost_sales"
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True, index=True)
    lost_probability = db.Column(db.Float, nullable=False, default=0.75)
    detected_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    status = db.Column(db.String(30), nullable=False, default="DETECTED")  # DETECTED, IN_RECOVERY, RECOVERED, EXPIRED, IGNORED
    
    product = db.relationship("Product", foreign_keys=[product_id])
    opportunities = db.relationship("RecoveryOpportunity", backref="lost_sale", lazy="dynamic")
    
    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "customer_name": self.customer.name if self.customer else "Unknown",
            "customer_email": self.customer.email if self.customer else "",
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else "Abandoned Cart",
            "lost_probability": round(self.lost_probability, 3),
            "detected_at": self.detected_at.strftime("%Y-%m-%d %H:%M") if self.detected_at else None,
            "status": self.status
        }

class RecoveryOpportunity(db.Model):
    __tablename__ = "recovery_opportunities"
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True, index=True)
    lost_sale_id = db.Column(db.Integer, db.ForeignKey("lost_sales.id"), nullable=True, index=True)
    
    recovery_probability = db.Column(db.Float, nullable=False, default=0.50)
    priority = db.Column(db.String(20), nullable=False, default="MEDIUM")  # HIGH, MEDIUM, LOW
    recommended_action = db.Column(db.String(50), nullable=False, default="CRM_FOLLOW_UP")  # SEND_PERSONALIZED_EMAIL, CRM_FOLLOW_UP, MONITOR, IGNORE
    reasoning = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), nullable=False, default="NEW")
    # Statuses: NEW, ANALYZING, ACTION_REQUIRED, EMAIL_SENT, FOLLOW_UP, RECOVERED, CLOSED, IGNORED
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    recovered_at = db.Column(db.DateTime, nullable=True)
    recovered_amount = db.Column(db.Float, default=0.0)
    
    product = db.relationship("Product", foreign_keys=[product_id])
    decisions = db.relationship("AgentDecision", backref="opportunity", lazy="dynamic", cascade="all, delete-orphan")
    actions = db.relationship("AgentAction", backref="opportunity", lazy="dynamic", cascade="all, delete-orphan")
    campaigns = db.relationship("Campaign", backref="opportunity", lazy="dynamic", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "customer_name": self.customer.name if self.customer else "Unknown",
            "customer_email": self.customer.email if self.customer else "",
            "customer_value": self.customer.customer_value if self.customer else "Medium",
            "product_id": self.product_id,
            "product_name": self.product.name if self.product else "Abandoned Items",
            "product_price": round(self.product.price, 2) if self.product else 120.0,
            "recovery_probability": round(self.recovery_probability, 3),
            "priority": self.priority,
            "recommended_action": self.recommended_action,
            "reasoning": self.reasoning,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None,
            "recovered_at": self.recovered_at.strftime("%Y-%m-%d %H:%M") if self.recovered_at else None,
            "recovered_amount": round(self.recovered_amount, 2)
        }
