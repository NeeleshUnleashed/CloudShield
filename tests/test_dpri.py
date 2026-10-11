import pytest
from app.models.disaster import DisasterInput, DisasterType
from app.models.dpri import RiskLevel
from app.core.dpri_engine import calculate_dpri

def test_dpri_bounds_and_validity():
    """Verify that DPRI score is always strictly constrained within [0.0, 1.0]."""
    test_cases = [
        # Extreme minimums
        DisasterInput(
            incident_name="Minor Flare",
            disaster_type=DisasterType.LANDSLIDE,
            region="Rural Outpost",
            affected_population=100,
            displaced_population=5,
            hazard_intensity=0.1,
            vulnerability_score=0.0,
            coping_capacity=1.0,
            infrastructure_damage=0.0
        ),
        # Extreme maximums
        DisasterInput(
            incident_name="Catastrophic Quake",
            disaster_type=DisasterType.EARTHQUAKE,
            region="Metro Core",
            affected_population=100000,
            displaced_population=50000,
            hazard_intensity=1.0,
            vulnerability_score=1.0,
            coping_capacity=0.05,
            infrastructure_damage=1.0
        ),
    ]
    for case in test_cases:
        res = calculate_dpri(case)
        assert 0.0 <= res.dpri_score <= 1.0, f"Score out of bounds: {res.dpri_score}"
        assert res.risk_level in [RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.CRITICAL]

def test_dpri_low_risk_classification():
    low_incident = DisasterInput(
        incident_name="Minor Localized Flood",
        disaster_type=DisasterType.FLOOD,
        region="Well-drained valley",
        affected_population=500,
        displaced_population=20,
        hazard_intensity=0.15,
        vulnerability_score=0.1,
        coping_capacity=0.9,
        infrastructure_damage=0.05
    )
    result = calculate_dpri(low_incident)
    assert result.risk_level in [RiskLevel.LOW, RiskLevel.MODERATE]
    assert result.dpri_score < 0.45

def test_dpri_critical_risk_classification():
    catastrophic_incident = DisasterInput(
        incident_name="Severe Tropical Cyclone",
        disaster_type=DisasterType.CYCLONE,
        region="Exposed Coastal Belt",
        affected_population=50000,
        displaced_population=25000,
        hazard_intensity=0.95,
        vulnerability_score=0.9,
        coping_capacity=0.1,
        infrastructure_damage=0.9
    )
    result = calculate_dpri(catastrophic_incident)
    assert result.risk_level == RiskLevel.CRITICAL
    assert result.dpri_score >= 0.75
