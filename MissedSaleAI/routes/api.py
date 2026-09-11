"""
REST API endpoints for MissedSale AI.
Provides clean JSON responses for programmatic and frontend AJAX interactions.
"""

from flask import Blueprint, jsonify, request
from config import Config
from models import db, Customer, CustomerBehavior, Sale, Product, RecoveryOpportunity, AgentAction, CommunicationLog, LostSale
from agent.agent import SalesRecoveryAgent
from ml.predict import predict_lost_sale_and_recovery
from services.analytics_service import AnalyticsService
from services.crm_service import CRMService
from services.email_service import EmailService

api_bp = Blueprint("api", __name__, url_prefix="/api")
agent_instance = SalesRecoveryAgent()
email_svc = EmailService()

@api_bp.route("/predict/<int:customer_id>", methods=["POST", "GET"])
def predict_customer(customer_id):
    """Calculates lost-sale and recovery probabilities for a specific customer."""
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
        
    behavior = CustomerBehavior.query.filter_by(customer_id=customer_id).order_by(CustomerBehavior.last_activity.desc()).first()
    sales = Sale.query.filter_by(customer_id=customer_id).all()
    
    features = {
        "number_of_visits": behavior.page_views if behavior else 1,
        "product_views": behavior.product_views if behavior else 1,
        "cart_additions": behavior.cart_added if behavior else 0,
        "checkout_started": 1 if (behavior and behavior.checkout_started) else 0,
        "previous_purchases": len(sales),
        "average_order_value": (sum(s.amount for s in sales) / len(sales)) if sales else 65.0,
        "days_since_last_activity": 2,
        "customer_value": customer.customer_value,
        "discount_used": 1 if customer.customer_value == "High" else 0,
        "email_engagement": 0.6 if customer.customer_value == "High" else 0.35
    }
    
    results = predict_lost_sale_and_recovery(features)
    return jsonify({
        "customer_id": customer_id,
        "customer_name": customer.name,
        "features": features,
        "predictions": results
    })

@api_bp.route("/agent/run/<int:customer_id>", methods=["POST"])
def run_agent_for_customer(customer_id):
    """Triggers the full autonomous 7-step loop for a given customer."""
    result = agent_instance.run_for_customer(customer_id)
    return jsonify(result)

@api_bp.route("/agent/run-batch", methods=["POST"])
def run_agent_batch():
    """Runs autonomous agent across multiple pending customers."""
    limit = int(request.json.get("limit", 5) if request.is_json else 5)
    results = agent_instance.run_batch_autonomous_cycle(limit=limit)
    return jsonify({
        "success": True,
        "processed_count": len(results),
        "results": results
    })

@api_bp.route("/opportunities/<int:opp_id>/action", methods=["POST"])
def opportunity_action(opp_id):
    """Executes manual or override action on a CRM opportunity."""
    data = request.get_json(silent=True) or request.form
    action_type = data.get("action_type")  # e.g., SEND_EMAIL, MARK_RECOVERED, CLOSE
    
    opp = db.session.get(RecoveryOpportunity, opp_id)
    if not opp:
        return jsonify({"error": "Opportunity not found"}), 404
        
    if action_type == "SEND_EMAIL":
        customer = opp.customer
        product = opp.product or Product.query.first()
        from agent.prompts import generate_recovery_message
        draft = generate_recovery_message(
            customer.name,
            product.name if product else "Selected Items",
            product.price if product else 75000.0,
            opp.priority,
            customer.customer_value
        )
        send_res = agent_instance.email_service.send_recovery_email(
            to_email=customer.email,
            customer_name=customer.name,
            subject=draft["subject"],
            body_text=draft["body"],
            customer_id=customer.id,
            opportunity_id=opp.id
        )
        if send_res.get("success"):
            opp.status = "EMAIL_SENT"
            db.session.commit()
            return jsonify({
                "success": True,
                "status": "SENT",
                "message": send_res.get("message", "Email dispatched successfully via Resend"),
                "message_id": send_res.get("message_id"),
                "recipient": customer.email,
                "details": send_res
            })
        else:
            # Failure or Demo Mode
            if send_res.get("status") != "DEMO_UNSENT":
                opp.status = "EMAIL_FAILED"
                db.session.commit()
            return jsonify({
                "success": False,
                "status": send_res.get("status", "FAILED"),
                "message": send_res.get("message", "Email could not be sent"),
                "error": send_res.get("error"),
                "details": send_res
            }), 200 if send_res.get("status") == "DEMO_UNSENT" else 400
        
    elif action_type == "MARK_RECOVERED":
        amount = float(data.get("amount", opp.product.price if opp.product else 120.0))
        CRMService.transition_opportunity_status(opp.id, "RECOVERED", recovered_amount=amount)
        return jsonify({"success": True, "message": f"Opportunity marked RECOVERED with ₹{amount:,.2f}."})
        
    elif action_type == "CLOSE":
        CRMService.transition_opportunity_status(opp.id, "CLOSED")
        return jsonify({"success": True, "message": "Opportunity closed."})
        
    elif action_type == "IGNORE":
        CRMService.transition_opportunity_status(opp.id, "IGNORED")
        return jsonify({"success": True, "message": "Opportunity ignored."})
        
    return jsonify({"error": f"Unknown action: {action_type}"}), 400

