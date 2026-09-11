"""
Tests for Flask REST API Endpoints.
"""

from models import Customer, RecoveryOpportunity, Product

def test_api_predict(client, app):
    with app.app_context():
        customer = Customer.query.first()
        res = client.post(f"/api/predict/{customer.id}")
        assert res.status_code == 200
        data = res.get_json()
        assert "predictions" in data
        assert "lost_sale_probability" in data["predictions"]

def test_api_agent_run(client, app):
    with app.app_context():
        customer = Customer.query.first()
        res = client.post(f"/api/agent/run/{customer.id}")
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True
        assert "trace" in data

def test_api_opportunities_action(client, app):
    with app.app_context():
        customer = Customer.query.first()
        product = Product.query.first()
        opp = RecoveryOpportunity(
            customer_id=customer.id,
            product_id=product.id,
            recovery_probability=0.8,
            priority="HIGH",
            recommended_action="SEND_PERSONALIZED_EMAIL",
            status="NEW"
        )
        from models import db
        db.session.add(opp)
        db.session.commit()
        
        # Test MARK_RECOVERED action
        res = client.post(
            f"/api/opportunities/{opp.id}/action",
            json={"action_type": "MARK_RECOVERED", "amount": 199.99}
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["success"] is True

def test_api_analytics_and_status(client, app):
    res_analytics = client.get("/api/analytics")
    assert res_analytics.status_code == 200
    data_analytics = res_analytics.get_json()
    assert "kpis" in data_analytics
    assert "charts" in data_analytics

    res_status = client.get("/api/agent/status")
    assert res_status.status_code == 200
    data_status = res_status.get_json()
    assert data_status["status"] == "ACTIVE"

def test_api_agent_activity(client, app):
    res = client.get("/api/agent/activity")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)

def test_api_customers_and_lost_sales(client, app):
    with app.app_context():
        customer = Customer.query.first()
        res_c = client.get(f"/api/customers/{customer.id}")
        assert res_c.status_code == 200
        assert res_c.get_json()["name"] == customer.name
        
        res_ls = client.get("/api/lost-sales")
        assert res_ls.status_code == 200
        assert isinstance(res_ls.get_json(), list)
        
        res_comm = client.get("/api/communications")
        assert res_comm.status_code == 200
        assert isinstance(res_comm.get_json(), list)

def test_api_email_test_and_webhook(client, app):
    # Test email test endpoint (without live key, returns DEMO_UNSENT in Demo Mode)
    res_test = client.post("/api/email/test", json={"to_email": "test_admin@example.com"})
    assert res_test.status_code == 200
    data = res_test.get_json()
    assert data["status"] in ("DEMO_UNSENT", "SENT")

    # Test webhook endpoint
    res_wh = client.post("/api/webhooks/resend", json={"type": "email.sent", "data": {}})
    assert res_wh.status_code == 200
    assert res_wh.get_json()["success"] is True

def test_api_demo_scenario(client, app):
    with app.app_context():
        from models import db, Customer
        rahul = Customer.query.filter_by(email="demo_customer@example.com").first()
        if not rahul:
            rahul = Customer(
                name="Rahul Sharma",
                email="demo_customer@example.com",
                phone="+91-98765-43210",
                customer_value="High"
            )
            db.session.add(rahul)
            db.session.commit()

        res_demo = client.get("/api/demo/run-scenario")
        assert res_demo.status_code == 200
        data = res_demo.get_json()
        assert data["status"] == "success"
        assert "Rahul Sharma" in data["scenario"]["customer"]

def test_crm_views_http_200(client, app):
    endpoints = ["/", "/dashboard", "/leads", "/products", "/communications", "/architecture", "/settings"]
    for ep in endpoints:
        res = client.get(ep, follow_redirects=True)
        assert res.status_code == 200
