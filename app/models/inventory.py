from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class SupplyCategory(str, Enum):
    WATER = "WATER"
    FOOD = "FOOD"
    MEDICAL = "MEDICAL"
    SHELTER = "SHELTER"
    POWER = "POWER"

class InventoryItem(BaseModel):
    item_id: str
    item_name: str
    category: SupplyCategory
    unit: str  # e.g., "liters", "ration packs", "kits", "tents", "units"

class WarehouseStock(BaseModel):
    warehouse_id: str
    warehouse_name: str
    location: str
    item_id: str
    item_name: str
    category: SupplyCategory
    quantity_available: int
    reserved_quantity: int = 0
    unit: str

class Warehouse(BaseModel):
    warehouse_id: str
    warehouse_name: str
    location: str
    latitude: float
    longitude: float

class InventorySummary(BaseModel):
    warehouses: List[Warehouse]
    stock: List[WarehouseStock]
