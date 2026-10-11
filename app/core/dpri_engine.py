from app.models.disaster import DisasterInput, DisasterType
from app.models.dpri import DPRIResult, RiskLevel

# Type-specific impact multipliers reflecting systemic lethality & infrastructure shock
DISASTER_TYPE_MULTIPLIERS = {
    DisasterType.EARTHQUAKE: 1.25,
    DisasterType.CYCLONE: 1.15,
    DisasterType.FLOOD: 1.10,
    DisasterType.WILDFIRE: 1.05,
    DisasterType.LANDSLIDE: 1.00,
}

def calculate_dpri(disaster: DisasterInput) -> DPRIResult:
    """
    Computes the Disaster Preparedness and Response Index (DPRI).
    
    Mathematical Formulation:
      DPRI = min(1.0, max(0.0, (Hazard_Eff * Vulnerability_Factor * Coping_Deficit * Infra_Multiplier) / Normalization_Constant))
      
    Guaranteed bounds: [0.0, 1.0]
    Risk Thresholds:
      - [0.00, 0.30): LOW
      - [0.30, 0.55): MODERATE
      - [0.55, 0.75): HIGH
      - [0.75, 1.00]: CRITICAL
    """
    type_mult = DISASTER_TYPE_MULTIPLIERS.get(disaster.disaster_type, 1.0)
    effective_hazard = disaster.hazard_intensity * type_mult
    
    # Vulnerability factor: ranges from 0.75 to 1.50
    vulnerability_factor = 0.75 + (0.75 * disaster.vulnerability_score)
    
    # Coping deficit: high coping capacity -> low deficit (ranges from 0.25 to 1.15)
    coping_deficit = 1.20 - (0.95 * disaster.coping_capacity)
    
    # Infrastructure penalty: ranges from 1.00 to 1.40
    infra_penalty = 1.00 + (0.40 * disaster.infrastructure_damage)
    
    # Raw aggregate
    raw_score = (effective_hazard * vulnerability_factor * coping_deficit * infra_penalty)
    
    # Normalize with calibrated constant (approx max possible ~2.1)
    normalized_score = round(min(1.0, max(0.0, raw_score / 2.05)), 4)
    
    # Categorical classification
    if normalized_score < 0.30:
        risk_level = RiskLevel.LOW
    elif normalized_score < 0.55:
        risk_level = RiskLevel.MODERATE
    elif normalized_score < 0.75:
        risk_level = RiskLevel.HIGH
    else:
        risk_level = RiskLevel.CRITICAL
        
    explanation = (
        f"DPRI calculated at {normalized_score:.4f} ({risk_level.value}). "
        f"Hazard Contribution: {effective_hazard:.2f}, Vulnerability Weight: {vulnerability_factor:.2f}, "
        f"Coping Deficit: {coping_deficit:.2f}, Infrastructure Logistics Disruption: {infra_penalty:.2f}."
    )
    
    return DPRIResult(
        dpri_score=normalized_score,
        risk_level=risk_level,
        hazard_component=round(effective_hazard, 4),
        vulnerability_component=round(vulnerability_factor, 4),
        coping_deficit=round(coping_deficit, 4),
        infrastructure_penalty=round(infra_penalty, 4),
        explanation=explanation
    )
