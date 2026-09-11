"""
Customer management routes.
"""

from flask import Blueprint, render_template, request
from routes.auth import login_required
from services.crm_service import CRMService

customers_bp = Blueprint("customers", __name__)

@customers_bp.route("/customers")
@login_required
def list_customers():
    search = request.args.get("search", "")
    value_filter = request.args.get("tier", "ALL")
    customers = CRMService.list_customers(search=search, value_filter=value_filter)
    return render_template(
        "customers.html",
        customers=customers,
        search=search,
        selected_tier=value_filter
    )

@customers_bp.route("/customers/<int:customer_id>")
@login_required
def customer_detail(customer_id):
    profile = CRMService.get_customer_profile(customer_id)
    return render_template(
        "customer_detail.html",
        customer=profile["customer"],
        sales=profile["sales"],
        behaviors=profile["behaviors"],
        opportunities=profile["opportunities"],
        actions=profile["actions"],
        communications=profile["communications"],
        total_spent=profile["total_spent"],
        sales_count=profile["completed_sales_count"]
    )
