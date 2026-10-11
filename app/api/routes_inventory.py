from fastapi import APIRouter, Depends
from app.models.inventory import InventorySummary
from app.models.approval import DemoRole
from app.services.inventory_service import get_inventory_summary
from app.db.seed_data import seed_database
from app.core.security import get_current_role, require_roles

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])

@router.get("", response_model=InventorySummary)
def get_inventory():
    """Returns current real-time inventory levels across all regional depots."""
    return get_inventory_summary()

@router.post("/reset", response_model=InventorySummary)
def reset_inventory(current_role: DemoRole = Depends(get_current_role)):
    """
    Resets inventory levels to initial seed baseline for demonstration and testing.
    RBAC: EMERGENCY_OFFICER, LOGISTICS_DIRECTOR (AUDITOR denied).
    """
    require_roles([DemoRole.EMERGENCY_OFFICER, DemoRole.LOGISTICS_DIRECTOR], current_role)
    seed_database(force_reset=True)
    return get_inventory_summary()
