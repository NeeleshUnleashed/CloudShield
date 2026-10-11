import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseModel):
    PROJECT_NAME: str = "CloudShield"
    VERSION: str = "1.0.0"
    
    # CRITICAL: Default must remain 'mock' to prevent unexpected AWS charges
    AWS_MODE: str = os.getenv("AWS_MODE", "mock")
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-southeast-2")
    
    DATA_DIR: Path = BASE_DIR / "data"
    DB_PATH: Path = BASE_DIR / "data" / "cloudshield.db"
    STORAGE_DIR: Path = BASE_DIR / "data" / "local_storage"
    LOGS_DIR: Path = BASE_DIR / "logs"

settings = Settings()

# Ensure directories exist locally
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
