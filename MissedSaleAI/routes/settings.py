"""
System Settings and Agent Threshold Configuration routes.
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for
from routes.auth import login_required
from config import Config
from models import db
from agent.agent import SalesRecoveryAgent

settings_bp = Blueprint("settings", __name__)

@settings_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings_view():
    if request.method == "POST":
        Config.LOST_SALE_THRESHOLD = float(request.form.get("lost_sale_threshold", Config.LOST_SALE_THRESHOLD))
        Config.RECOVERY_THRESHOLD_HIGH = float(request.form.get("recovery_threshold_high", Config.RECOVERY_THRESHOLD_HIGH))
        Config.RECOVERY_THRESHOLD_MED = float(request.form.get("recovery_threshold_med", Config.RECOVERY_THRESHOLD_MED))
        Config.MAX_OUTREACH_ATTEMPTS = int(request.form.get("max_outreach_attempts", Config.MAX_OUTREACH_ATTEMPTS))
        
        # Resend API Key & Sender update
        new_key = request.form.get("resend_api_key", "").strip()
        if new_key and not new_key.startswith("•"):
            Config.RESEND_API_KEY = new_key
            
        new_sender = request.form.get("email_from", "").strip()
        if new_sender:
            Config.EMAIL_FROM = new_sender

        demo_mode_val = request.form.get("demo_mode")
        Config.DEMO_EMAIL_MODE = bool(demo_mode_val == "on")
        
        flash("Settings and agent decision thresholds updated successfully!", "success")
        return redirect(url_for("settings.settings_view"))
        
    db_uri = Config.SQLALCHEMY_DATABASE_URI
    db_engine_name = "PostgreSQL" if "postgres" in db_uri else "SQLite (Demo / Standalone)"
    is_configured = Config.is_resend_configured()
    
    return render_template(
        "settings.html",
        lost_threshold=Config.LOST_SALE_THRESHOLD,
        recov_high=Config.RECOVERY_THRESHOLD_HIGH,
        recov_med=Config.RECOVERY_THRESHOLD_MED,
        max_attempts=Config.MAX_OUTREACH_ATTEMPTS,
        is_resend_configured=is_configured,
        masked_api_key=(Config.RESEND_API_KEY[:4] + "••••••••••••••••") if is_configured else "",
        email_from=Config.EMAIL_FROM,
        email_mode="LIVE" if is_configured and not Config.DEMO_EMAIL_MODE else "DEMO",
        demo_email_mode=Config.DEMO_EMAIL_MODE,
        db_engine_name=db_engine_name,
        db_uri=db_uri
    )
