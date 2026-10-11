import pytest
from app.models.disaster import DisasterInput, DisasterType
from app.models.inventory import SupplyCategory
from app.core.dpri_engine import calculate_dpri
from app.core.prediction_engine import predict_resource_demands

def test_prediction_output_categories():
    """Verify that all 5 critical humanitarian categories are forecasted."""
    disaster = DisasterInput(
        incident_name="Flood Delta",
        disaster_type=DisasterType.FLOOD,
        region="Delta Zone",
        affected_population=10000,
        displaced_population=3000,
        hazard_intensity=0.7,
        vulnerability_score=0.6,
        coping_capacity=0.4,
        infrastructure_damage=0.5
    )
    dpri = calculate_dpri(disaster)
    demand = predict_resource_demands(disaster, dpri)
    
    forecasted_categories = {item.category for item in demand.items}
    expected_categories = {
        SupplyCategory.WATER,
        SupplyCategory.FOOD,
        SupplyCategory.MEDICAL,
        SupplyCategory.SHELTER,
        SupplyCategory.POWER
    }
    assert forecasted_categories == expected_categories
    for item in demand.items:
        assert item.predicted_demand > 0
        assert isinstance(item.predicted_demand, int)

def test_prediction_monotonic_scaling():
    """Higher population and higher DPRI must forecast strictly greater demand."""
    small_disaster = DisasterInput(
        incident_name="Small Tremor",
        disaster_type=DisasterType.EARTHQUAKE,
        region="Town A",
        affected_population=1000,
        displaced_population=200,
        hazard_intensity=0.3,
        vulnerability_score=0.3,
        coping_capacity=0.8,
        infrastructure_damage=0.2
    )
    large_disaster = DisasterInput(
        incident_name="Major Quake",
        disaster_type=DisasterType.EARTHQUAKE,
        region="City B",
        affected_population=20000,
        displaced_population=8000,
        hazard_intensity=0.9,
        vulnerability_score=0.8,
        coping_capacity=0.2,
        infrastructure_damage=0.85
    )
    
    dpri_small = calculate_dpri(small_disaster)
    dpri_large = calculate_dpri(large_disaster)
    
    demand_small = predict_resource_demands(small_disaster, dpri_small)
    demand_large = predict_resource_demands(large_disaster, dpri_large)
    
    small_map = {i.category: i.predicted_demand for i in demand_small.items}
    large_map = {i.category: i.predicted_demand for i in demand_large.items}
    
    for cat in small_map:
        assert large_map[cat] > small_map[cat], f"Demand did not scale for category {cat}"
