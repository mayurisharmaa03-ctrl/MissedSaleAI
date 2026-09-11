"""
Agent Memory Subsystem.
Provides episodic and long-term memory for the Sales Recovery Agent:
- Prior communication fatigue tracking
- Action history retrieval
- Recovery outcome learning
- Decision recording
"""

from datetime import datetime, timezone
import json
from models import db, Customer, Sale, CustomerBehavior, LostSale, RecoveryOpportunity, AgentAction, AgentDecision, ModelPrediction, CommunicationLog

class AgentMemory:
    def __init__(self):
        pass
        
    def get_customer_history(self, customer_id):
        """Retrieve full customer history: purchases, behavior, and previous attempts."""
        customer = Customer.query.get(customer_id)
        if not customer:
            return None
            
        sales = Sale.query.filter_by(customer_id=customer_id).order_by(Sale.sale_date.desc()).all()
        behaviors = CustomerBehavior.query.filter_by(customer_id=customer_id).order_by(CustomerBehavior.last_activity.desc()).all()
        prior_actions = AgentAction.query.filter_by(customer_id=customer_id).order_by(AgentAction.created_at.desc()).limit(10).all()
        prior_comms = CommunicationLog.query.filter_by(customer_id=customer_id).order_by(CommunicationLog.sent_at.desc()).all()
        active_opportunities = RecoveryOpportunity.query.filter_by(customer_id=customer_id).all()
        
        return {
            "customer": customer,
            "sales_count": len(sales),
            "completed_purchases": [s for s in sales if s.status == "COMPLETED"],
            "total_spent": sum(s.amount for s in sales if s.status == "COMPLETED"),
            "latest_behavior": behaviors[0] if behaviors else None,
            "all_behaviors": behaviors,
            "prior_actions": prior_actions,
            "emails_sent_count": len(prior_comms),
            "prior_communications": prior_comms,
            "active_opportunities": active_opportunities
        }

    def check_fatigue_limit(self, customer_id, max_attempts=2):
        """
        Check if customer has received too many recovery attempts recently.
        Prevents customer spamming/annoyance.
        """
        recent_emails = CommunicationLog.query.filter_by(
            customer_id=customer_id,
            status="SENT"
        ).count()
        
        demo_emails = CommunicationLog.query.filter_by(
            customer_id=customer_id,
            status="DEMO_SIMULATED"
        ).count()
        
        total_outreach = recent_emails + demo_emails
        return total_outreach >= max_attempts, total_outreach

    def record_action(self, customer_id, action_type, reasoning, result=None, opportunity_id=None):
        """Store atomic agent action in persistent memory."""
        action = AgentAction(
            customer_id=customer_id,
            opportunity_id=opportunity_id,
            action_type=action_type,
            reasoning=reasoning,
            result=result,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(action)
        db.session.commit()
        return action

    def record_decision(self, customer_id, rationale, priority, recommended_action, opportunity_id=None):
        """Record transparent reasoning behind an agent decision."""
        decision = AgentDecision(
            customer_id=customer_id,
            opportunity_id=opportunity_id,
            rationale=rationale,
            priority=priority,
            recommended_action=recommended_action,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(decision)
        db.session.commit()
        return decision

    def record_prediction(self, customer_id, lost_prob, recovery_prob, baseline_prob=None, features=None):
        """Record ML model outputs."""
        pred = ModelPrediction(
            customer_id=customer_id,
            lost_probability=lost_prob,
            recovery_probability=recovery_prob,
            baseline_probability=baseline_prob,
            features_json=json.dumps(features) if features else None,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(pred)
        db.session.commit()
        return pred

    def get_recent_actions(self, limit=50):
        """Fetch chronological timeline for Agent Activity page."""
        return AgentAction.query.order_by(AgentAction.created_at.desc()).limit(limit).all()
