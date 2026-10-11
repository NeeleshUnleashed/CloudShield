import pytest
from app.config import settings
from app.adapters.notification import (
    MockSNSNotificationAdapter, LiveSNSNotificationAdapter, get_notification_adapter
)
from app.adapters.storage import (
    LocalStorageAdapter, S3StorageAdapter, get_storage_adapter
)

def test_mock_notification_adapter():
    """Verify mock SNS adapter generates simulated payloads offline."""
    adapter = MockSNSNotificationAdapter()
    res = adapter.send_alert(
        incident_id="INC-ADAPT-01",
        subject="Adapter Test Alert",
        message="Simulated alert body",
        severity="HIGH",
        topic_arn="arn:aws:sns:ap-southeast-2:206238482111:CloudShield-Disaster-Alerts"
    )
    assert res["simulated"] is True
    assert res["sns_publish_status"] == "SIMULATED_PUBLISHED_200"
    assert res["message_id"].startswith("mock-msg-")

def test_live_notification_adapter_blocks_in_mock_mode():
    """Verify live SNS adapter refuses execution when AWS_MODE=mock (Cost Safety)."""
    assert settings.AWS_MODE == "mock"
    live_adapter = LiveSNSNotificationAdapter()
    with pytest.raises(RuntimeError) as exc:
        live_adapter.send_alert(
            incident_id="INC-FAIL",
            subject="Unauthorized",
            message="Body",
            severity="LOW",
            topic_arn="arn:aws:sns:..."
        )
    assert "CRITICAL POLICY VIOLATION" in str(exc.value)

def test_local_storage_adapter_read_write():
    """Verify local storage adapter stores and retrieves artifacts."""
    adapter = LocalStorageAdapter()
    filename = "test_manifest.txt"
    content = b"Manifest report data"
    
    path = adapter.store_file(filename, content)
    assert path is not None
    
    retrieved = adapter.retrieve_file(filename)
    assert retrieved == content

def test_s3_storage_adapter_blocks_in_mock_mode():
    """Verify live S3 adapter refuses execution when AWS_MODE=mock."""
    assert settings.AWS_MODE == "mock"
    s3_adapter = S3StorageAdapter()
    with pytest.raises(RuntimeError) as exc:
        s3_adapter.store_file("artifact.txt", b"data")
    assert "CRITICAL POLICY VIOLATION" in str(exc.value)

def test_adapter_factories_return_mock_by_default():
    """Verify adapter factories default to local mock instances."""
    notif = get_notification_adapter()
    assert isinstance(notif, MockSNSNotificationAdapter)
    
    storage = get_storage_adapter()
    assert isinstance(storage, LocalStorageAdapter)
