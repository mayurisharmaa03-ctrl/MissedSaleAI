"""
Unit tests verifying the Plus Send Email Button, Compose Modal, and Edit Email functionality.
"""

from models import CommunicationLog

def login_admin(client):
    return client.get("/quick-demo-login", follow_redirects=True)

def test_campaigns_page_has_plus_send_email_button(client):
    login_admin(client)
    res = client.get("/campaigns")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    
    # 1. Verify '+' Send Email button on Raw Communication Protocol Logs card
    assert "btnSendRawLogEmail" in html
    assert "Raw Communication Protocol Logs" in html
    assert "fa-plus" in html
    
    # 2. Verify modal partial included
    assert "sendEmailModal" in html
    
    # 3. Verify 'Enter e-mail of customer' field
    assert "Enter e-mail of customer" in html
    assert "modalCustomerEmail" in html
    
    # 4. Verify 'Edit Email' button
    assert "Edit Email" in html
    assert "btnEditEmail" in html
    assert "modalEmailSubjectInput" in html
    assert "modalEmailBodyTextarea" in html

def test_communications_page_has_plus_send_email_button(client):
    login_admin(client)
    res = client.get("/communications")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    
    assert "btnSendCommCardEmail" in html
    assert "sendEmailModal" in html
    assert "Enter e-mail of customer" in html
    assert "btnEditEmail" in html

def test_top_navbar_has_global_plus_send_email_button(client):
    login_admin(client)
    res = client.get("/dashboard")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    
    # Global plus button in top navbar
    assert "openSendEmailModal()" in html
    assert "sendEmailModal" in html

def test_api_email_send_with_custom_edited_content(client, app):
    login_admin(client)
    
    payload = {
        "to": "test_edited_friend@gmail.com",
        "customer_name": "My Dear Friend",
        "subject": "Customized Subject: Special VIP Deal Just For You",
        "message": "Hi Friend, this is an edited custom message body with code VIP50."
    }
    res = client.post("/api/email/send", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["recipient"] == "test_edited_friend@gmail.com"
    assert data["status"] in ("SENT", "DEMO_UNSENT")
    
    # Verify CommunicationLog was recorded with the edited subject
    with app.app_context():
        log = CommunicationLog.query.filter_by(recipient="test_edited_friend@gmail.com").first()
        assert log is not None
        assert log.subject == "Customized Subject: Special VIP Deal Just For You"
