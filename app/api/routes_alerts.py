from fastapi import APIRouter
from typing import List, Dict, Any
from app.db.database import get_connection

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

@router.get("", response_model=List[Dict[str, Any]])
def get_alerts():
    """Returns log of simulated SNS emergency alerts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT message_id, incident_id, topic_arn, subject, message, severity, timestamp
        FROM notifications_log
        ORDER BY timestamp DESC;
    """)
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows
