import math
import numpy as np
from app.models.disaster import DisasterInput, DisasterType
from app.models.dpri import DPRIResult
from app.models.inventory import SupplyCategory
from app.models.allocation import DemandPrediction, DemandItem

# Domain-specific baseline multipliers per person per disaster type
DISASTER_TYPE_COEFFICIENTS = {
    DisasterType.FLOOD: {
        SupplyCategory.WATER: 4.5,     # Water contaminated in floods
        SupplyCategory.FOOD: 1.8,
        SupplyCategory.MEDICAL: 0.08,
        SupplyCategory.SHELTER: 0.22,
        SupplyCategory.POWER: 0.005,
    },
    DisasterType.EARTHQUAKE: {
        SupplyCategory.WATER: 3.5,
        SupplyCategory.FOOD: 1.5,
        SupplyCategory.MEDICAL: 0.18,   # High trauma injuries
        SupplyCategory.SHELTER: 0.28,   # High home destruction
        SupplyCategory.POWER: 0.008,
    },
    DisasterType.CYCLONE: {
        SupplyCategory.WATER: 4.0,
        SupplyCategory.FOOD: 1.7,
        SupplyCategory.MEDICAL: 0.12,
        SupplyCategory.SHELTER: 0.25,
        SupplyCategory.POWER: 0.007,
    },
    DisasterType.WILDFIRE: {
        SupplyCategory.WATER: 5.0,
        SupplyCategory.FOOD: 1.4,
        SupplyCategory.MEDICAL: 0.14,   # Burns & smoke inhalation
        SupplyCategory.SHELTER: 0.20,
        SupplyCategory.POWER: 0.004,
    },
    DisasterType.LANDSLIDE: {
        SupplyCategory.WATER: 3.0,
        SupplyCategory.FOOD: 1.3,
        SupplyCategory.MEDICAL: 0.15,
        SupplyCategory.SHELTER: 0.18,
        SupplyCategory.POWER: 0.003,
    },
}

ITEM_METADATA = {
    SupplyCategory.WATER: ("Clean Drinking Water & Purification", "liters"),
    SupplyCategory.FOOD: ("Emergency Ready-to-Eat Food Rations", "ration packs"),
    SupplyCategory.MEDICAL: ("Emergency Trauma & First-Aid Kits", "kits"),
    SupplyCategory.SHELTER: ("All-Weather Family Shelter Tents", "tents"),
    SupplyCategory.POWER: ("Mobile Emergency Power Generators", "units"),
}

def predict_resource_demands(disaster: DisasterInput, dpri: DPRIResult) -> DemandPrediction:
    """
    Predicts relief supplies needed based on affected/displaced population,
    disaster type dynamics, and the computed DPRI severity multiplier.
    
    Formula:
      Demand = Base_Coefficient * (Affected_Pop * 0.4 + Displaced_Pop * 0.6) * (1 + DPRI_Score)
    """
    coeffs = DISASTER_TYPE_COEFFICIENTS.get(disaster.disaster_type, DISASTER_TYPE_COEFFICIENTS[DisasterType.FLOOD])
    
    # Effective weighted population under direct acute need
    effective_pop = (disaster.affected_population * 0.35) + (disaster.displaced_population * 0.65)
    
    # DPRI scaling factor (amplifies demand for critical zones)
    dpri_amplifier = 0.8 + (1.2 * dpri.dpri_score)
    
    items = []
    for cat, base_rate in coeffs.items():
        raw_quantity = base_rate * effective_pop * dpri_amplifier
        
        # Round up to sensible integer units
        predicted_quantity = max(10, int(math.ceil(raw_quantity)))
        
        item_name, unit = ITEM_METADATA[cat]
        items.append(
            DemandItem(
                category=cat,
                item_name=item_name,
                unit=unit,
                predicted_demand=predicted_quantity
            )
        )
        
    return DemandPrediction(
        incident_name=disaster.incident_name,
        items=items,
        methodology="Calibrated Humanitarian Sphere Model with DPRI Severity Amplification"
    )
