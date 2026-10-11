import pytest
from app.db.seed_data import seed_database
from app.services.inventory_service import (
    get_inventory_summary, get_network_stock_totals, deduct_dispatched_stock
)
from app.models.inventory import SupplyCategory

@pytest.fixture(autouse=True)
def setup_db():
    seed_database(force_reset=True)

def test_inventory_seed_and_summary():
    """Verify pre-seeded warehouses and inventory stock lines."""
    summary = get_inventory_summary()
    assert len(summary.warehouses) == 4
    warehouse_ids = {w.warehouse_id for w in summary.warehouses}
    assert warehouse_ids == {"WH-SYD", "WH-BNE", "WH-MEL", "WH-PER"}
    assert len(summary.stock) == 20  # 4 warehouses * 5 supply items

def test_network_stock_totals():
    """Verify aggregated category totals across all 4 depots."""
    totals = get_network_stock_totals()
    for cat in SupplyCategory:
        assert cat in totals
        assert totals[cat] > 0

def test_atomic_stock_deduction():
    """Verify that stock is deducted cleanly and bounds check prevents over-deduction."""
    summary = get_inventory_summary()
    first_stock = summary.stock[0]
    initial_qty = first_stock.quantity_available
    
    # Valid deduction
    success = deduct_dispatched_stock(first_stock.warehouse_id, first_stock.item_id, 100)
    assert success is True
    
    # Check new quantity
    updated_summary = get_inventory_summary()
    for s in updated_summary.stock:
        if s.warehouse_id == first_stock.warehouse_id and s.item_id == first_stock.item_id:
            assert s.quantity_available == initial_qty - 100
            
    # Invalid over-deduction (more than remaining)
    fail_success = deduct_dispatched_stock(first_stock.warehouse_id, first_stock.item_id, initial_qty * 2)
    assert fail_success is False
