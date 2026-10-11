from app.config import settings
from app.models.allocation import AllocationRecommendation, SNSAlertPayload
from app.models.dpri import DPRIResult
from app.adapters.notification import get_notification_adapter

SNS_MOCK_TOPIC_ARN = f"arn:aws:sns:{settings.AWS_REGION}:206238482111:CloudShield-Disaster-Alerts"

def dispatch_simulated_sns_alert(
    incident_id: str,
    incident_name: str,
    region: str,
    dpri: DPRIResult,
    allocation: AllocationRecommendation
) -> SNSAlertPayload:
    """
    Dispatches a structured emergency alert via the active notification adapter.
    In AWS_MODE=mock, the MockSNSNotificationAdapter persists and logs the event offline.
    """
    subject = f"[CLOUDSHIELD ALERT] {dpri.risk_level.value} Emergency: {incident_name} ({region})"
    
    shortages_text = ""
    if allocation.total_shortage_units > 0:
        shortages_text = "\n⚠️ CRITICAL SHORTAGES DETECTED:\n" + "\n".join(
            f"  - {s.item_name}: Shortfall of {s.shortage_quantity} {s.category.value} units ({s.fulfillment_percentage}% fulfilled)"
            for s in allocation.shortage_breakdown if s.shortage_quantity > 0
        )
    else:
        shortages_text = "\n✅ All requested relief items 100% fulfilled by depot network."

    body = (
        f"CLOUDSHIELD EMERGENCY DISPATCH ORDER\n"
        f"====================================\n"
        f"Incident: {incident_name}\n"
        f"Target Region: {region}\n"
        f"DPRI Score: {dpri.dpri_score:.4f} [{dpri.risk_level.value}]\n"
        f"Total Units Dispatched: {allocation.total_allocated_units}\n"
        f"Overall Network Fulfillment: {allocation.overall_fulfillment_rate}%\n"
        f"{shortages_text}\n"
        f"Mode: {'SIMULATED (AWS_MODE=mock)' if settings.AWS_MODE == 'mock' else 'LIVE AWS'} | Zero Charges Incurred\n"
    )
    
    adapter = get_notification_adapter()
    result = adapter.send_alert(
        incident_id=incident_id,
        subject=subject,
        message=body,
        severity=dpri.risk_level.value,
        topic_arn=SNS_MOCK_TOPIC_ARN
    )
    
    return SNSAlertPayload(**result)
