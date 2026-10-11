import pytest
from starlette.testclient import TestClient
from app.main import app
from app.db.seed_data import seed_database
from app.services.inventory_service import get_inventory_summary

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    seed_database(force_reset=True)

SAMPLE_DISASTER = {
    "incident_name": "Tropical Cyclone Jasper",
    "disaster_type": "CYCLONE",
    "region": "Far North Queensland",
    "affected_population": 16000,
    "displaced_population": 5000,
    "hazard_intensity": 0.85,
    "vulnerability_score": 0.65,
    "coping_capacity": 0.40,
    "infrastructure_damage": 0.70
}

# -------------------------------------------------------------
# 1. Proposal Creation & Zero-Deduction Verification
# -------------------------------------------------------------
def test_propose_creates_pending_approval_without_deduction():
    """Verify that proposing a disaster does NOT deduct inventory or send alerts."""
    initial_inv = get_inventory_summary()
    initial_total_stock = sum(s.quantity_available for s in initial_inv.stock)

    # Emergency officer submits proposal
    res = client.post(
        "/api/disaster/propose",
        json=SAMPLE_DISASTER,
        headers={"X-User-Role": "EMERGENCY_OFFICER"}
    )
    assert res.status_code == 200
    data = res.json()
    
    assert data["status"] == "PENDING_APPROVAL"
    assert data["created_by_role"] == "EMERGENCY_OFFICER"
    assert data["inventory_updated"] is False
    assert data["incident_id"].startswith("INC-")

    # Inventory must remain exactly unchanged!
    current_inv = get_inventory_summary()
    current_total_stock = sum(s.quantity_available for s in current_inv.stock)
    assert current_total_stock == initial_total_stock

# -------------------------------------------------------------
# 2. Authorized Approval Commits Inventory & Dispatches SNS
# -------------------------------------------------------------
def test_approval_by_logistics_director():
    """Verify that LOGISTICS_DIRECTOR approval deducts stock and broadcasts alert."""
    initial_inv = get_inventory_summary()
    initial_total_stock = sum(s.quantity_available for s in initial_inv.stock)

    # 1. Propose
    res_prop = client.post(
        "/api/disaster/propose",
        json=SAMPLE_DISASTER,
        headers={"X-User-Role": "EMERGENCY_OFFICER"}
    )
    inc_id = res_prop.json()["incident_id"]
    allocated_units = res_prop.json()["allocation_plan"]["total_allocated_units"]

    # 2. Approve by LOGISTICS_DIRECTOR
    res_app = client.post(
        f"/api/disaster/approve/{inc_id}",
        json={"notes": "Cleared for immediate release"},
        headers={"X-User-Role": "LOGISTICS_DIRECTOR"}
    )
    assert res_app.status_code == 200
    data = res_app.json()

    assert data["status"] == "APPROVED_DISPATCHED"
    assert data["approved_by_role"] == "LOGISTICS_DIRECTOR"
    assert data["inventory_updated"] is True
    assert data["sns_alert"]["simulated"] is True
    assert data["dispatched_items_count"] == allocated_units

    # Verify inventory was accurately decremented
    updated_inv = get_inventory_summary()
    updated_total_stock = sum(s.quantity_available for s in updated_inv.stock)
    assert updated_total_stock == initial_total_stock - allocated_units

# -------------------------------------------------------------
# 3. Prevent Duplicate Approvals & Duplicate Stock Deductions
# -------------------------------------------------------------
def test_prevent_duplicate_approvals():
    """Verify that a proposal cannot be approved twice."""
    res_prop = client.post(
        "/api/disaster/propose",
        json=SAMPLE_DISASTER,
        headers={"X-User-Role": "EMERGENCY_OFFICER"}
    )
    inc_id = res_prop.json()["incident_id"]

    # First approval succeeds
    res_first = client.post(
        f"/api/disaster/approve/{inc_id}",
        headers={"X-User-Role": "LOGISTICS_DIRECTOR"}
    )
    assert res_first.status_code == 200

    inv_after_first = sum(s.quantity_available for s in get_inventory_summary().stock)

    # Second approval attempt MUST fail with HTTP 400
    res_second = client.post(
        f"/api/disaster/approve/{inc_id}",
        headers={"X-User-Role": "LOGISTICS_DIRECTOR"}
    )
    assert res_second.status_code == 400
    assert "Duplicate approval rejected" in res_second.json()["detail"]

    # Stock must NOT be deducted a second time
    inv_after_second = sum(s.quantity_available for s in get_inventory_summary().stock)
    assert inv_after_second == inv_after_first

# -------------------------------------------------------------
# 4. Rejection Workflow & Zero Inventory Deduction
# -------------------------------------------------------------
def test_rejection_workflow_and_zero_deduction():
    """Verify that a rejected proposal updates status and does NOT deduct stock."""
    initial_stock = sum(s.quantity_available for s in get_inventory_summary().stock)

    res_prop = client.post(
        "/api/disaster/propose",
        json=SAMPLE_DISASTER,
        headers={"X-User-Role": "EMERGENCY_OFFICER"}
    )
    inc_id = res_prop.json()["incident_id"]

    # Reject
    res_rej = client.post(
        f"/api/disaster/reject/{inc_id}",
        json={"reason": "Hazard subsided; regional mutual aid adequate"},
        headers={"X-User-Role": "LOGISTICS_DIRECTOR"}
    )
    assert res_rej.status_code == 200
    assert res_rej.json()["status"] == "REJECTED"
    assert res_rej.json()["inventory_updated"] is False

    # Check stock intact
    assert sum(s.quantity_available for s in get_inventory_summary().stock) == initial_stock

    # Attempting to approve rejected incident must fail
    res_app_rej = client.post(
        f"/api/disaster/approve/{inc_id}",
        headers={"X-User-Role": "LOGISTICS_DIRECTOR"}
    )
    assert res_app_rej.status_code == 400
    assert "REJECTED" in res_app_rej.json()["detail"]

