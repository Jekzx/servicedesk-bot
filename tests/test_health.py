"""Unit tests for Health and Diagnostic endpoints."""


def test_api_basic_health(client):
    """Test basic liveness endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_monitored_services_health(client):
    """Test infrastructure services health list."""
    response = client.get("/api/health/services")
    assert response.status_code == 200
    data = response.json()
    assert "system_status" in data
    assert data["total_monitored"] >= 5
    assert len(data["services"]) >= 5


def test_run_on_demand_diagnostic(client):
    """Test running manual diagnostic check."""
    payload = {"target": "crm"}
    response = client.post("/api/health/diagnostics", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["target"] == "crm"
    assert data["status"] in ["OPERATIONAL", "DEGRADED"]
    assert data["is_operational"] is True