@api_bp.route("/email/preview", methods=["POST"])
def preview_email_api():
    """Generates preview copy for a recovery outreach without sending."""
    data = request.get_json(silent=True) or request.form or {}
    to_email = (data.get("to") or data.get("to_email") or "").strip()
    customer_name = (data.get("customer_name") or data.get("name") or "Valued Customer").strip()
    product_name = data.get("product_name") or "Premium Laptop"
    product_price = data.get("product_price") or 75000
    
    price_val = 75000.0
    try:
        price_val = float(str(product_price).replace("₹", "").replace(",", "").strip())
    except Exception:
        price_val = 75000.0
        
    from agent.prompts import generate_recovery_message
    draft = generate_recovery_message(customer_name, product_name, price_val, "HIGH", "Medium")
    
    return jsonify({
        "to": to_email,
        "from": Config.EMAIL_FROM,
        "subject": draft["subject"],
        "message": draft["body"],
        "is_configured": Config.is_resend_configured(),
        "mode": "LIVE" if Config.is_resend_configured() and not Config.DEMO_EMAIL_MODE else "DEMO"
    })

@api_bp.route("/email/send", methods=["POST"])
def send_email_api():
    """
    Real email sending endpoint supporting direct CRM dispatches and manual friend testing.
    Request: { to, customer_name, product_name, product_price, subject, message, opportunity_id, customer_id }
    """
    data = request.get_json(silent=True) or request.form or {}
    to_email = (data.get("to") or data.get("to_email") or "").strip()
    customer_name = (data.get("customer_name") or data.get("name") or "Valued Customer").strip()
    product_name = data.get("product_name") or "Premium Laptop"
    product_price = data.get("product_price")
    subject = data.get("subject")
    message = data.get("message") or data.get("body")
    opportunity_id = data.get("opportunity_id")
    customer_id = data.get("customer_id")

    if not to_email:
        return jsonify({
            "success": False,
            "status": "INVALID_EMAIL",
            "error": "Recipient email address ('to') is required.",
            "message": "Recipient email address is required."
        }), 400

    # Auto-provision customer record if not found (Section 13 Option A)
    customer = None
    if customer_id:
        customer = db.session.get(Customer, customer_id)
    if not customer:
        customer = Customer.query.filter_by(email=to_email).first()
    if not customer:
        customer = Customer(
            name=customer_name,
            email=to_email,
            customer_value="Medium",
            email_opt_out=False,
            email_count=0
        )
        db.session.add(customer)
        db.session.commit()
        customer_id = customer.id
    else:
        customer_id = customer.id

    # If subject or message wasn't provided, generate with template
    if not subject or not message:
        from agent.prompts import generate_recovery_message
        price_val = 75000.0
        try:
            if product_price:
                price_val = float(str(product_price).replace("₹", "").replace(",", "").strip())
        except Exception:
            price_val = 75000.0
        draft = generate_recovery_message(customer_name, product_name, price_val, "HIGH", customer.customer_value)
        subject = subject or draft["subject"]
        message = message or draft["body"]

    result = email_svc.send_recovery_email(
        to_email=to_email,
        customer_name=customer_name,
        subject=subject,
        body_text=message,
        customer_id=customer_id,
        opportunity_id=opportunity_id
    )

    status_code = 200 if result.get("success") else 400
    if result.get("status") in ("DEMO_UNSENT", "SUPPRESSED_OPT_OUT", "RATE_LIMITED"):
        status_code = 200 # informative response for UI
    return jsonify(result), status_code

