"""
Detailed Analytics and Model Performance routes.
"""

from flask import Blueprint, render_template
from routes.auth import login_required
from services.analytics_service import AnalyticsService

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/analytics")
@login_required
def analytics_view():
    data = AnalyticsService.get_dashboard_data()
    return render_template(
        "analytics.html",
        kpis=data["kpis"],
        charts=data["charts"],
        ml_metrics=data["ml_metrics"]
    )
