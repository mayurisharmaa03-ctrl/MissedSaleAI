"""
Email Campaigns and Communication Logging models.
"""

from datetime import datetime, timezone
from models import db

class Campaign(db.Model):
    __tablename__ = "campaigns"
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False, index=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey("recovery_opportunities.id"), nullable=True, index=True)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="SENT")  # QUEUED, SENT, OPENED, CLICKED, RECOVERED, DEMO_SIMULATED
    sent_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    customer = db.relationship("Customer", backref="campaigns")
    
    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "customer_name": self.customer.name if self.customer else "Unknown",
            "customer_email": self.customer.email if self.customer else "",
            "opportunity_id": self.opportunity_id,
            "subject": self.subject,
            "message": self.message,
            "status": self.status,
            "sent_at": self.sent_at.strftime("%Y-%m-%d %H:%M") if self.sent_at else None
        }

class CommunicationLog(db.Model):
    __tablename__ = "communication_logs"
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=True, index=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey("recovery_opportunities.id"), nullable=True, index=True)
    channel = db.Column(db.String(30), default="EMAIL")  # EMAIL, RESEND, CRM_NOTE
    recipient = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(30), default="SENT")  # SENT, FAILED, DELIVERED, OPENED, CLICKED, BOUNCED, DEMO_UNSENT
    subject = db.Column(db.String(255), nullable=True)
    body = db.Column(db.Text, nullable=True)
    provider = db.Column(db.String(50), default="Resend")
    resend_id = db.Column(db.String(100), nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    sent_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    customer = db.relationship("Customer", backref="communication_logs")
    opportunity = db.relationship("RecoveryOpportunity", backref="communication_logs")
    
    def __init__(self, **kwargs):
        # Support aliases gracefully
        if "recipient_email" in kwargs and "recipient" not in kwargs:
            kwargs["recipient"] = kwargs.pop("recipient_email")
        if "message" in kwargs and "body" not in kwargs:
            kwargs["body"] = kwargs.pop("message")
        if "provider_message_id" in kwargs and "resend_id" not in kwargs:
            kwargs["resend_id"] = kwargs.pop("provider_message_id")
        super().__init__(**kwargs)

    @property
    def email(self):
        return self.recipient

    @property
    def recipient_email(self):
        return self.recipient
        
    @recipient_email.setter
    def recipient_email(self, val):
        self.recipient = val

    @property
    def message(self):
        return self.body

    @message.setter
    def message(self, val):
        self.body = val
        
    @property
    def provider_message_id(self):
        return self.resend_id

    @provider_message_id.setter
    def provider_message_id(self, val):
        self.resend_id = val
    
    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "customer_name": self.customer.name if self.customer else "Guest / Test Recipient",
            "opportunity_id": self.opportunity_id,
            "channel": self.channel,
            "recipient": self.recipient,
            "recipient_email": self.recipient,
            "email": self.recipient,
            "provider": self.provider or "Resend",
            "provider_message_id": self.resend_id,
            "resend_id": self.resend_id,
            "status": self.status,
            "subject": self.subject,
            "body": self.body,
            "message": self.body,
            "error_message": self.error_message,
            "sent_at": self.sent_at.strftime("%Y-%m-%d %H:%M:%S") if self.sent_at else None,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }
