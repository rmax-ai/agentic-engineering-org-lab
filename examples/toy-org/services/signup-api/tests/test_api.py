"""Integration tests for signup-api endpoints."""

from fastapi.testclient import TestClient

from signup_api.app import app

client = TestClient(app)


def test_health_returns_200():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_signup_valid_data_returns_200():
    response = client.post(
        "/signup",
        json={"email": "user@example.com", "password": "securepass", "name": "Alice"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "user_id" in data


def test_signup_invalid_email_returns_400():
    response = client.post(
        "/signup",
        json={"email": "notanemail", "password": "securepass", "name": "Alice"},
    )
    assert response.status_code == 400
    assert "error" in response.json()


def test_signup_short_password_returns_400():
    response = client.post(
        "/signup",
        json={"email": "user@example.com", "password": "short", "name": "Alice"},
    )
    assert response.status_code == 400


def test_signup_empty_name_returns_400():
    response = client.post(
        "/signup",
        json={"email": "user@example.com", "password": "securepass", "name": ""},
    )
    assert response.status_code == 400


def test_signup_missing_field_returns_400():
    response = client.post(
        "/signup",
        json={"email": "user@example.com", "password": "securepass"},
    )
    assert response.status_code == 400
