"""
Email Service integrated with Resend API.
Strictly dispatches REAL emails to REAL email addresses via the Resend API.

Key Design Principles:
1. Zero fake delivery: Never returns success=True unless the Resend API accepted the email and returned a message ID.
2. Safe Demo Mode: Clearly reports DEMO_UNSENT when RESEND_API_KEY is not configured.
3. Security: API keys are strictly kept on backend; safe sanitized errors returned to clients.
4. Safety rules: Opt-out suppression and rate limiting (daily cap & interval).
5. Full CRM audit: Automatically persists records in communication_logs with provider, message ID, and status.
"""

import os
import re
from datetime import datetime, timezone
import requests
from flask import current_app, has_app_context
from config import Config
from models import db, Customer, CommunicationLog, Campaign, RecoveryOpportunity

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

class EmailService:
    def __init__(self, api_key=None, email_from=None, demo_mode=None):
        self._api_key = api_key
        self._email_from = email_from
        self._demo_mode = demo_mode
        self.resend_endpoint = "https://api.resend.com/emails"

    @property
    def api_key(self):
        if self._api_key is not None:
            return (self._api_key or "").strip()
        if has_app_context():
            return (current_app.config.get("RESEND_API_KEY") or "").strip()
        return (Config.RESEND_API_KEY or "").strip()

    @property
    def email_from(self):
        if self._email_from is not None:
            return self._email_from
        if has_app_context():
            return current_app.config.get("EMAIL_FROM", Config.EMAIL_FROM)
        return Config.EMAIL_FROM

    @property
    def demo_mode(self):
        if self._demo_mode is not None:
            return self._demo_mode
        if has_app_context():
            return current_app.config.get("DEMO_EMAIL_MODE", Config.DEMO_EMAIL_MODE)
        return Config.DEMO_EMAIL_MODE

    def is_configured(self):
        """Returns True when an API key is present."""
        return bool(self.api_key and len(self.api_key) > 5)

    def validate_email(self, email):
        """
        Validates email address.
        Returns (is_valid: bool, error_message: str or None).
        """
        if not email or not isinstance(email, str) or not email.strip():
            return False, "Recipient email address cannot be empty."
        cleaned = email.strip()
        if not EMAIL_REGEX.match(cleaned):
            return False, f"Invalid email format: '{cleaned}' is not a valid email address."
        return True, None

    def send_recovery_email(self, to_email, customer_name, subject, body_text, customer_id=None, opportunity_id=None):
        """
        Sends real recovery email via the Resend API.
        Enforces:
        - Email syntax validation
        - Customer opt-out check
        - Customer rate-limiting check
        - Direct call to Resend API
        - Database logging with Resend Message ID
        - CRM status synchronization (EMAIL_SENT or EMAIL_FAILED)
        """
        # 1. Email Address Validation
        is_valid, validation_err = self.validate_email(to_email)
        if not is_valid:
            return {
                "success": False,
                "status": "INVALID_EMAIL",
                "mode": "VALIDATION_ERROR",
                "error": validation_err,
                "message": validation_err
            }

        cleaned_email = to_email.strip()

        # 2. Required Fields Validation
        if not subject or not subject.strip():
            return {
                "success": False,
                "status": "VALIDATION_ERROR",
                "error": "Email subject cannot be empty.",
                "message": "Email subject cannot be empty."
            }
        if not body_text or not body_text.strip():
            return {
                "success": False,
                "status": "VALIDATION_ERROR",
                "error": "Email message body cannot be empty.",
                "message": "Email message body cannot be empty."
            }

        # 3. Customer Communication Rules Check
        customer = db.session.get(Customer, customer_id) if customer_id else None
        if not customer:
            customer = Customer.query.filter_by(email=cleaned_email).first()
            if customer:
                customer_id = customer.id

        if customer:
            # Opt-out check (Section 19)
            if getattr(customer, "email_opt_out", False):
                self._log_communication(
                    customer_id=customer.id,
                    recipient=cleaned_email,
                    status="SUPPRESSED_OPT_OUT",
                    subject=subject,
                    body=body_text,
                    resend_id=None,
                    opportunity_id=opportunity_id,
                    error_message="Customer opted out"
                )
                return {
                    "success": False,
                    "status": "SUPPRESSED_OPT_OUT",
                    "mode": "OPT_OUT",
                    "error": "Email not sent because customer has opted out.",
                    "message": "Email not sent because customer has opted out."
                }

            # Rate Limiting Check (Section 18)
            allowed, rate_reason = customer.check_rate_limit(
                max_per_day=Config.MAX_EMAILS_PER_DAY,
                min_interval_seconds=Config.MIN_EMAIL_INTERVAL_SECONDS
            )
            if not allowed:
                return {
                    "success": False,
                    "status": "RATE_LIMITED",
                    "mode": "RATE_LIMITED",
                    "error": rate_reason,
                    "message": rate_reason
                }

        # 4. Check if Resend API is configured
        if not self.is_configured() or self.demo_mode:
            # Section 25 Demo Mode: NEVER show "Email sent successfully" in demo mode.
            msg = (
                "DEMO MODE: Real email sending is disabled because RESEND_API_KEY is not configured. "
                "Demo email generated but NOT sent. Please configure RESEND_API_KEY in your .env file."
            )
            self._log_communication(
                customer_id=customer_id,
                recipient=cleaned_email,
                status="DEMO_UNSENT",
                subject=subject,
                body=body_text,
                resend_id=None,
                opportunity_id=opportunity_id,
                error_message="RESEND_API_KEY not configured (Demo Mode)"
            )
            return {
                "success": False,
                "status": "DEMO_UNSENT",
                "mode": "DEMO_MODE",
                "recipient": cleaned_email,
                "message": msg,
                "error": msg
            }

        # 5. Live Resend API Dispatch (Backend Only, HTTPS)
        html_content = self._render_html_template(customer_name, subject, body_text)
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "from": self.email_from,
                "to": [cleaned_email],
                "subject": subject,
                "text": body_text,
                "html": html_content
            }
            response = requests.post(self.resend_endpoint, json=payload, headers=headers, timeout=12)

            if response.status_code in (200, 201):
                data = response.json()
                resend_id = data.get("id")
                
                # Update database communication log
                self._log_communication(
                    customer_id=customer_id,
                    recipient=cleaned_email,
                    status="SENT",
                    subject=subject,
                    body=body_text,
                    resend_id=resend_id,
                    opportunity_id=opportunity_id
                )

                # Update CRM opportunity status to EMAIL_SENT
                if opportunity_id:
                    opp = db.session.get(RecoveryOpportunity, opportunity_id)
                    if opp:
                        opp.status = "EMAIL_SENT"
                        db.session.commit()

                return {
                    "success": True,
                    "status": "SENT",
                    "mode": "LIVE",
                    "message_id": resend_id,
                    "provider": "Resend",
                    "recipient": cleaned_email,
                    "message": f"✓ Email sent successfully to {cleaned_email}"
                }
            else:
                safe_error = self._sanitize_resend_error(response)
                
                self._log_communication(
                    customer_id=customer_id,
                    recipient=cleaned_email,
                    status="FAILED",
                    subject=subject,
                    body=body_text,
                    resend_id=None,
                    opportunity_id=opportunity_id,
                    error_message=safe_error
                )

                # Keep/Set CRM status to EMAIL_FAILED
                if opportunity_id:
                    opp = db.session.get(RecoveryOpportunity, opportunity_id)
                    if opp:
                        opp.status = "EMAIL_FAILED"
                        db.session.commit()

                return {
                    "success": False,
                    "status": "FAILED",
                    "mode": "LIVE",
                    "error": safe_error,
                    "recipient": cleaned_email,
                    "message": f"✕ Email could not be sent. Reason: {safe_error}"
                }

        except requests.exceptions.RequestException as exc:
            safe_error = f"Network connection error while contacting Resend API: {str(exc)}"
            self._log_communication(
                customer_id=customer_id,
                recipient=cleaned_email,
                status="FAILED",
                subject=subject,
                body=body_text,
                resend_id=None,
                opportunity_id=opportunity_id,
                error_message=safe_error
            )
            if opportunity_id:
                opp = db.session.get(RecoveryOpportunity, opportunity_id)
                if opp:
                    opp.status = "EMAIL_FAILED"
                    db.session.commit()

            return {
                "success": False,
                "status": "FAILED",
                "mode": "LIVE",
                "error": safe_error,
                "recipient": cleaned_email,
                "message": f"✕ Email could not be sent. Reason: {safe_error}"
            }

    def send_test_email(self, to_email):
        """
        Sends an integration verification test email to verify that the Resend API is functional.
        Never pretends success if not configured or if the API rejects it.
        """
        is_valid, validation_err = self.validate_email(to_email)
        if not is_valid:
            return {
                "success": False,
                "status": "INVALID_EMAIL",
                "error": validation_err,
                "message": validation_err
            }

        subject = "MissedSale AI: Integration Test Verification"
        body_text = (
            f"Hello,\n\n"
            f"This is a real diagnostic verification email from your MissedSale AI Autonomous Platform.\n"
            f"Your Resend API integration is fully operational and authenticated.\n\n"
            f"Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"Sender: {self.email_from}\n\n"
            f"Best regards,\nMissedSale AI"
        )
        return self.send_recovery_email(
            to_email=to_email,
            customer_name="Administrator",
            subject=subject,
            body_text=body_text
        )

    def process_resend_webhook(self, payload):
        """
        Processes asynchronous incoming Resend webhook events:
        email.delivered, email.opened, email.clicked, email.bounced.
        Updates communication_logs table.
        """
        event_type = payload.get("type", "")
        data = payload.get("data", {})
        email_id = data.get("email_id") or data.get("id")

        if not email_id:
            return {"status": "ignored", "event": event_type, "reason": "No email_id in webhook payload"}

        comm_log = CommunicationLog.query.filter_by(resend_id=email_id).first()
        if comm_log:
            if event_type == "email.delivered":
                comm_log.status = "DELIVERED"
            elif event_type == "email.opened":
                comm_log.status = "OPENED"
            elif event_type == "email.clicked":
                comm_log.status = "CLICKED"
            elif event_type == "email.bounced":
                comm_log.status = "BOUNCED"
            elif event_type in ("email.failed", "email.complained"):
                comm_log.status = "FAILED"
            db.session.commit()
            return {
                "status": "updated",
                "event": event_type,
                "email_id": email_id,
                "new_status": comm_log.status
            }

        return {"status": "not_found", "event": event_type, "email_id": email_id}

    def _sanitize_resend_error(self, response):
        """Extracts user-friendly error without leaking sensitive credentials."""
        try:
            err_json = response.json()
            if isinstance(err_json, dict):
                msg = err_json.get("message") or err_json.get("error") or response.text
                return f"Resend API error ({response.status_code}): {msg}"
        except Exception:
            pass
        return f"Resend API error ({response.status_code}): {response.text[:200]}"

    def _log_communication(self, customer_id, recipient, status, subject, body, resend_id, opportunity_id, error_message=None):
        """Persists email communication log and updates customer metrics."""
        log_entry = CommunicationLog(
            customer_id=customer_id,
            opportunity_id=opportunity_id,
            channel="EMAIL",
            recipient=recipient,
            status=status,
            subject=subject,
            body=body,
            provider="Resend",
            resend_id=resend_id,
            error_message=error_message,
            sent_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(log_entry)

        if status == "SENT":
            campaign = Campaign(
                customer_id=customer_id or 1,
                opportunity_id=opportunity_id,
                subject=subject,
                message=body,
                status="SENT",
                sent_at=datetime.now(timezone.utc)
            )
            db.session.add(campaign)

            if customer_id:
                customer = db.session.get(Customer, customer_id)
                if customer:
                    customer.email_count = (customer.email_count or 0) + 1
                    customer.last_email_sent = datetime.now(timezone.utc)

        db.session.commit()

    def _render_html_template(self, customer_name, subject, body_text):
        """Generates modern responsive HTML email."""
        paragraphs = body_text.split("\n\n")
        html_paragraphs = "".join([
            f"<p style='margin: 0 0 16px 0; line-height: 1.6; color: #334155;'>{p.replace(chr(10), '<br>')}</p>"
            for p in paragraphs if p.strip()
        ])

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{subject}</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; padding: 24px; margin: 0;">
    <table width="100%" border="0" cellspacing="0" cellpadding="0">
        <tr>
            <td align="center">
                <table width="600" border="0" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                    <tr>
                        <td style="background: linear-gradient(135deg, #0ea5e9, #6366f1); padding: 24px 32px; color: #ffffff;">
                            <h2 style="margin: 0; font-size: 20px; font-weight: 700; letter-spacing: -0.5px;">MissedSale AI Recovery</h2>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 32px; font-size: 15px;">
                            {html_paragraphs}
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #f8fafc; padding: 16px 32px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0;">
                            Sent automatically by MissedSale AI Autonomous Recovery System.<br>
                            To manage communication preferences or unsubscribe, reply with "UNSUBSCRIBE".
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""
