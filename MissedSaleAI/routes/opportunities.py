"""
Lost Sales and Recovery Opportunities routes.
"""

from flask import Blueprint, render_template, request
from routes.auth import login_required
from models import LostSale, RecoveryOpportunity

opportunities_bp = Blueprint("opportunities", __name__)

@opportunities_bp.route("/lost-sales")
@login_required
def lost_sales():
    status_filter = request.args.get("status", "ALL")
    query = LostSale.query
    if status_filter != "ALL":
        query = query.filter_by(status=status_filter)
    lost_list = query.order_by(LostSale.detected_at.desc()).all()
    return render_template("lost_sales.html", lost_sales=lost_list, selected_status=status_filter)

@opportunities_bp.route("/opportunities")
@login_required
def opportunities():
    status_filter = request.args.get("status", "ALL")
    priority_filter = request.args.get("priority", "ALL")
    
    query = RecoveryOpportunity.query
    if status_filter != "ALL":
        query = query.filter_by(status=status_filter)
    if priority_filter != "ALL":
        query = query.filter_by(priority=priority_filter)
        
    opps = query.order_by(RecoveryOpportunity.created_at.desc()).all()
    return render_template(
        "opportunities.html",
        opportunities=opps,
        selected_status=status_filter,
        selected_priority=priority_filter
    )
