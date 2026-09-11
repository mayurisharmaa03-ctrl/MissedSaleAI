"""
Tests for CRM Opportunity Transitions and Email Service Integration.
"""

from services.crm_service import CRMService
from services.email_service import EmailService
from models import db, Customer, Product, RecoveryOpportunity, CommunicationLog, Sale

def test_crm_opportunity_transitions(app):
    with app.app_context():
        customer = Customer.query.first()
        product = Product.query.first()
        
        # Create opportunity
        opp = RecoveryOpportunity(
            customer_id=customer.id,
            product_id=product.id,
            recovery_probability=0.75,
            priority="HIGH",
            recommended_action="SEND_PERSONALIZED_EMAIL",
            status="ACTION_REQUIRED"
        )
        db.session.add(opp)
        db.session.commit()
        
        # Transition to EMAIL_SENT
        updated = CRMService.transition_opportunity_status(opp.id, "EMAIL_SENT")
        assert updated.status == "EMAIL_SENT"
        
        # Transition to RECOVERED with amount
        recovered = CRMService.transition_opportunity_status(opp.id, "RECOVERED", recovered_amount=199.99)
        assert recovered.status == "RECOVERED"
        assert recovered.recovered_amount == 199.99
        assert recovered.recovered_at is not None

def test_email_service_demo_mode(app):
    with app.app_context():
        customer = Customer.query.first()
        email_svc = EmailService(api_key="", demo_mode=True)
        
        result = email_svc.send_recovery_email(
            to_email=customer.email,
            customer_name=customer.name,
            subject="Special offer on your cart",
            body_text="Hi Alice,\n\nWe saved your items. Complete checkout now.",
            customer_id=customer.id
        )
        
        # Section 25: Never show success in demo mode
        assert result["success"] is False
        assert result["status"] == "DEMO_UNSENT"
        assert "DEMO MODE" in result["message"]
        
        # Verify log entry in database
        log = CommunicationLog.query.filter_by(customer_id=customer.id).first()
        assert log is not None
        assert log.status == "DEMO_UNSENT"
        assert "Alice" in log.body

def test_email_service_opt_out_enforcement(app):
    with app.app_context():
        customer = Customer.query.first()
        customer.email_opt_out = True
        db.session.commit()
        
        email_svc = EmailService(api_key="re_test_key_12345", demo_mode=False)
        res = email_svc.send_recovery_email(
            to_email=customer.email,
            customer_name=customer.name,
            subject="Special offer",
            body_text="Hi Alice",
            customer_id=customer.id
        )
        assert res["success"] is False
        assert res["status"] == "SUPPRESSED_OPT_OUT"
        assert "opted out" in res["message"]

def test_email_service_test_email_and_webhook(app):
    with app.app_context():
        email_svc = EmailService(api_key="", demo_mode=True)
        
        # Test admin test email in demo mode
        test_res = email_svc.send_test_email("admin@test.com")
        assert test_res["success"] is False
        assert test_res["status"] == "DEMO_UNSENT"
        
        # Test webhook processing
        # Pre-create communication log
        log = CommunicationLog(
            recipient="alice@test.com",
            channel="EMAIL",
            status="SENT",
            subject="Welcome",
            resend_id="test_msg_123"
        )
        db.session.add(log)
        db.session.commit()
        
        webhook_payload = {
            "type": "email.delivered",
            "data": {
                "email_id": "test_msg_123",
                "to": ["alice@test.com"]
            }
        }
        wb_res = email_svc.process_resend_webhook(webhook_payload)
        assert wb_res["event"] == "email.delivered"
        assert log.status == "DELIVERED"
