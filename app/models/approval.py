from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.disaster import DisasterInput, DisasterType
from app.models.dpri import DPRIResult, RiskLevel
from app.models.allocation import DemandPrediction, AllocationRecommendation, SNSAlertPayload

class DemoRole(str, Enum):
    """
    Demo Role-Based Access Control (RBAC) tiers.
    NOTE: Demo role selection is for academic evaluation and demonstration;
    it is not a production-grade cryptographic identity provider.
    """
    EMERGENCY_OFFICER = "EMERGENCY_OFFICER"
    LOGISTICS_DIRECTOR = "LOGISTICS_DIRECTOR"
    AUDITOR = "AUDITOR"

class IncidentStatus(str, Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED_DISPATCHED = "APPROVED_DISPATCHED"
    REJECTED = "REJECTED"

class ProposalResponse(BaseModel):
    incident_id: str
    status: IncidentStatus
    incident_name: str
    region: str
    disaster_input: DisasterInput
    dpri_result: DPRIResult
    predicted_demand: DemandPrediction
    allocation_plan: AllocationRecommendation
    created_by_role: DemoRole
    inventory_updated: bool = False
    message: str = "Allocation proposal generated. Pending authorization from LOGISTICS_DIRECTOR."

class ApprovalRequest(BaseModel):
    notes: Optional[str] = "Approved after logistical evaluation"

class ApprovalResponse(BaseModel):
    incident_id: str
    status: IncidentStatus
    approved_by_role: DemoRole
    approved_at: str
    sns_alert: SNSAlertPayload
    inventory_updated: bool
    dispatched_items_count: int
    message: str = "Dispatch approved. Inventory successfully allocated and SNS alert broadcast."

class RejectionRequest(BaseModel):
    reason: str = "Allocation rejected by logistics authority"

class RejectionResponse(BaseModel):
    incident_id: str
    status: IncidentStatus
    rejected_by_role: DemoRole
    reason: str
    inventory_updated: bool = False
    message: str = "Proposal rejected. Zero inventory deducted."

# Multi-Region Prioritization Models
class RankedRegionItem(BaseModel):
    rank: int
    incident_name: str
    region: str
    disaster_type: DisasterType
    dpri_score: float
    risk_level: RiskLevel
    urgency_tier: str
    recommended_action: str

class MultiRegionPrioritizationResult(BaseModel):
    total_regions_evaluated: int
    critical_count: int
    high_count: int
    ranked_regions: List[RankedRegionItem]
    prioritization_rationale: str
