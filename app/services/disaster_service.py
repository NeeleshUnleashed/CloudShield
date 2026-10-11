import json
import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import HTTPException, status

from app.db.database import get_connection
from app.models.disaster import DisasterInput, DisasterType
from app.models.dpri import DPRIResult, RiskLevel
from app.models.allocation import (
    AllocationRecommendation, WorkflowExecutionResult, DemandPrediction
)
from app.models.approval import (
    DemoRole, IncidentStatus, ProposalResponse, ApprovalResponse, RejectionResponse,
    RankedRegionItem, MultiRegionPrioritizationResult
)
from app.core.dpri_engine import calculate_dpri
from app.core.prediction_engine import predict_resource_demands
from app.core.allocation_engine import calculate_shortages_and_allocation, CATEGORY_TO_ITEM_ID
from app.core.notification_engine import dispatch_simulated_sns_alert

def propose_disaster_plan(
    disaster: DisasterInput,
    created_by_role: DemoRole = DemoRole.EMERGENCY_OFFICER
) -> ProposalResponse:
    """
    Step 1 of Human-in-the-Loop workflow:
    Calculates DPRI, predicts demand, and calculates proposed depot allocation.
    PERSISTS PROPOSAL WITH STATUS 'PENDING_APPROVAL'.
    ZERO INVENTORY IS DEDUCTED AND ZERO NOTIFICATIONS ARE SENT.
    """
    incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
    
    dpri = calculate_dpri(disaster)
    demand = predict_resource_demands(disaster, dpri)
    allocation = calculate_shortages_and_allocation(disaster, dpri, demand)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    allocation_json = allocation.model_dump_json()
    
    cursor.execute("""
        INSERT INTO disaster_logs (
            incident_id, incident_name, disaster_type, region,
            affected_population, displaced_population, dpri_score, risk_level,
            status, created_by_role, proposed_allocation_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PENDING_APPROVAL', ?, ?);
    """, (
        incident_id,
        disaster.incident_name,
        disaster.disaster_type.value,
        disaster.region,
        disaster.affected_population,
        disaster.displaced_population,
        dpri.dpri_score,
        dpri.risk_level.value,
        created_by_role.value,
        allocation_json
    ))
    conn.commit()
    conn.close()
    
    return ProposalResponse(
        incident_id=incident_id,
        status=IncidentStatus.PENDING_APPROVAL,
        incident_name=disaster.incident_name,
        region=disaster.region,
        disaster_input=disaster,
        dpri_result=dpri,
        predicted_demand=demand,
        allocation_plan=allocation,
        created_by_role=created_by_role,
        inventory_updated=False,
        message="Allocation proposal generated. Pending authorization from LOGISTICS_DIRECTOR."
    )

def approve_dispatch_plan(
    incident_id: str,
    approved_by_role: DemoRole = DemoRole.LOGISTICS_DIRECTOR,
    notes: Optional[str] = None
) -> ApprovalResponse:
    """
    Step 2 of Human-in-the-Loop workflow:
    Authorizes a pending proposal, atomically deducts stock from SQLite,
    records dispatch manifests, and dispatches the simulated SNS alert.
    PREVENTS DUPLICATE APPROVALS.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT incident_id, incident_name, disaster_type, region,
               dpri_score, risk_level, status, proposed_allocation_json
        FROM disaster_logs
        WHERE incident_id = ?;
    """, (incident_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disaster incident '{incident_id}' not found."
        )
        
    current_status = row["status"]
    if current_status == IncidentStatus.APPROVED_DISPATCHED.value:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Duplicate approval rejected: Incident '{incident_id}' is already APPROVED and dispatched."
        )
        
    if current_status == IncidentStatus.REJECTED.value:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve incident '{incident_id}' because it has been REJECTED."
        )

    # Deserialize planned allocation
    raw_json = row["proposed_allocation_json"]
    if not raw_json:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Corrupted incident: Proposed allocation plan payload is missing."
        )
    
    allocation_dict = json.loads(raw_json)
    allocation = AllocationRecommendation(**allocation_dict)
    
    # Reconstruct DPRI Result for notification
    dpri = DPRIResult(
        dpri_score=row["dpri_score"],
        risk_level=RiskLevel(row["risk_level"]),
        hazard_component=0.8,
        vulnerability_component=1.0,
        coping_deficit=0.5,
        infrastructure_penalty=1.0,
        explanation=f"Authorized incident {row['incident_name']}"
    )

    # Transactional stock deduction and manifest logging
    dispatched_count = 0
    now_iso = datetime.now(timezone.utc).isoformat()
    
    try:
        for item in allocation.dispatch_plan:
            dispatch_id = f"DSP-{uuid.uuid4().hex[:8].upper()}"
            item_id = CATEGORY_TO_ITEM_ID.get(item.category, "ITEM-WATER")
            
            # Check availability first to ensure sufficient stock
            cursor.execute("""
                SELECT quantity_available FROM warehouse_stock
                WHERE warehouse_id = ? AND item_id = ?;
            """, (item.warehouse_id, item_id))
            stock_row = cursor.fetchone()
            available = stock_row["quantity_available"] if stock_row else 0
            
            actual_dispatch = min(item.dispatched_quantity, available)
            if actual_dispatch > 0:
                cursor.execute("""
                    INSERT INTO dispatch_manifests (
                        dispatch_id, incident_id, warehouse_id, item_id, quantity_dispatched, status
                    ) VALUES (?, ?, ?, ?, ?, 'DISPATCHED_CONFIRMED');
                """, (dispatch_id, incident_id, item.warehouse_id, item_id, actual_dispatch))
                
                cursor.execute("""
                    UPDATE warehouse_stock
                    SET quantity_available = quantity_available - ?
                    WHERE warehouse_id = ? AND item_id = ?;
                """, (actual_dispatch, item.warehouse_id, item_id))
                dispatched_count += actual_dispatch

        # Mark incident as APPROVED_DISPATCHED
        cursor.execute("""
            UPDATE disaster_logs
            SET status = 'APPROVED_DISPATCHED',
                approved_by_role = ?,
                approved_at = ?
            WHERE incident_id = ?;
        """, (approved_by_role.value, now_iso, incident_id))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transactional dispatch failed: {str(e)}"
        )
    finally:
        conn.close()

    # Trigger simulated SNS alert
    sns_alert = dispatch_simulated_sns_alert(
        incident_id=incident_id,
        incident_name=row["incident_name"],
        region=row["region"],
        dpri=dpri,
        allocation=allocation
    )

    return ApprovalResponse(
        incident_id=incident_id,
        status=IncidentStatus.APPROVED_DISPATCHED,
        approved_by_role=approved_by_role,
        approved_at=now_iso,
        sns_alert=sns_alert,
        inventory_updated=True,
        dispatched_items_count=dispatched_count,
        message=f"Dispatch approved by {approved_by_role.value}. {dispatched_count} units dispatched and SNS alert broadcast."
    )

