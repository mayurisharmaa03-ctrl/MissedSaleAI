"""
Customer model representing CRM leads and accounts.
"""

from datetime import datetime, timezone
from models import db

class Customer(db.Model):
    __tablename__ = "customers"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(30), nullable=True)
    customer_value = db.Column(db.String(20), default="Medium")  # Low, Medium, High
    email_opt_out = db.Column(db.Boolean, default=False, nullable=False)
    last_email_sent = db.Column(db.DateTime, nullable=True)
    email_count = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    sales = db.relationship("Sale", backref="customer", lazy="dynamic", cascade="all, delete-orphan")
    behaviors = db.relationship("CustomerBehavior", backref="customer", lazy="dynamic", cascade="all, delete-orphan")
    lost_sales = db.relationship("LostSale", backref="customer", lazy="dynamic", cascade="all, delete-orphan")
    opportunities = db.relationship("RecoveryOpportunity", backref="customer", lazy="dynamic", cascade="all, delete-orphan")
    agent_actions = db.relationship("AgentAction", backref="customer", lazy="dynamic", cascade="all, delete-orphan")
    
    def total_purchases(self):
        completed = self.sales.filter_by(status="COMPLETED").all()
        return len(completed)
        
    def lifetime_revenue(self):
        completed = self.sales.filter_by(status="COMPLETED").all()
        return sum(s.amount for s in completed)

    def emails_sent_today(self):
        """Calculates emails sent to this customer in the past 24 hours."""
        from models.campaign import CommunicationLog
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=1)
        return CommunicationLog.query.filter(
            CommunicationLog.customer_id == self.id,
            CommunicationLog.sent_at >= cutoff,
            CommunicationLog.status.in_(["SENT", "DELIVERED", "OPENED", "CLICKED"])
        ).count()

    def seconds_since_last_email(self):
        """Returns seconds elapsed since last sent email, or None if never sent."""
        if not self.last_email_sent:
            return None
        last_dt = self.last_email_sent
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=timezone.utc)
        now_dt = datetime.now(timezone.utc)
        return max(0, int((now_dt - last_dt).total_seconds()))

    def check_rate_limit(self, max_per_day=3, min_interval_seconds=60):
        """
        Validates if customer is allowed to receive a recovery email.
        Returns (allowed: bool, reason: str).
        """
        if self.email_opt_out:
            return False, f"Customer {self.email} has opted out of marketing communications."

        sent_today = self.emails_sent_today()
        if sent_today >= max_per_day:
            return False, f"Rate limit reached: Customer has already received {sent_today} emails today (max {max_per_day}/day)."

        sec_since = self.seconds_since_last_email()
        if sec_since is not None and sec_since < min_interval_seconds:
            wait_time = min_interval_seconds - sec_since
            return False, f"Rate limit active: Please wait {wait_time}s before sending another email to this customer."

        return True, "OK"
        
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "customer_value": self.customer_value,
            "email_opt_out": self.email_opt_out,
            "last_email_sent": self.last_email_sent.strftime("%Y-%m-%d %H:%M") if self.last_email_sent else None,
            "email_count": self.email_count,
            "total_purchases": self.total_purchases(),
            "lifetime_revenue": round(self.lifetime_revenue(), 2),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M") if self.created_at else None
        }
