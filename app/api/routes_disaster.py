from fastapi import APIRouter, HTTPException, Depends, Query, Header
from typing import List, Dict, Any, Optional
from app.models.disaster import DisasterInput
from app.models.dpri import DPRIResult
from app.models.allocation import DemandPrediction, WorkflowExecutionResult
from app.models.approval import (
    DemoRole, ProposalResponse, ApprovalRequest, ApprovalResponse,
    RejectionRequest, RejectionResponse, MultiRegionPrioritizationResult
)
from app.core.dpri_engine import calculate_dpri
from app.core.prediction_engine import predict_resource_demands
from app.core.security import get_current_role, require_roles
from app.services.disaster_service import (
    propose_disaster_plan, approve_dispatch_plan, reject_dispatch_plan,
    prioritize_multiple_regions, execute_disaster_workflow
)
from app.db.database import get_connection

router = APIRouter(prefix="/api/disaster", tags=["Disaster"])

@router.post("/propose", response_model=ProposalResponse)
def propose_disaster_endpoint(
    disaster: DisasterInput,
    current_role: DemoRole = Depends(get_current_role)
):
    """
    Step 1: Ingests disaster input, calculates DPRI, predicts demand, and proposes allocation.
    STATUS: PENDING_APPROVAL. Zero inventory is deducted.
    RBAC: EMERGENCY_OFFICER, LOGISTICS_DIRECTOR (AUDITOR denied).
    """
    require_roles([DemoRole.EMERGENCY_OFFICER, DemoRole.LOGISTICS_DIRECTOR], current_role)
    return propose_disaster_plan(disaster, created_by_role=current_role)

@router.post("/approve/{incident_id}", response_model=ApprovalResponse)
def approve_dispatch_endpoint(
    incident_id: str,
    body: Optional[ApprovalRequest] = None,
    current_role: DemoRole = Depends(get_current_role)
):
    """
    Step 2: Human-in-the-Loop Approval.
    Authorizes allocation, deducts inventory, and sends simulated SNS broadcast.
    RBAC: LOGISTICS_DIRECTOR only (EMERGENCY_OFFICER and AUDITOR denied).
    PREVENTS DUPLICATE APPROVALS.
    """
    require_roles([DemoRole.LOGISTICS_DIRECTOR], current_role)
    notes = body.notes if body else "Approved by Logistics Authority"
    return approve_dispatch_plan(incident_id, approved_by_role=current_role, notes=notes)

@router.post("/reject/{incident_id}", response_model=RejectionResponse)
def reject_dispatch_endpoint(
    incident_id: str,
    body: Optional[RejectionRequest] = None,
    current_role: DemoRole = Depends(get_current_role)
):
    """
    Rejects a pending disaster proposal. Zero inventory is deducted.
    RBAC: LOGISTICS_DIRECTOR only.
    """
    require_roles([DemoRole.LOGISTICS_DIRECTOR], current_role)
    reason = body.reason if body else "Rejected by logistics authority"
    return reject_dispatch_plan(incident_id, rejected_by_role=current_role, reason=reason)

@router.post("/prioritize-regions", response_model=MultiRegionPrioritizationResult)
def prioritize_regions_endpoint(incidents: List[DisasterInput]):
    """
    Multi-Region Prioritization:
    Ingests multiple concurrent regional disaster reports, computes DPRI for each,
    and returns a priority-ranked dispatch schedule.
    """
    return prioritize_multiple_regions(incidents)

@router.post("/workflow", response_model=WorkflowExecutionResult)
def run_workflow_endpoint(disaster: DisasterInput):
    """
    Combined End-to-End Workflow (Propose + Auto-Approve).
    Preserved for backward-compatible automated tests and single-click execution.
    """
    try:
        return execute_disaster_workflow(disaster)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")

@router.post("/dpri", response_model=DPRIResult)
def calculate_dpri_endpoint(disaster: DisasterInput):
    """Calculates DPRI score and risk classification."""
    return calculate_dpri(disaster)

@router.post("/predict", response_model=DemandPrediction)
def predict_demands_endpoint(disaster: DisasterInput):
    """Calculates predicted relief supply demand."""
    dpri = calculate_dpri(disaster)
    return predict_resource_demands(disaster, dpri)

@router.get("/history")
def get_incident_history():
    """Returns complete audit history of disaster incidents and their approval status."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT incident_id, incident_name, disaster_type, region,
               affected_population, displaced_population, dpri_score, risk_level,
               status, created_by_role, approved_by_role, approved_at, rejection_reason, created_at
        FROM disaster_logs
        ORDER BY created_at DESC;
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows
