"""
Tests for Agent Decision Engine and Transparent Reasoning.
"""

from agent.decision_engine import DecisionEngine
from models import Customer, Product, CustomerBehavior

def test_decision_engine_high_priority(app):
    with app.app_context():
        engine = DecisionEngine(lost_threshold=0.60, recov_high=0.70, recov_med=0.40)
        customer = Customer.query.filter_by(email="alice@test.com").first()
        behavior = CustomerBehavior.query.filter_by(customer_id=customer.id).first()
        product = Product.query.first()
        
        eval_result = engine.evaluate(
            customer=customer,
            behavior=behavior,
            product=product,
            lost_prob=0.85,
            recovery_prob=0.82,
            fatigue_reached=False
        )
        
        assert eval_result["is_opportunity"] is True
        assert eval_result["priority"] == "HIGH"
        assert eval_result["recommended_action"] == "SEND_PERSONALIZED_EMAIL"
        assert eval_result["should_send_email"] is True
        assert "Customer initiated checkout" in eval_result["reasoning"]
        assert "HIGH PRIORITY" in eval_result["reasoning"]

def test_decision_engine_fatigue_limit(app):
    with app.app_context():
        engine = DecisionEngine()
        customer = Customer.query.filter_by(email="alice@test.com").first()
        behavior = CustomerBehavior.query.filter_by(customer_id=customer.id).first()
        product = Product.query.first()
        
        # Customer already reached 2 previous outreach attempts
        eval_result = engine.evaluate(
            customer=customer,
            behavior=behavior,
            product=product,
            lost_prob=0.85,
            recovery_prob=0.82,
            fatigue_reached=True,
            prior_attempts=2
        )
        
        assert eval_result["recommended_action"] == "HALT_FATIGUE"
        assert eval_result["should_send_email"] is False
        assert "fatigue limit reached" in eval_result["reasoning"]
