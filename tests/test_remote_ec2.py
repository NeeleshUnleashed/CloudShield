import urllib.request
import json
import pytest

BASE_URL = "http://32.236.173.240:8000"

def test_live_ec2_e2e_workflow():
    # 0. Reset inventory to baseline
    req_reset = urllib.request.Request(
        BASE_URL + "/api/inventory/reset",
        data=b"",
        headers={"X-User-Role": "LOGISTICS_DIRECTOR"}
    )
    res_reset = urllib.request.urlopen(req_reset, timeout=10)
    assert res_reset.status == 200
    print("0. Inventory reset to baseline.")
    # 1. Dashboard UI
    ui_res = urllib.request.urlopen(BASE_URL + "/", timeout=10)
    assert ui_res.status == 200
    html_content = ui_res.read().decode("utf-8")
    assert "CloudShield" in html_content
    print("1. Dashboard UI loaded successfully.")

    # 2. Inventory check
    inv_res = urllib.request.urlopen(BASE_URL + "/api/inventory", timeout=10)
    inv_data = json.loads(inv_res.read().decode("utf-8"))
    assert len(inv_data["warehouses"]) == 4
    sydney_water_initial = next(
        s["quantity_available"]
        for s in inv_data["stock"]
        if s["warehouse_name"] == "Central Depot Sydney" and s["item_name"] == "Clean Drinking Water & Purification"
    )
    print(f"2. Inventory loaded. Sydney Water: {sydney_water_initial}")

    # 3. Propose Disaster (EMERGENCY_OFFICER)
    payload_1 = {
        "incident_name": "Cyclone Debbie - Far North QLD",
        "disaster_type": "CYCLONE",
        "region": "Cairns District",
        "affected_population": 20000,
        "displaced_population": 5000,
        "hazard_intensity": 0.85,
        "vulnerability_score": 0.60,
        "coping_capacity": 0.40,
        "infrastructure_damage": 0.70
    }
    req = urllib.request.Request(
        BASE_URL + "/api/disaster/propose",
        data=json.dumps(payload_1).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-User-Role": "EMERGENCY_OFFICER"}
    )
    res = urllib.request.urlopen(req, timeout=10)
    prop1 = json.loads(res.read().decode("utf-8"))
    inc1_id = prop1["incident_id"]
    assert prop1["status"] == "PENDING_APPROVAL"
    print(f"3. Proposed {inc1_id}: Status={prop1['status']}, DPRI={prop1['dpri_result']['dpri_score']}")

    # 4. Verify Zero Stock Deduction on Proposal
    inv_res = urllib.request.urlopen(BASE_URL + "/api/inventory", timeout=10)
    inv_data = json.loads(inv_res.read().decode("utf-8"))
    sydney_water_after_prop = next(
        s["quantity_available"]
        for s in inv_data["stock"]
        if s["warehouse_name"] == "Central Depot Sydney" and s["item_name"] == "Clean Drinking Water & Purification"
    )
    assert sydney_water_initial == sydney_water_after_prop, "Zero stock deduction violated!"
    print("4. Zero deduction on proposal VERIFIED.")

    # 5. Reject Disaster 1 (LOGISTICS_DIRECTOR)
    req_rej = urllib.request.Request(
        f"{BASE_URL}/api/disaster/reject/{inc1_id}",
        data=json.dumps({"reason": "Duplicate report"}).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-User-Role": "LOGISTICS_DIRECTOR"}
    )
    rej_res = urllib.request.urlopen(req_rej, timeout=10)
    rej_data = json.loads(rej_res.read().decode("utf-8"))
    assert rej_data["status"] == "REJECTED"
    print(f"5. Rejected {inc1_id}: Status={rej_data['status']}")

    # 6. Verify Zero Stock Deduction on Rejection
    inv_res = urllib.request.urlopen(BASE_URL + "/api/inventory", timeout=10)
    inv_data = json.loads(inv_res.read().decode("utf-8"))
    sydney_water_after_rej = next(
        s["quantity_available"]
        for s in inv_data["stock"]
        if s["warehouse_name"] == "Central Depot Sydney" and s["item_name"] == "Clean Drinking Water & Purification"
    )
    assert sydney_water_initial == sydney_water_after_rej, "Zero stock deduction on rejection violated!"
    print("6. Zero deduction on rejection VERIFIED.")

    # 7. Propose Disaster 2 for Approval
    payload_2 = {
        "incident_name": "Bushfire Front - Blue Mountains NSW",
        "disaster_type": "WILDFIRE",
        "region": "Blue Mountains",
        "affected_population": 15000,
        "displaced_population": 3500,
        "hazard_intensity": 0.80,
        "vulnerability_score": 0.55,
        "coping_capacity": 0.50,
        "infrastructure_damage": 0.65
    }
    req = urllib.request.Request(
        BASE_URL + "/api/disaster/propose",
        data=json.dumps(payload_2).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-User-Role": "EMERGENCY_OFFICER"}
    )
    res = urllib.request.urlopen(req, timeout=10)
    prop2 = json.loads(res.read().decode("utf-8"))
    inc2_id = prop2["incident_id"]
    print(f"7. Proposed {inc2_id}: Status={prop2['status']}")

    # 8. Approve Disaster 2 (LOGISTICS_DIRECTOR) -> Deducts inventory & publishes live SNS alert
    req_app = urllib.request.Request(
        f"{BASE_URL}/api/disaster/approve/{inc2_id}",
        data=json.dumps({"notes": "Approved for emergency deployment"}).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-User-Role": "LOGISTICS_DIRECTOR"}
    )
    res_app = urllib.request.urlopen(req_app, timeout=15)
    app2 = json.loads(res_app.read().decode("utf-8"))
    assert app2["status"] == "APPROVED_DISPATCHED"
    assert app2["inventory_updated"] is True
    print(f"8. Approved {inc2_id}: Status={app2['status']}")
    if app2.get("alert_result"):
        print(f"   Real AWS SNS Status: {app2['alert_result'].get('sns_publish_status')}, MsgId: {app2['alert_result'].get('message_id')}")

    # 9. Verify Stock Deduction Happened
    inv_res = urllib.request.urlopen(BASE_URL + "/api/inventory", timeout=10)
    inv_data = json.loads(inv_res.read().decode("utf-8"))
    sydney_water_after_app = next(
        s["quantity_available"]
        for s in inv_data["stock"]
        if s["warehouse_name"] == "Central Depot Sydney" and s["item_name"] == "Clean Drinking Water & Purification"
    )
    assert sydney_water_after_app < sydney_water_initial, "Stock was not deducted!"
    print(f"9. Stock deducted: {sydney_water_initial} -> {sydney_water_after_app}")

    # 10. Verify Duplicate Approval is Blocked (HTTP 400)
    try:
        urllib.request.urlopen(req_app, timeout=10)
        assert False, "Duplicate approval should have returned HTTP 400"
    except urllib.error.HTTPError as e:
        assert e.code == 400
        print(f"10. Duplicate approval correctly blocked with HTTP {e.code}.")

    # 11. Multi-Region Prioritization
    req_prio = urllib.request.Request(
        BASE_URL + "/api/disaster/prioritize-regions",
        data=json.dumps([payload_1, payload_2]).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res_prio = urllib.request.urlopen(req_prio, timeout=10)
    prio_data = json.loads(res_prio.read().decode("utf-8"))
    assert len(prio_data["ranked_regions"]) == 2
    print(f"11. Multi-Region Prioritization returned rankings. Top rank: {prio_data['ranked_regions'][0]['incident_name']}")

    # 12. Audit History
    hist_res = urllib.request.urlopen(BASE_URL + "/api/disaster/history", timeout=10)
    hist_data = json.loads(hist_res.read().decode("utf-8"))
    assert len(hist_data) >= 2
    print(f"12. Audit history verified. Total entries: {len(hist_data)}")

if __name__ == "__main__":
    test_live_ec2_e2e_workflow()
