"""
Dashboard routes for MissedSale AI.
"""

from flask import Blueprint, render_template, redirect, url_for, session
from routes.auth import login_required
from services.analytics_service import AnalyticsService
from models import RecoveryOpportunity, AgentAction

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def root():
    if "user_id" in session:
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))

@dashboard_bp.route("/dashboard")
@login_required
def index():
    data = AnalyticsService.get_dashboard_data()
    recent_actions = AgentAction.query.order_by(AgentAction.created_at.desc()).limit(6).all()
    priority_opportunities = RecoveryOpportunity.query.filter_by(priority="HIGH").order_by(RecoveryOpportunity.created_at.desc()).limit(5).all()
    
    return render_template(
        "dashboard.html",
        kpis=data["kpis"],
        charts=data["charts"],
        recent_actions=recent_actions,
        priority_opportunities=priority_opportunities
    )
