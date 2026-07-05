"""Tests for the billing-api service.

All endpoints use in-memory storage. Tests are isolated per run.
"""

from fastapi.testclient import TestClient

from billing_api.app import app

client = TestClient(app)


class TestHealth:
    def test_health_returns_200(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["service"] == "billing-api"


class TestCreateInvoice:
    def test_valid_invoice_returns_200(self):
        payload = {
            "customer_id": "cust-001",
            "amount": 5000,
            "description": "Monthly hosting fee",
        }
        resp = client.post("/invoices", json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body["customer_id"] == "cust-001"
        assert body["amount"] == 5000
        assert body["description"] == "Monthly hosting fee"
        assert "invoice_id" in body
        assert "audit_id" in body
        assert "created_at" in body

    def test_negative_amount_returns_422(self):
        payload = {
            "customer_id": "cust-001",
            "amount": -100,
            "description": "Bad invoice",
        }
        resp = client.post("/invoices", json=payload)
        # Pydantic v2 validation errors produce 422 by default
        assert resp.status_code == 422

    def test_zero_amount_returns_422(self):
        payload = {
            "customer_id": "cust-001",
            "amount": 0,
            "description": "Zero amount invoice",
        }
        resp = client.post("/invoices", json=payload)
        assert resp.status_code == 422

    def test_missing_customer_id_returns_422(self):
        payload = {"amount": 1000, "description": "Missing customer"}
        resp = client.post("/invoices", json=payload)
        assert resp.status_code == 422


class TestGetInvoice:
    def test_get_existing_invoice(self):
        # Create an invoice first
        create_resp = client.post(
            "/invoices",
            json={
                "customer_id": "cust-002",
                "amount": 2500,
                "description": "Setup fee",
            },
        )
        invoice_id = create_resp.json()["invoice_id"]

        # Retrieve it
        resp = client.get(f"/invoices/{invoice_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["invoice_id"] == invoice_id
        assert body["customer_id"] == "cust-002"
        assert body["amount"] == 2500

    def test_get_nonexistent_invoice_returns_404(self):
        resp = client.get("/invoices/nonexistent-id")
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"]


class TestCreateSubscription:
    def test_valid_subscription_returns_200(self):
        payload = {
            "customer_id": "cust-003",
            "plan": "pro",
            "price": 2999,
        }
        resp = client.post("/subscriptions", json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body["customer_id"] == "cust-003"
        assert body["plan"] == "pro"
        assert body["price"] == 2999
        assert "subscription_id" in body
        assert "audit_id" in body

    def test_invalid_plan_returns_422(self):
        payload = {
            "customer_id": "cust-004",
            "plan": "platinum",
            "price": 5000,
        }
        resp = client.post("/subscriptions", json=payload)
        assert resp.status_code == 422

    def test_negative_price_returns_422(self):
        payload = {
            "customer_id": "cust-005",
            "plan": "basic",
            "price": -1,
        }
        resp = client.post("/subscriptions", json=payload)
        assert resp.status_code == 422

    def test_empty_plan_returns_422(self):
        payload = {
            "customer_id": "cust-006",
            "plan": "",
            "price": 1000,
        }
        resp = client.post("/subscriptions", json=payload)
        assert resp.status_code == 422