# -------------------------------------------------------------
# 5. RBAC Backend Enforcement (403 Forbidden Checks)
# -------------------------------------------------------------
def test_rbac_backend_permission_boundaries():
    """Verify backend rejection of unauthorized roles."""
    # 1. AUDITOR cannot create proposals (403)
    res_auditor_prop = client.post(
        "/api/disaster/propose",
        json=SAMPLE_DISASTER,
        headers={"X-User-Role": "AUDITOR"}
    )
    assert res_auditor_prop.status_code == 403
    assert "Access Denied" in res_auditor_prop.json()["detail"]

    # 2. EMERGENCY_OFFICER creates proposal (200)
    res_prop = client.post(
        "/api/disaster/propose",
        json=SAMPLE_DISASTER,
        headers={"X-User-Role": "EMERGENCY_OFFICER"}
    )
    inc_id = res_prop.json()["incident_id"]

    # 3. EMERGENCY_OFFICER cannot approve dispatch (403)
    res_officer_app = client.post(
        f"/api/disaster/approve/{inc_id}",
        headers={"X-User-Role": "EMERGENCY_OFFICER"}
    )
    assert res_officer_app.status_code == 403
    assert "Access Denied" in res_officer_app.json()["detail"]

    # 4. AUDITOR cannot approve dispatch (403)
    res_auditor_app = client.post(
        f"/api/disaster/approve/{inc_id}",
        headers={"X-User-Role": "AUDITOR"}
    )
    assert res_auditor_app.status_code == 403

    # 5. AUDITOR cannot reset inventory (403)
    res_auditor_reset = client.post(
        "/api/inventory/reset",
        headers={"X-User-Role": "AUDITOR"}
    )
    assert res_auditor_reset.status_code == 403

# -------------------------------------------------------------
# 6. Multi-Region DPRI Prioritization
# -------------------------------------------------------------
def test_multi_region_dpri_prioritization():
    """Verify batch calculation and sorting of concurrent regional disasters."""
    regions_batch = [
        {
            "incident_name": "Lowland Runoff",
            "disaster_type": "FLOOD",
            "region": "Zone C",
            "affected_population": 3000,
            "displaced_population": 500,
            "hazard_intensity": 0.3,
            "vulnerability_score": 0.3,
            "coping_capacity": 0.8,
            "infrastructure_damage": 0.2
        },
        {
            "incident_name": "Major Fault Rupture",
            "disaster_type": "EARTHQUAKE",
            "region": "Zone A",
            "affected_population": 45000,
            "displaced_population": 18000,
            "hazard_intensity": 0.95,
            "vulnerability_score": 0.85,
            "coping_capacity": 0.2,
            "infrastructure_damage": 0.95
        },
        {
            "incident_name": "Severe Cyclone",
            "disaster_type": "CYCLONE",
            "region": "Zone B",
            "affected_population": 20000,
            "displaced_population": 7000,
            "hazard_intensity": 0.8,
            "vulnerability_score": 0.6,
            "coping_capacity": 0.5,
            "infrastructure_damage": 0.6
        }
    ]
    res = client.post("/api/disaster/prioritize-regions", json=regions_batch)
    assert res.status_code == 200
    data = res.json()

    assert data["total_regions_evaluated"] == 3
    assert len(data["ranked_regions"]) == 3
    
    # Highest DPRI must be Rank 1 (Major Fault Rupture - Zone A)
    rank1 = data["ranked_regions"][0]
    rank2 = data["ranked_regions"][1]
    rank3 = data["ranked_regions"][2]

    assert rank1["rank"] == 1
    assert rank1["region"] == "Zone A"
    assert rank1["dpri_score"] >= rank2["dpri_score"] >= rank3["dpri_score"]

# -------------------------------------------------------------
# 7. Audit History Includes Status & Acting Demo Role
# -------------------------------------------------------------
def test_audit_history_records_full_lifecycle():
    """Verify that history includes status, created_by_role, approved_by_role."""
    # 1. Propose
    res_prop = client.post(
        "/api/disaster/propose",
        json=SAMPLE_DISASTER,
        headers={"X-User-Role": "EMERGENCY_OFFICER"}
    )
    inc_id = res_prop.json()["incident_id"]

    # 2. Approve
    client.post(
        f"/api/disaster/approve/{inc_id}",
        headers={"X-User-Role": "LOGISTICS_DIRECTOR"}
    )

    # 3. Inspect history
    res_hist = client.get("/api/disaster/history")
    assert res_hist.status_code == 200
    records = res_hist.json()
    
    target = next((r for r in records if r["incident_id"] == inc_id), None)
    assert target is not None
    assert target["status"] == "APPROVED_DISPATCHED"
    assert target["created_by_role"] == "EMERGENCY_OFFICER"
    assert target["approved_by_role"] == "LOGISTICS_DIRECTOR"
    assert target["approved_at"] is not None