def reject_dispatch_plan(
    incident_id: str,
    rejected_by_role: DemoRole = DemoRole.LOGISTICS_DIRECTOR,
    reason: str = "Allocation plan rejected by logistics authority"
) -> RejectionResponse:
    """
    Rejects a pending disaster proposal.
    ZERO INVENTORY IS DEDUCTED.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT incident_id, status FROM disaster_logs WHERE incident_id = ?;", (incident_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Disaster incident '{incident_id}' not found."
        )
        
    current_status = row["status"]
    if current_status == IncidentStatus.APPROVED_DISPATCHED.value:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject incident '{incident_id}': Already approved and dispatched."
        )
        
    if current_status == IncidentStatus.REJECTED.value:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Incident '{incident_id}' is already REJECTED."
        )
        
    cursor.execute("""
        UPDATE disaster_logs
        SET status = 'REJECTED',
            approved_by_role = ?,
            rejection_reason = ?,
            approved_at = ?
        WHERE incident_id = ?;
    """, (rejected_by_role.value, reason, datetime.now(timezone.utc).isoformat(), incident_id))
    conn.commit()
    conn.close()
    
    return RejectionResponse(
        incident_id=incident_id,
        status=IncidentStatus.REJECTED,
        rejected_by_role=rejected_by_role,
        reason=reason,
        inventory_updated=False,
        message="Proposal rejected. Zero inventory deducted."
    )

def prioritize_multiple_regions(incidents: List[DisasterInput]) -> MultiRegionPrioritizationResult:
    """
    Multi-Region DPRI Prioritization:
    Evaluates a batch of regional disaster inputs, computes DPRI for each,
    and ranks them from highest severity to lowest to prioritize relief allocation.
    """
    if not incidents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incident list cannot be empty.")
        
    scored_regions = []
    for inc in incidents:
        dpri = calculate_dpri(inc)
        scored_regions.append((inc, dpri))
        
    # Sort descending by DPRI score
    scored_regions.sort(key=lambda x: x[1].dpri_score, reverse=True)
    
    ranked_items: List[RankedRegionItem] = []
    critical_count = 0
    high_count = 0
    
    for rank_idx, (inc, dpri) in enumerate(scored_regions, start=1):
        if dpri.risk_level == RiskLevel.CRITICAL:
            urgency = "Tier-1 Immediate Airlift & Deployment"
            critical_count += 1
            action = "Dispatch immediate maximum available relief stock; activate national mutual aid."
        elif dpri.risk_level == RiskLevel.HIGH:
            urgency = "Tier-2 Secondary Ground Logistics Dispatch"
            high_count += 1
            action = "Dispatch secondary regional reserves within 6-12 hours."
        elif dpri.risk_level == RiskLevel.MODERATE:
            urgency = "Tier-3 Municipal Preparedness Reserve"
            action = "Monitor situation; prepare stage-1 relief packs."
        else:
            urgency = "Tier-4 Local Standard Monitoring"
            action = "Local municipal handling sufficient."
            
        ranked_items.append(
            RankedRegionItem(
                rank=rank_idx,
                incident_name=inc.incident_name,
                region=inc.region,
                disaster_type=inc.disaster_type,
                dpri_score=dpri.dpri_score,
                risk_level=dpri.risk_level,
                urgency_tier=urgency,
                recommended_action=action
            )
        )
        
    rationale = (
        f"Evaluated {len(incidents)} regions. Ranked by acute vulnerability and coping deficit. "
        f"Top Priority: {ranked_items[0].region} (DPRI: {ranked_items[0].dpri_score:.4f}, {ranked_items[0].risk_level.value})."
    )
    
    return MultiRegionPrioritizationResult(
        total_regions_evaluated=len(incidents),
        critical_count=critical_count,
        high_count=high_count,
        ranked_regions=ranked_items,
        prioritization_rationale=rationale
    )

def execute_disaster_workflow(disaster: DisasterInput) -> WorkflowExecutionResult:
    """
    Combined End-to-End Workflow:
    Executes proposal + auto-approval for seamless backwards compatibility with existing test suites.
    """
    proposal = propose_disaster_plan(disaster, created_by_role=DemoRole.EMERGENCY_OFFICER)
    approval = approve_dispatch_plan(proposal.incident_id, approved_by_role=DemoRole.LOGISTICS_DIRECTOR)
    
    return WorkflowExecutionResult(
        execution_id=proposal.incident_id,
        status="SUCCESS",
        disaster_input=disaster,
        dpri_result=proposal.dpri_result,
        predicted_demand=proposal.predicted_demand,
        allocation_plan=proposal.allocation_plan,
        sns_alert=approval.sns_alert,
        inventory_updated=approval.inventory_updated
    )
