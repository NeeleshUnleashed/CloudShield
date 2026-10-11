import pytest
from starlette.testclient import TestClient
from app.main import app
from app.db.seed_data import seed_database

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db():
    seed_database(force_reset=True)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["aws_mode"] == "mock"

def test_inventory_endpoint():
    response = client.get("/api/inventory")
    assert response.status_code == 200
    data = response.json()
    assert "warehouses" in data
    assert "stock" in data
    assert len(data["warehouses"]) == 4

def test_dpri_endpoint():
    payload = {
        "incident_name": "API Test Quake",
        "disaster_type": "EARTHQUAKE",
        "region": "Capital Region",
        "affected_population": 5000,
        "displaced_population": 1200,
        "hazard_intensity": 0.7,
        "vulnerability_score": 0.5,
        "coping_capacity": 0.6,
        "infrastructure_damage": 0.4
    }
    response = client.post("/api/disaster/dpri", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "dpri_score" in data
    assert "risk_level" in data
    assert 0.0 <= data["dpri_score"] <= 1.0

def test_workflow_api_endpoint():
    payload = {
        "incident_name": "API Test Cyclone",
        "disaster_type": "CYCLONE",
        "region": "Coastal Sector",
        "affected_population": 10000,
        "displaced_population": 3000,
        "hazard_intensity": 0.8,
        "vulnerability_score": 0.6,
        "coping_capacity": 0.5,
        "infrastructure_damage": 0.6
    }
    response = client.post("/api/disaster/workflow", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "dpri_result" in data
    assert "predicted_demand" in data
    assert "allocation_plan" in data
    assert "sns_alert" in data
    assert data["sns_alert"]["simulated"] is True
    assert data["inventory_updated"] is True

def test_incident_history_endpoint():
    # Run a workflow first
    payload = {
        "incident_name": "Logged Storm",
        "disaster_type": "FLOOD",
        "region": "River Valley",
        "affected_population": 4000,
        "displaced_population": 800,
        "hazard_intensity": 0.5,
        "vulnerability_score": 0.4,
        "coping_capacity": 0.7,
        "infrastructure_damage": 0.3
    }
    client.post("/api/disaster/workflow", json=payload)
    
    response = client.get("/api/disaster/history")
    assert response.status_code == 200
    history = response.json()
    assert len(history) >= 1
    assert any(h["incident_name"] == "Logged Storm" for h in history)
