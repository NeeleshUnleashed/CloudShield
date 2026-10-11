import uuid
from datetime import datetime, timezone
from typing import Dict, Any
from app.config import settings
from app.db.database import get_connection
from app.adapters.base import BaseNotificationAdapter

class MockSNSNotificationAdapter(BaseNotificationAdapter):
    """
    Local mock adapter simulating Amazon SNS emergency broadcast alerts.
    Operates strictly offline without making live AWS API calls or incurring charges.
    """
    
    def send_alert(
        self,
        incident_id: str,
        subject: str,
        message: str,
        severity: str,
        topic_arn: str
    ) -> Dict[str, Any]:
        message_id = f"mock-msg-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Persist alert to local database
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notifications_log (message_id, incident_id, topic_arn, subject, message, severity, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (message_id, incident_id, topic_arn, subject, message, severity, timestamp))
        conn.commit()
        conn.close()
        
        # Append to rotating local disk log
        log_file = settings.LOGS_DIR / "sns_simulated_alerts.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"\n--- [{timestamp}] SNS TOPIC: {topic_arn} ---\n")
            f.write(f"Subject: {subject}\nMessage-ID: {message_id}\nSeverity: {severity}\n{message}\n")
            
        return {
            "simulated": True,
            "topic_arn": topic_arn,
            "subject": subject,
            "message_id": message_id,
            "timestamp": timestamp,
            "severity": severity,
            "message": message,
            "sns_publish_status": "SIMULATED_PUBLISHED_200"
        }

class LiveSNSNotificationAdapter(BaseNotificationAdapter):
    """
    Production AWS SNS adapter.
    Guarded by AWS Zero-Unexpected-Charges policy: forbidden unless AWS_MODE=live is explicitly approved.
    """
    
    def send_alert(
        self,
        incident_id: str,
        subject: str,
        message: str,
        severity: str,
        topic_arn: str
    ) -> Dict[str, Any]:
        if settings.AWS_MODE != "live":
            raise RuntimeError(
                "CRITICAL POLICY VIOLATION: Live SNS adapter invoked while AWS_MODE=mock. "
                "Live AWS operations require explicit user approval and AWS_MODE=live."
            )
        try:
            import boto3
            client = boto3.client("sns", region_name=settings.AWS_REGION)
            response = client.publish(
                TopicArn=topic_arn,
                Subject=subject[:100],  # SNS subject 100 char limit
                Message=message
            )
            return {
                "simulated": False,
                "topic_arn": topic_arn,
                "subject": subject,
                "message_id": response["MessageId"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "severity": severity,
                "message": message,
                "sns_publish_status": "AWS_SNS_PUBLISHED_200"
            }
        except Exception as e:
            raise RuntimeError(f"Live AWS SNS publication failed: {str(e)}")

def get_notification_adapter() -> BaseNotificationAdapter:
    """Factory function returning the active notification adapter based on AWS_MODE."""
    if settings.AWS_MODE == "live":
        return LiveSNSNotificationAdapter()
    return MockSNSNotificationAdapter()
