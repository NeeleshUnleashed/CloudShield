import pytest
from starlette.testclient import TestClient
from app.main import app
from app.db.seed_data import seed_database
from app.services.inventory_service import get_inventory_summary

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_db_before_test():
    seed_database(force_reset=True)

# -------------------------------------------------------------
# Test 1: All Four Preset Scenarios
# -------------------------------------------------------------
def test_all_four_presets():
    """Verify that all 4 UI presets execute cleanly through the full workflow."""
    presets = [
        {
            "name": "Severe Cyclone Veronica",
            "type": "CYCLONE",
            "region": "Pilbara Coastal Region",
            "affected": 22000,
            "displaced": 8500,
            "hazard": 0.90,
            "vuln": 0.75,
            "coping": 0.35,
            "infra": 0.80
        },
        {
            "name": "Magnitude 7.2 Fault Rupture",
            "type": "EARTHQUAKE",
            "region": "Central Metropolitan Basin",
            "affected": 35000,
            "displaced": 15000,
            "hazard": 0.95,
            "vuln": 0.80,
            "coping": 0.30,
            "infra": 0.90
        },
        {
            "name": "Major River Basin Flash Flood",
            "type": "FLOOD",
            "region": "Northern Delta Plains",
            "affected": 14000,
            "displaced": 4200,
            "hazard": 0.70,
            "vuln": 0.60,
            "coping": 0.50,
            "infra": 0.60
        },
        {
            "name": "Extreme Forest Firestorm",
            "type": "WILDFIRE",
            "region": "East Gippsland Escarpment",
            "affected": 7500,
            "displaced": 2400,
            "hazard": 0.85,
            "vuln": 0.50,
            "coping": 0.60,
            "infra": 0.50
        }
    ]

    for p in presets:
        seed_database(force_reset=True)
        payload = {
            "incident_name": p["name"],
            "disaster_type": p["type"],
            "region": p["region"],
            "affected_population": p["affected"],
            "displaced_population": p["displaced"],
            "hazard_intensity": p["hazard"],
            "vulnerability_score": p["vuln"],
            "coping_capacity": p["coping"],
            "infrastructure_damage": p["infra"]
        }
        res = client.post("/api/disaster/workflow", json=payload)
        assert res.status_code == 200, f"Preset {p['name']} failed: {res.text}"
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert 0.0 <= data["dpri_result"]["dpri_score"] <= 1.0
        assert data["allocation_plan"]["total_allocated_units"] > 0
        assert data["sns_alert"]["simulated"] is True
        assert data["inventory_updated"] is True

# -------------------------------------------------------------
# Test 2: Input Validation & Edge Cases (Invalid inputs)
# -------------------------------------------------------------
def test_invalid_input_rejections():
    """Verify that malformed or out-of-bounds parameters return 422 HTTP errors."""
    # Negative population
    res_neg_pop = client.post("/api/disaster/workflow", json={
        "incident_name": "Invalid Incident",
        "disaster_type": "FLOOD",
        "region": "Zone A",
        "affected_population": -100,
        "displaced_population": 10,
        "hazard_intensity": 0.5,
        "vulnerability_score": 0.5,
        "coping_capacity": 0.5,
        "infrastructure_damage": 0.5
    })
    assert res_neg_pop.status_code == 422

    # Hazard intensity exceeding 1.0
    res_hazard = client.post("/api/disaster/workflow", json={
        "incident_name": "Invalid Hazard",
        "disaster_type": "FLOOD",
        "region": "Zone A",
        "affected_population": 1000,
        "displaced_population": 100,
        "hazard_intensity": 2.5,
        "vulnerability_score": 0.5,
        "coping_capacity": 0.5,
        "infrastructure_damage": 0.5
    })
    assert res_hazard.status_code == 422

    # Invalid disaster type enum
    res_type = client.post("/api/disaster/workflow", json={
        "incident_name": "Invalid Type",
        "disaster_type": "METEOR_STRIKE",
        "region": "Zone A",
        "affected_population": 1000,
        "displaced_population": 100,
        "hazard_intensity": 0.5,
        "vulnerability_score": 0.5,
        "coping_capacity": 0.5,
        "infrastructure_damage": 0.5
    })
    assert res_type.status_code == 422

# -------------------------------------------------------------
# Test 3: Insufficient Inventory (Demand Exceeding Total Stock)
# -------------------------------------------------------------
def test_insufficient_inventory_shortage_handling():
    """Verify handling when disaster demand exceeds entire network supply."""
    mega_disaster = {
        "incident_name": "Cataclysmic Super-Quake",
        "disaster_type": "EARTHQUAKE",
        "region": "Continent-Wide",
        "affected_population": 2500000,
        "displaced_population": 1000000,
        "hazard_intensity": 1.0,
        "vulnerability_score": 1.0,
        "coping_capacity": 0.05,
        "infrastructure_damage": 1.0
    }
    res = client.post("/api/disaster/workflow", json=mega_disaster)
    assert res.status_code == 200
    data = res.json()
    alloc = data["allocation_plan"]
    
    # Demands should exceed network capacity
    assert alloc["total_shortage_units"] > 0
    assert alloc["overall_fulfillment_rate"] < 100.0
    
    # Check that shortages are reported in the SNS message
    assert "CRITICAL SHORTAGES DETECTED" in data["sns_alert"]["message"]
    
    # Check that stock never falls below 0
    inv = get_inventory_summary()
    for s in inv.stock:
        assert s.quantity_available >= 0

# -------------------------------------------------------------
# Test 4: Repeated Workflow Execution until Depletion
# -------------------------------------------------------------
def test_repeated_workflow_execution():
    """Verify system stability across consecutive workflow runs without crashing."""
    incident = {
        "incident_name": "Recurring Aftershock",
        "disaster_type": "EARTHQUAKE",
        "region": "Coastal Province",
        "affected_population": 50000,
        "displaced_population": 20000,
        "hazard_intensity": 0.8,
        "vulnerability_score": 0.7,
        "coping_capacity": 0.4,
        "infrastructure_damage": 0.7
    }
    
    # Run multiple consecutive times
    for i in range(5):
        res = client.post("/api/disaster/workflow", json=incident)
        assert res.status_code == 200
        
    inv = get_inventory_summary()
    for s in inv.stock:
        assert s.quantity_available >= 0

# -------------------------------------------------------------
# Test 5: Inventory Reset Restores Baseline Correctly
# -------------------------------------------------------------
def test_inventory_reset_persistence():
    """Verify that inventory reset restores exact original stock numbers."""
    initial_inv = client.get("/api/inventory").json()
    initial_total = sum(s["quantity_available"] for s in initial_inv["stock"])
    
    # Deplete stock with a workflow
    client.post("/api/disaster/workflow", json={
        "incident_name": "Depletion Test",
        "disaster_type": "FLOOD",
        "region": "Depot Zone",
        "affected_population": 15000,
        "displaced_population": 4000,
        "hazard_intensity": 0.7,
        "vulnerability_score": 0.5,
        "coping_capacity": 0.5,
        "infrastructure_damage": 0.5
    })
    
    depleted_inv = client.get("/api/inventory").json()
    depleted_total = sum(s["quantity_available"] for s in depleted_inv["stock"])
    assert depleted_total < initial_total
    
    # Reset inventory
    reset_res = client.post("/api/inventory/reset")
    assert reset_res.status_code == 200
    reset_inv = reset_res.json()
    reset_total = sum(s["quantity_available"] for s in reset_inv["stock"])
    
    assert reset_total == initial_total
