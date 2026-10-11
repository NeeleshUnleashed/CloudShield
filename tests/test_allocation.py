import pytest
from app.db.seed_data import seed_database
from app.models.disaster import DisasterInput, DisasterType
from app.core.dpri_engine import calculate_dpri
from app.core.prediction_engine import predict_resource_demands
from app.core.allocation_engine import calculate_shortages_and_allocation
from app.core.notification_engine import dispatch_simulated_sns_alert

@pytest.fixture(autouse=True)
def setup_db():
    seed_database(force_reset=True)

def test_allocation_and_shortage_calculation():
    """Verify shortage identification and dispatch plan generation."""
    disaster = DisasterInput(
        incident_name="Queensland Cyclone",
        disaster_type=DisasterType.CYCLONE,
        region="Cairns Coast",
        affected_population=12000,
        displaced_population=4000,
        hazard_intensity=0.8,
        vulnerability_score=0.6,
        coping_capacity=0.5,
        infrastructure_damage=0.6
    )
    dpri = calculate_dpri(disaster)
    demand = predict_resource_demands(disaster, dpri)
    allocation = calculate_shortages_and_allocation(disaster, dpri, demand)
    
    assert allocation.total_demanded_units > 0
    assert allocation.total_allocated_units > 0
    assert allocation.overall_fulfillment_rate > 0.0
    assert len(allocation.dispatch_plan) > 0
    assert len(allocation.shortage_breakdown) == 5
    
    # Check that dispatch plan sum matches total allocated units
    dispatched_sum = sum(p.dispatched_quantity for p in allocation.dispatch_plan)
    assert dispatched_sum == allocation.total_allocated_units

def test_simulated_sns_alert_generation():
    """Verify simulated SNS notification generation and audit payload."""
    disaster = DisasterInput(
        incident_name="Victorian Bushfire",
        disaster_type=DisasterType.WILDFIRE,
        region="East Gippsland",
        affected_population=8000,
        displaced_population=2500,
        hazard_intensity=0.75,
        vulnerability_score=0.5,
        coping_capacity=0.6,
        infrastructure_damage=0.5
    )
    dpri = calculate_dpri(disaster)
    demand = predict_resource_demands(disaster, dpri)
    allocation = calculate_shortages_and_allocation(disaster, dpri, demand)
    
    alert = dispatch_simulated_sns_alert("INC-TEST-01", disaster.incident_name, disaster.region, dpri, allocation)
    assert alert.simulated is True
    assert alert.message_id.startswith("mock-msg-")
    assert "CloudShield-Disaster-Alerts" in alert.topic_arn
    assert alert.sns_publish_status == "SIMULATED_PUBLISHED_200"
    assert "Victorian Bushfire" in alert.message
