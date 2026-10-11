import pytest
from app.db.seed_data import seed_database
from app.models.disaster import DisasterInput, DisasterType
from app.services.disaster_service import execute_disaster_workflow
from app.services.inventory_service import get_inventory_summary

@pytest.fixture(autouse=True)
def setup_db():
    seed_database(force_reset=True)

def test_full_7_step_workflow():
    """
    Executes and validates the complete end-to-end 7-step pipeline:
      1. Disaster Input
      2. DPRI Calculation
      3. Resource-Demand Prediction
      4. Shortage Calculation
      5. Resource Allocation Recommendation
      6. Simulated SNS Alert
      7. Inventory Update
    """
    initial_inv = get_inventory_summary()
    initial_total_stock = sum(s.quantity_available for s in initial_inv.stock)
    
    disaster = DisasterInput(
        incident_name="Operation Southern Storm",
        disaster_type=DisasterType.CYCLONE,
        region="Illawarra Coast",
        affected_population=15000,
        displaced_population=5000,
        hazard_intensity=0.82,
        vulnerability_score=0.65,
        coping_capacity=0.45,
        infrastructure_damage=0.70
    )
    
    result = execute_disaster_workflow(disaster)
    
    # 1. Check Execution ID & Status
    assert result.status == "SUCCESS"
    assert result.execution_id.startswith("INC-")
    
    # 2. Check DPRI calculation
    assert 0.0 <= result.dpri_result.dpri_score <= 1.0
    assert result.dpri_result.risk_level.value in ["HIGH", "CRITICAL"]
    
    # 3. Check Resource-Demand Prediction
    assert len(result.predicted_demand.items) == 5
    for item in result.predicted_demand.items:
        assert item.predicted_demand > 0
        
    # 4 & 5. Check Shortage and Allocation
    assert result.allocation_plan.total_allocated_units > 0
    assert len(result.allocation_plan.dispatch_plan) > 0
    
    # 6. Check Simulated SNS Alert
    assert result.sns_alert.simulated is True
    assert result.sns_alert.sns_publish_status == "SIMULATED_PUBLISHED_200"
    assert "Southern Storm" in result.sns_alert.subject
    
    # 7. Check Inventory Update
    assert result.inventory_updated is True
    updated_inv = get_inventory_summary()
    updated_total_stock = sum(s.quantity_available for s in updated_inv.stock)
    
    # Inventory must have been decremented by the exact allocated amount
    expected_remaining = initial_total_stock - result.allocation_plan.total_allocated_units
    assert updated_total_stock == expected_remaining
