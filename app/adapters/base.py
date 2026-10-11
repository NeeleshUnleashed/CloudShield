from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseNotificationAdapter(ABC):
    """Abstract interface for disaster emergency notifications."""
    
    @abstractmethod
    def send_alert(
        self,
        incident_id: str,
        subject: str,
        message: str,
        severity: str,
        topic_arn: str
    ) -> Dict[str, Any]:
        """Dispatches an emergency broadcast alert."""
        pass

class BaseStorageAdapter(ABC):
    """Abstract interface for object and artifact storage."""
    
    @abstractmethod
    def store_file(self, filename: str, content: bytes, content_type: str = "text/plain") -> str:
        """Stores a file and returns its storage URI or local path."""
        pass

    @abstractmethod
    def retrieve_file(self, filename: str) -> Optional[bytes]:
        """Retrieves file content by filename."""
        pass
