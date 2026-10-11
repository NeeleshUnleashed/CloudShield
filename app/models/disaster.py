from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class DisasterType(str, Enum):
    FLOOD = "FLOOD"
    EARTHQUAKE = "EARTHQUAKE"
    WILDFIRE = "WILDFIRE"
    CYCLONE = "CYCLONE"
    LANDSLIDE = "LANDSLIDE"

class DisasterInput(BaseModel):
    incident_name: str = Field(..., description="Name or identifier for the incident", examples=["Cyclone Olivia - Coastal Region"])
    disaster_type: DisasterType = Field(..., description="Type of natural or environmental disaster")
    region: str = Field(..., description="Target affected zone or district", examples=["Northern Delta"])
    affected_population: int = Field(..., ge=1, description="Total estimated people impacted", examples=[15000])
    displaced_population: int = Field(..., ge=0, description="People evacuated or homeless", examples=[4500])
    hazard_intensity: float = Field(..., ge=0.1, le=1.0, description="Raw physical intensity of the disaster (0.1 to 1.0)", examples=[0.85])
    vulnerability_score: float = Field(0.5, ge=0.0, le=1.0, description="Demographic and socioeconomic vulnerability index (0.0 to 1.0)")
    coping_capacity: float = Field(0.5, ge=0.05, le=1.0, description="Local administrative & healthcare capacity (0.05 to 1.0)")
    infrastructure_damage: float = Field(0.5, ge=0.0, le=1.0, description="Road, water, and power grid disruption index (0.0 to 1.0)")