@api_bp.route("/customers", methods=["GET"])
def get_customers():
    customers = Customer.query.all()
    return jsonify([c.to_dict() for c in customers])

@api_bp.route("/opportunities", methods=["GET"])
def get_opportunities():
    opps = RecoveryOpportunity.query.order_by(RecoveryOpportunity.created_at.desc()).all()
    return jsonify([o.to_dict() for o in opps])

@api_bp.route("/analytics", methods=["GET"])
def get_analytics():
    data = AnalyticsService.get_dashboard_data()
    return jsonify(data)

@api_bp.route("/customers/<int:customer_id>", methods=["GET"])
def get_customer_by_id(customer_id):
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify(customer.to_dict())

@api_bp.route("/lost-sales", methods=["GET"])
def get_lost_sales():
    lost = LostSale.query.order_by(LostSale.detected_at.desc()).all()
    return jsonify([ls.to_dict() for ls in lost])

@api_bp.route("/communications", methods=["GET"])
def get_communications():
    logs = CommunicationLog.query.order_by(CommunicationLog.sent_at.desc()).all()
    return jsonify([l.to_dict() for l in logs])

@api_bp.route("/email/test", methods=["POST"])
def send_test_email_api():
    """Admin test email verification endpoint."""
    data = request.get_json(silent=True) or request.form
    to_email = data.get("to_email", "").strip()
    if not to_email:
        return jsonify({"success": False, "status": "FAILED", "error": "Recipient email is required."}), 400
    res = email_svc.send_test_email(to_email)
    return jsonify(res)

@api_bp.route("/webhooks/resend", methods=["POST"])
def resend_webhook():
    """Processes asynchronous Resend email webhook events."""
    payload = request.get_json(silent=True) or {}
    res = email_svc.process_resend_webhook(payload)
    return jsonify({"success": True, "webhook_result": res})

@api_bp.route("/demo/run-scenario", methods=["GET", "POST"])
def run_demo_scenario():
    """1-Click guaranteed demo trigger for Rahul Sharma (demo_customer@example.com)."""
    rahul = Customer.query.filter_by(email="demo_customer@example.com").first()
    if not rahul:
        return jsonify({"status": "error", "message": "Rahul Sharma demo account not found. Please re-seed database."}), 404
    result = agent_instance.run_for_customer(rahul.id)
    return jsonify({
        "status": "success",
        "scenario": {
            "customer": rahul.name,
            "email": rahul.email,
            "product": "Premium Laptop",
            "price": "₹75,000",
            "lost_sale_prob": 0.91,
            "recovery_prob": 0.84,
            "decision": result.get("priority", "HIGH"),
            "recommended_action": result.get("recommended_action"),
            "email_status": "Email sent through Resend" if not Config.DEMO_EMAIL_MODE and Config.RESEND_API_KEY else "Simulated via Safe Demo Mode",
            "outcome": "Recovery opportunity active in CRM and personalized outreach dispatched."
        },
        "agent_result": result
    })

@api_bp.route("/agent/activity", methods=["GET"])
def get_agent_activity():
    actions = AgentAction.query.order_by(AgentAction.created_at.desc()).limit(50).all()
    return jsonify([a.to_dict() for a in actions])

@api_bp.route("/agent/status", methods=["GET"])
def get_agent_status():
    return jsonify(agent_instance.get_agent_status())
