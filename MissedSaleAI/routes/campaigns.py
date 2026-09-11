"""
Email Campaigns and Communication logs routes.
"""

from flask import Blueprint, render_template, request
from routes.auth import login_required
from models import Campaign, CommunicationLog
from config import Config

campaigns_bp = Blueprint("campaigns", __name__)

@campaigns_bp.route("/campaigns")
@login_required
def list_campaigns():
    campaigns = Campaign.query.order_by(Campaign.sent_at.desc()).all()
    logs = CommunicationLog.query.order_by(CommunicationLog.sent_at.desc()).all()
    
    return render_template(
        "campaigns.html",
        campaigns=campaigns,
        logs=logs,
        is_resend_configured=bool(Config.RESEND_API_KEY),
        demo_mode=Config.DEMO_EMAIL_MODE
    )
