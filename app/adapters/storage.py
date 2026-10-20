from pathlib import Path
from typing import Optional
from app.config import settings
from app.adapters.base import BaseStorageAdapter

class LocalStorageAdapter(BaseStorageAdapter):
    """
    Local filesystem storage adapter simulating Amazon S3 bucket storage.
    Files are stored deterministically in data/local_storage/s3/.
    """
    
    def __init__(self):
        self.base_dir = settings.STORAGE_DIR / "s3"
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def store_file(self, filename: str, content: bytes, content_type: str = "text/plain") -> str:
        target_path = self.base_dir / filename
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "wb") as f:
            f.write(content)
        return str(target_path)
        
    def retrieve_file(self, filename: str) -> Optional[bytes]:
        target_path = self.base_dir / filename
        if not target_path.exists():
            return None
        with open(target_path, "rb") as f:
            return f.read()

class S3StorageAdapter(BaseStorageAdapter):
    """
    Production Amazon S3 storage adapter.
    Guarded by AWS Zero-Unexpected-Charges policy.
    """
    
    def store_file(self, filename: str, content: bytes, content_type: str = "text/plain") -> str:
        if settings.AWS_MODE != "live":
            raise RuntimeError(
                "CRITICAL POLICY VIOLATION: S3 storage adapter invoked while AWS_MODE=mock. "
                "Live S3 operations require explicit user authorization."
            )
        try:
            import boto3
            s3 = boto3.client("s3", region_name=settings.AWS_REGION)
            bucket_name = settings.S3_BUCKET_NAME
            s3.put_object(
                Bucket=bucket_name,
                Key=filename,
                Body=content,
                ContentType=content_type
            )
            return f"s3://{bucket_name}/{filename}"
        except Exception as e:
            raise RuntimeError(f"S3 upload failed: {str(e)}")
            
    def retrieve_file(self, filename: str) -> Optional[bytes]:
        if settings.AWS_MODE != "live":
            raise RuntimeError("Live S3 access blocked in mock mode.")
        import boto3
        s3 = boto3.client("s3", region_name=settings.AWS_REGION)
        bucket_name = settings.S3_BUCKET_NAME
        res = s3.get_object(Bucket=bucket_name, Key=filename)
        return res["Body"].read()

def get_storage_adapter() -> BaseStorageAdapter:
    """Factory function returning the active storage adapter."""
    if settings.AWS_MODE == "live":
        return S3StorageAdapter()
    return LocalStorageAdapter()
