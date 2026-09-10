from fastapi.testclient import TestClient

from operations_copilot.api import app

client = TestClient(app)


def test_health_and_capabilities():
    assert client.get("/health").json() == {"status": "ok", "version": "0.2.0"}
    response = client.get("/capabilities")
    assert response.status_code == 200
    assert "waiting_approval" in response.json()["workflow_statuses"]


def test_transition_contract():
    response = client.post(
        "/workflows/transition",
        json={"status": "draft", "action": "start"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_invalid_transition_returns_validation_error():
    response = client.post(
        "/workflows/transition",
        json={"status": "completed", "action": "start"},
    )
    assert response.status_code == 409
