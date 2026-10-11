from typing import Dict, List
from app.models.disaster import DisasterInput
from app.models.dpri import DPRIResult
from app.models.inventory import SupplyCategory, WarehouseStock
from app.models.allocation import (
    DemandPrediction, ShortageItem, DispatchPlanItem, AllocationRecommendation
)
from app.services.inventory_service import get_inventory_summary

# Map categories to canonical item IDs
CATEGORY_TO_ITEM_ID = {
    SupplyCategory.WATER: "ITEM-WATER",
    SupplyCategory.FOOD: "ITEM-FOOD",
    SupplyCategory.MEDICAL: "ITEM-MED",
    SupplyCategory.SHELTER: "ITEM-SHELTER",
    SupplyCategory.POWER: "ITEM-POWER",
}

def calculate_shortages_and_allocation(
    disaster: DisasterInput,
    dpri: DPRIResult,
    demand: DemandPrediction
) -> AllocationRecommendation:
    """
    1. Computes inventory deficits/shortages across the network.
    2. Generates an optimal multi-warehouse dispatch recommendation using priority-based allocation.
    """
    inv_summary = get_inventory_summary()
    
    # Group stock by category and warehouse
    stock_by_item: Dict[str, List[WarehouseStock]] = {}
    total_stock_by_cat: Dict[SupplyCategory, int] = {cat: 0 for cat in SupplyCategory}
    
    for s in inv_summary.stock:
        stock_by_item.setdefault(s.item_id, []).append(s)
        total_stock_by_cat[s.category] += s.quantity_available
        
    shortage_items: List[ShortageItem] = []
    dispatch_plan: List[DispatchPlanItem] = []
    
    total_demanded = 0
    total_allocated = 0
    total_shortage = 0
    
    for demanded_item in demand.items:
        cat = demanded_item.category
        item_id = CATEGORY_TO_ITEM_ID.get(cat, "ITEM-WATER")
        needed_qty = demanded_item.predicted_demand
        network_available = total_stock_by_cat.get(cat, 0)
        
        can_fulfill = min(needed_qty, network_available)
        shortage_qty = max(0, needed_qty - network_available)
        fulfillment_pct = round((can_fulfill / needed_qty * 100.0) if needed_qty > 0 else 100.0, 1)
        
        total_demanded += needed_qty
        total_allocated += can_fulfill
        total_shortage += shortage_qty
        
        shortage_items.append(
            ShortageItem(
                category=cat,
                item_name=demanded_item.item_name,
                demanded=needed_qty,
                available_network_stock=network_available,
                shortage_quantity=shortage_qty,
                fulfilled_quantity=can_fulfill,
                fulfillment_percentage=fulfillment_pct
            )
        )
        
        # Dispatch allocation across available depots
        remaining_to_dispatch = can_fulfill
        # Prioritize depots with highest available stock of this item
        eligible_depots = sorted(
            stock_by_item.get(item_id, []),
            key=lambda x: x.quantity_available,
            reverse=True
        )
        
        for depot_stock in eligible_depots:
            if remaining_to_dispatch <= 0:
                break
            if depot_stock.quantity_available <= 0:
                continue
                
            dispatch_amount = min(remaining_to_dispatch, depot_stock.quantity_available)
            if dispatch_amount > 0:
                dispatch_plan.append(
                    DispatchPlanItem(
                        warehouse_id=depot_stock.warehouse_id,
                        warehouse_name=depot_stock.warehouse_name,
                        category=cat,
                        item_name=demanded_item.item_name,
                        dispatched_quantity=dispatch_amount,
                        unit=demanded_item.unit
                    )
                )
                remaining_to_dispatch -= dispatch_amount
                # Decrement temporary tracker for subsequent calculations in this session
                depot_stock.quantity_available -= dispatch_amount
                
    overall_fulfillment = round((total_allocated / total_demanded * 100.0) if total_demanded > 0 else 100.0, 1)
    
    return AllocationRecommendation(
        incident_name=disaster.incident_name,
        target_region=disaster.region,
        dpri_score=dpri.dpri_score,
        total_demanded_units=total_demanded,
        total_allocated_units=total_allocated,
        total_shortage_units=total_shortage,
        overall_fulfillment_rate=overall_fulfillment,
        dispatch_plan=dispatch_plan,
        shortage_breakdown=shortage_items
    )
