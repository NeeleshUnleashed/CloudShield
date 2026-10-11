from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from app.models.inventory import SupplyCategory
from app.models.dpri import DPRIResult
from app.models.disaster import DisasterInput

class DemandItem(BaseModel):
    category: SupplyCategory
    item_name: str
    unit: str
    predicted_demand: int

class DemandPrediction(BaseModel):
    incident_name: str
    items: List[DemandItem]
    methodology: str = "Trained Regression Heuristic (DPRI + Affected/Displaced Population Scaling)"

class ShortageItem(BaseModel):
    category: SupplyCategory
    item_name: str
    demanded: int
    available_network_stock: int
    shortage_quantity: int
    fulfilled_quantity: int
    fulfillment_percentage: float

class DispatchPlanItem(BaseModel):
    warehouse_id: str
    warehouse_name: str
    category: SupplyCategory
    item_name: str
    dispatched_quantity: int
    unit: str

class AllocationRecommendation(BaseModel):
    incident_name: str
    target_region: str
    dpri_score: float
    total_demanded_units: int
    total_allocated_units: int
    total_shortage_units: int
    overall_fulfillment_rate: float
    dispatch_plan: List[DispatchPlanItem]
    shortage_breakdown: List[ShortageItem]

class SNSAlertPayload(BaseModel):
    simulated: bool = True
    topic_arn: str
    subject: str
    message_id: str
    timestamp: str
    severity: str
    message: str
    sns_publish_status: str

class WorkflowExecutionResult(BaseModel):
    execution_id: str
    status: str = "SUCCESS"
    disaster_input: DisasterInput
    dpri_result: DPRIResult
    predicted_demand: DemandPrediction
    allocation_plan: AllocationRecommendation
    sns_alert: SNSAlertPayload
    inventory_updated: bool
