"""Regression checks for public errors, request IDs, and documented routes."""
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.github_client import github_client


def test_invalid_request_returns_400_without_echoing_payload():
    response = TestClient(app).post("/issues", json={"body": "sensitive-example"})
    assert response.status_code == 400
    assert response.json()["error"] == "validation_error"
    assert "sensitive-example" not in response.text
    assert response.headers["X-Request-ID"]


def test_request_id_is_returned_for_success_and_handled_failure(monkeypatch):
    client = TestClient(app)
    response = client.get("/healthz", headers={"X-Request-ID": "review-123"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "review-123"

    def unavailable(*args):
        raise HTTPException(503, "GitHub temporarily unavailable", headers={"Retry-After": "10"})

    monkeypatch.setattr(github_client, "list_issues", unavailable)
    response = client.get("/issues", headers={"X-Request-ID": "failure-123"})
    assert response.status_code == 503
    assert response.headers["Retry-After"] == "10"
    assert response.headers["X-Request-ID"] == "failure-123"
    assert response.json()["error"] == "service_unavailable"


def test_unexpected_failure_does_not_disclose_exception(monkeypatch):
    def broken(*args):
        raise RuntimeError("secret-example-do-not-disclose")

    monkeypatch.setattr(github_client, "list_issues", broken)
    response = TestClient(app, raise_server_exceptions=False).get("/issues")
    assert response.status_code == 500
    assert response.json()["error"] == "internal_server_error"
    assert "secret-example" not in response.text
    assert response.headers["X-Request-ID"]


def test_health_response_contains_the_documented_service_version():
    response = TestClient(app).get("/healthz")
    assert response.json() == {"status": "healthy", "service": "GitHub Issues Service", "version": "1.0.0"}
