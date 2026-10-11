import pytest
from pathlib import Path
from app.config import settings
from app.db.seed_data import seed_database

@pytest.fixture(scope="session", autouse=True)
def configure_isolated_test_database():
    """
    Directs all automated test executions to an isolated test database.
    Prevents tests from wiping out or modifying the user's real demo database (cloudshield.db).
    """
    test_db_path = settings.DATA_DIR / "test_cloudshield.db"
    settings.DB_PATH = test_db_path
    
    # Initialize fresh schema & seed
    seed_database(force_reset=True)
    yield
    
    # Clean up test database after test run
    if test_db_path.exists():
        try:
            test_db_path.unlink()
        except Exception:
            pass
