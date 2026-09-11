"""
Agent Action, Decision, and ML Model Prediction persistent memory models.
Enables transparent agent memory, auditable decision traces, and outcome loops.
"""

from datetime import datetime, timezone
import json
from models import db

class AgentAction(db.Model):
    __tablename__ = "agent_actions"
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False, index=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey("recovery_opportunities.id"), nullable=True, index=True)
    action_type = db.Column(db.String(60), nullable=False)
    # Action types: OBSERVE_BEHAVIOR, PREDICT_LOST_SALE, PREDICT_RECOVERY, CREATE_OPPORTUNITY, 
    #               SEND_RECOVERY_EMAIL, SCHEDULE_FOLLOW_UP, UPDATE_STATUS, DETECT_RECOVERY, HALT_FATIGUE
    reasoning = db.Column(db.Text, nullable=False)
    result = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "customer_name": self.customer.name if self.customer else f"Customer #{self.customer_id}",
            "opportunity_id": self.opportunity_id,
            "action_type": self.action_type,
            "reasoning": self.reasoning,
            "result": self.result,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "time_ago": self.created_at.strftime("%I:%M %p") if self.created_at else None
        }

class AgentDecision(db.Model):
    __tablename__ = "agent_decisions"
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False, index=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey("recovery_opportunities.id"), nullable=True, index=True)
    decision = db.Column(db.String(60), nullable=True)  # e.g., HIGH_PRIORITY_EMAIL, CRM_FOLLOW_UP, MONITOR
    reasoning = db.Column(db.Text, nullable=True)
    rationale = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float, default=0.85)
    priority = db.Column(db.String(20), nullable=False, default="MEDIUM")
    recommended_action = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    customer = db.relationship("Customer", backref="decisions")
    
    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "customer_name": self.customer.name if self.customer else f"Customer #{self.customer_id}",
            "opportunity_id": self.opportunity_id,
            "decision": self.decision or self.recommended_action,
            "reasoning": self.reasoning or self.rationale,
            "rationale": self.rationale,
            "confidence": round(self.confidence, 3),
            "priority": self.priority,
            "recommended_action": self.recommended_action,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }

class ModelPrediction(db.Model):
    __tablename__ = "model_predictions"
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False, index=True)
    lost_probability = db.Column(db.Float, nullable=False)
    recovery_probability = db.Column(db.Float, nullable=False)
    model_name = db.Column(db.String(60), default="Random Forest Champion")
    baseline_probability = db.Column(db.Float, nullable=True)
    features_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    customer = db.relationship("Customer", backref="predictions")
    
    @property
    def lost_sale_probability(self):
        return self.lost_probability
        
    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "customer_name": self.customer.name if self.customer else f"Customer #{self.customer_id}",
            "model_name": self.model_name,
            "lost_sale_probability": round(self.lost_probability, 3),
            "lost_probability": round(self.lost_probability, 3),
            "recovery_probability": round(self.recovery_probability, 3),
            "baseline_probability": round(self.baseline_probability, 3) if self.baseline_probability is not None else None,
            "features": json.loads(self.features_json) if self.features_json else {},
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }
