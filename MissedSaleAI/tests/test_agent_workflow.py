"""
Tests for Master Autonomous Agent Loop (OBSERVE -> ANALYZE -> REASON -> DECIDE -> ACT -> MONITOR -> ADAPT).
"""

from agent.agent import SalesRecoveryAgent
from models import Customer, RecoveryOpportunity, AgentAction, CommunicationLog

def test_full_autonomous_agent_cycle(app):
    with app.app_context():
        customer = Customer.query.filter_by(email="alice@test.com").first()
        agent = SalesRecoveryAgent()
        
        result = agent.run_for_customer(customer.id)
        
        # Verify execution response
        assert result["success"] is True
        assert result["customer_id"] == customer.id
        assert result["priority"] in ("HIGH", "MEDIUM", "LOW")
        assert len(result["reasoning"]) > 10
        
        # Verify 7-step trace
        trace = result["trace"]
        assert len(trace) >= 7
        step_names = [t["step"] for t in trace]
        assert "OBSERVE" in step_names
        assert "ANALYZE" in step_names
        assert "REASON" in step_names
        assert "DECIDE" in step_names
        assert "ACT" in step_names
        assert "MONITOR" in step_names
        assert "ADAPT" in step_names
        
        # Verify persistent memory was updated
        actions = AgentAction.query.filter_by(customer_id=customer.id).all()
        assert len(actions) >= 1
        
        # Verify CRM Opportunity was generated
        opp = RecoveryOpportunity.query.filter_by(customer_id=customer.id).first()
        assert opp is not None
        assert opp.status in ("ACTION_REQUIRED", "EMAIL_SENT", "ANALYZING", "RECOVERED")
