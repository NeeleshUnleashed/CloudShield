from enum import Enum
from pydantic import BaseModel, Field

class RiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class DPRIResult(BaseModel):
    dpri_score: float = Field(..., ge=0.0, le=1.0, description="Overall Disaster Preparedness and Response Index (0.0 - 1.0)")
    risk_level: RiskLevel = Field(..., description="Categorical risk classification")
    hazard_component: float = Field(..., description="Normalized physical hazard contribution")
    vulnerability_component: float = Field(..., description="Demographic exposure and fragility weight")
    coping_deficit: float = Field(..., description="Inverse coping ability score")
    infrastructure_penalty: float = Field(..., description="Multiplier representing logistic disruption")
    explanation: str = Field(..., description="Human-readable breakdown of the score")
