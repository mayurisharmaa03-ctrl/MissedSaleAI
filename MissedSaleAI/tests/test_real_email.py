"""
Comprehensive Automated Tests for Real Resend Email Delivery (Section 24).
Tests:
1. Email Validation (valid, invalid, empty)
2. Email Service (successful Resend response, failed Resend response, missing API key)
3. CRM Integration (communication log creation, status update, provider message ID storage)
4. Agent Decisions (decides to send, decides not to send, opt-out suppression, rate limiting)
"""

from unittest.mock import patch, MagicMock
from services.email_service import EmailService
from models import db, Customer, Product, RecoveryOpportunity, CommunicationLog, CustomerBehavior
from agent.agent import SalesRecoveryAgent
from agent.decision_engine import DecisionEngine

# =====================================================================
# 1. EMAIL VALIDATION TESTS
# =====================================================================

def test_email_validation_valid():
    svc = EmailService()
    valid_emails = [
        "friend@gmail.com",
        "rahul.sharma@example.co.in",
        "user_123+tag@domain.org",
        "customer@sub.domain.com"
    ]
    for email in valid_emails:
        is_valid, err = svc.validate_email(email)
        assert is_valid is True
        assert err is None

def test_email_validation_invalid():
    svc = EmailService()
    invalid_emails = [
        "not-an-email",
        "@missingusername.com",
        "missingatsign.com",
        "user@.com",
        "user@domain",
        "spaces in@email.com"
    ]
    for email in invalid_emails:
        is_valid, err = svc.validate_email(email)
        assert is_valid is False
        assert err is not None

def test_email_validation_empty():
    svc = EmailService()
    for empty_val in ["", "   ", None]:
        is_valid, err = svc.validate_email(empty_val)
        assert is_valid is False
        assert "cannot be empty" in err

# =====================================================================
# 2. EMAIL SERVICE DISPATCH TESTS (MOCKED RESEND RESPONSES)
# =====================================================================

def test_email_service_successful_resend_response(app):
    with app.app_context():
        customer = Customer.query.first()
        svc = EmailService(api_key="re_live_test_key_123456", demo_mode=False)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "re_live_msg_789456"}

        with patch("requests.post", return_value=mock_resp) as mock_post:
            res = svc.send_recovery_email(
                to_email=customer.email,
                customer_name=customer.name,
                subject="Complete your purchase",
                body_text="Hi Alice, we saved your item.",
                customer_id=customer.id
            )

            assert res["success"] is True
            assert res["status"] == "SENT"
            assert res["message_id"] == "re_live_msg_789456"
            assert res["provider"] == "Resend"
            assert "✓ Email sent successfully" in res["message"]

            # Verify Resend API request headers & payload
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            assert "Bearer re_live_test_key_123456" in kwargs["headers"]["Authorization"]
            assert kwargs["json"]["to"] == [customer.email]
            assert kwargs["json"]["subject"] == "Complete your purchase"

            # Verify communication log in DB
            log = CommunicationLog.query.filter_by(resend_id="re_live_msg_789456").first()
            assert log is not None
            assert log.status == "SENT"
            assert log.provider == "Resend"
            assert log.recipient == customer.email
            assert log.provider_message_id == "re_live_msg_789456"

def test_email_service_failed_resend_response(app):
    with app.app_context():
        customer = Customer.query.first()
        svc = EmailService(api_key="re_invalid_or_expired_key", demo_mode=False)

        mock_resp = MagicMock()
        mock_resp.status_code = 422
        mock_resp.json.return_value = {"message": "Domain is not verified for sending."}

        with patch("requests.post", return_value=mock_resp):
            res = svc.send_recovery_email(
                to_email=customer.email,
                customer_name=customer.name,
                subject="Complete your purchase",
                body_text="Hi Alice",
                customer_id=customer.id
            )

            # Section 9: Never show success on Resend failure
            assert res["success"] is False
            assert res["status"] == "FAILED"
            assert "Domain is not verified" in res["error"]
            assert "could not be sent" in res["message"]

            # Communication log stores failure safely
            log = CommunicationLog.query.filter_by(customer_id=customer.id, status="FAILED").first()
            assert log is not None
            assert "Domain is not verified" in log.error_message
            assert log.resend_id is None

def test_email_service_missing_api_key(app):
    with app.app_context():
        customer = Customer.query.first()
        # Empty API key
        svc = EmailService(api_key="", demo_mode=False)

        res = svc.send_recovery_email(
            to_email=customer.email,
            customer_name=customer.name,
            subject="Test",
            body_text="Test Body",
            customer_id=customer.id
        )

        # Section 25: Never show success in demo mode
        assert res["success"] is False
        assert res["status"] == "DEMO_UNSENT"
        assert res["mode"] == "DEMO_MODE"
        assert "RESEND_API_KEY is not configured" in res["message"]

