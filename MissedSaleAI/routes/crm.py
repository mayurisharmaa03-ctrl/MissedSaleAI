"""
Integrated CRM Module routes.
Provides routes for CRM pipeline, Leads, Product Catalog, Communications history, and Architecture diagrams.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from routes.auth import login_required
from services.crm_service import CRMService
from models import db, RecoveryOpportunity, Customer, Product, CommunicationLog, CustomerBehavior, LostSale

crm_bp = Blueprint("crm", __name__)

@crm_bp.route("/crm")
@login_required
def crm_view():
    all_opps = RecoveryOpportunity.query.order_by(RecoveryOpportunity.created_at.desc()).all()
    
    stages = {
        "NEW": [o for o in all_opps if o.status in ("NEW", "ANALYZING")],
        "ACTION_REQUIRED": [o for o in all_opps if o.status == "ACTION_REQUIRED"],
        "EMAIL_SENT": [o for o in all_opps if o.status == "EMAIL_SENT"],
        "FOLLOW_UP": [o for o in all_opps if o.status == "FOLLOW_UP"],
        "RECOVERED": [o for o in all_opps if o.status == "RECOVERED"],
        "CLOSED": [o for o in all_opps if o.status in ("CLOSED", "IGNORED")]
    }
    
    customers = Customer.query.order_by(Customer.name.asc()).all()
    
    return render_template(
        "crm.html",
        stages=stages,
        total_pipeline=len(all_opps),
        customers=customers
    )

@crm_bp.route("/crm/opportunity/<int:opportunity_id>/status", methods=["POST"])
@login_required
def update_status(opportunity_id):
    new_status = request.form.get("status")
    recovered_amount = request.form.get("recovered_amount")
    
    CRMService.transition_opportunity_status(
        opportunity_id=opportunity_id,
        new_status=new_status,
        recovered_amount=recovered_amount
    )
    flash(f"Opportunity #{opportunity_id} status updated to {new_status}.", "success")
    return redirect(request.referrer or url_for("crm.crm_view"))

@crm_bp.route("/leads")
@login_required
def list_leads():
    """Shows cart abandonment leads and visitor intent records."""
    behaviors = CustomerBehavior.query.filter_by(purchased=False).order_by(CustomerBehavior.last_activity.desc()).all()
    return render_template("leads.html", leads=behaviors)

@crm_bp.route("/products")
@login_required
def list_products():
    """Product catalog management view."""
    products = Product.query.order_by(Product.price.desc()).all()
    total_stock = sum(p.stock for p in products)
    categories = sorted(list(set(p.category for p in products)))
    return render_template("products.html", products=products, total_stock=total_stock, categories=categories)

@crm_bp.route("/communications")
@login_required
def list_communications():
    """Dedicated communication log and delivery status view."""
    logs = CommunicationLog.query.order_by(CommunicationLog.sent_at.desc()).all()
    return render_template("communications.html", logs=logs)

@crm_bp.route("/architecture")
@login_required
def architecture_view():
    """Interactive Lucid-style architecture diagrams viewer."""
    return render_template("architecture.html")