# =====================================================================
# 3. CRM INTEGRATION & STATUS SYNCHRONIZATION TESTS
# =====================================================================

def test_crm_communication_log_and_status_update(app):
    with app.app_context():
        customer = Customer.query.first()
        product = Product.query.first()

        opp = RecoveryOpportunity(
            customer_id=customer.id,
            product_id=product.id,
            recovery_probability=0.88,
            priority="HIGH",
            recommended_action="SEND_PERSONALIZED_EMAIL",
            status="ACTION_REQUIRED"
        )
        db.session.add(opp)
        db.session.commit()

        svc = EmailService(api_key="re_valid_key_123", demo_mode=False)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "re_opp_sync_001"}

        with patch("requests.post", return_value=mock_resp):
            res = svc.send_recovery_email(
                to_email=customer.email,
                customer_name=customer.name,
                subject="Regarding your items",
                body_text="Hi Alice",
                customer_id=customer.id,
                opportunity_id=opp.id
            )

            assert res["success"] is True
            # Opportunity must update to EMAIL_SENT
            updated_opp = db.session.get(RecoveryOpportunity, opp.id)
            assert updated_opp.status == "EMAIL_SENT"

            # Check communication log entry
            log = CommunicationLog.query.filter_by(opportunity_id=opp.id).first()
            assert log is not None
            assert log.status == "SENT"
            assert log.provider_message_id == "re_opp_sync_001"

def test_crm_opportunity_transitions_to_failed_on_send_error(app):
    with app.app_context():
        customer = Customer.query.first()
        product = Product.query.first()

        opp = RecoveryOpportunity(
            customer_id=customer.id,
            product_id=product.id,
            recovery_probability=0.85,
            priority="HIGH",
            recommended_action="SEND_PERSONALIZED_EMAIL",
            status="ACTION_REQUIRED"
        )
        db.session.add(opp)
        db.session.commit()

        svc = EmailService(api_key="re_test_key", demo_mode=False)
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        mock_resp.json.side_effect = Exception("No JSON")

        with patch("requests.post", return_value=mock_resp):
            res = svc.send_recovery_email(
                to_email=customer.email,
                customer_name=customer.name,
                subject="Test",
                body_text="Test",
                customer_id=customer.id,
                opportunity_id=opp.id
            )

            assert res["success"] is False
            # Opportunity status must update to EMAIL_FAILED
            updated_opp = db.session.get(RecoveryOpportunity, opp.id)
            assert updated_opp.status == "EMAIL_FAILED"

# =====================================================================
# 4. AGENT DECISIONS & SAFETY RULES (OPT-OUT & RATE LIMITING)
# =====================================================================

def test_agent_decides_to_send_and_records_message_id(app):
    with app.app_context():
        customer = Customer.query.first()
        svc = EmailService(api_key="re_agent_key_456", demo_mode=False)
        agent = SalesRecoveryAgent(email_service=svc)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "re_agent_msg_999"}

        with patch("requests.post", return_value=mock_resp):
            trace_result = agent.run_for_customer(customer.id)

            assert trace_result.get("recommended_action") in ("SEND_PERSONALIZED_EMAIL", "OFFER_INCENTIVE", "URGENT_OUTREACH")
            # Verify memory and log recorded
            log = CommunicationLog.query.filter_by(resend_id="re_agent_msg_999").first()
            assert log is not None
            assert log.status == "SENT"

def test_agent_opt_out_suppression(app):
    with app.app_context():
        customer = Customer.query.first()
        customer.email_opt_out = True
        db.session.commit()

        svc = EmailService(api_key="re_test_key", demo_mode=False)
        res = svc.send_recovery_email(
            to_email=customer.email,
            customer_name=customer.name,
            subject="Special offer",
            body_text="Hi Alice",
            customer_id=customer.id
        )

        assert res["success"] is False
        assert res["status"] == "SUPPRESSED_OPT_OUT"
        assert "opted out" in res["message"]

def test_agent_rate_limiting_enforcement(app):
    with app.app_context():
        customer = Customer.query.first()
        customer.email_opt_out = False
        db.session.commit()

        svc = EmailService(api_key="re_test_key", demo_mode=False)
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "re_rate_msg_1"}

        with patch("requests.post", return_value=mock_resp):
            # Send first email
            res1 = svc.send_recovery_email(
                to_email=customer.email,
                customer_name=customer.name,
                subject="Notice 1",
                body_text="Body 1",
                customer_id=customer.id
            )
            assert res1["success"] is True

            # Attempt immediate second email (within 60 second interval limit)
            res2 = svc.send_recovery_email(
                to_email=customer.email,
                customer_name=customer.name,
                subject="Notice 2",
                body_text="Body 2",
                customer_id=customer.id
            )
            assert res2["success"] is False
            assert res2["status"] == "RATE_LIMITED"
            assert "Rate limit active" in res2["message"]
