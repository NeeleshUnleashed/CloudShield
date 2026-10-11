import sqlite3
from typing import Dict, List, Optional
from app.db.database import get_connection
from app.models.inventory import (
    Warehouse, WarehouseStock, InventorySummary, SupplyCategory
)

def get_inventory_summary() -> InventorySummary:
    """Retrieves full view of all warehouses and their real-time inventory."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT warehouse_id, warehouse_name, location, latitude, longitude FROM warehouses;")
    warehouses = [
        Warehouse(
            warehouse_id=row["warehouse_id"],
            warehouse_name=row["warehouse_name"],
            location=row["location"],
            latitude=row["latitude"],
            longitude=row["longitude"]
        )
        for row in cursor.fetchall()
    ]
    
    cursor.execute("""
        SELECT ws.warehouse_id, w.warehouse_name, w.location, ws.item_id, i.item_name, i.category,
               ws.quantity_available, ws.reserved_quantity, i.unit
        FROM warehouse_stock ws
        JOIN warehouses w ON ws.warehouse_id = w.warehouse_id
        JOIN inventory_items i ON ws.item_id = i.item_id
        ORDER BY w.warehouse_name, i.category;
    """)
    stocks = [
        WarehouseStock(
            warehouse_id=row["warehouse_id"],
            warehouse_name=row["warehouse_name"],
            location=row["location"],
            item_id=row["item_id"],
            item_name=row["item_name"],
            category=SupplyCategory(row["category"]),
            quantity_available=row["quantity_available"],
            reserved_quantity=row["reserved_quantity"],
            unit=row["unit"]
        )
        for row in cursor.fetchall()
    ]
    
    conn.close()
    return InventorySummary(warehouses=warehouses, stock=stocks)

def get_network_stock_totals() -> Dict[SupplyCategory, int]:
    """Returns aggregated available quantities by supply category across the entire depot network."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT i.category, SUM(ws.quantity_available) as total_available
        FROM warehouse_stock ws
        JOIN inventory_items i ON ws.item_id = i.item_id
        GROUP BY i.category;
    """)
    totals = {}
    for row in cursor.fetchall():
        totals[SupplyCategory(row["category"])] = row["total_available"] or 0
        
    conn.close()
    return totals

def deduct_dispatched_stock(warehouse_id: str, item_id: str, quantity: int) -> bool:
    """Atomically deducts allocated stock from a specific warehouse."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE warehouse_stock
        SET quantity_available = quantity_available - ?
        WHERE warehouse_id = ? AND item_id = ? AND quantity_available >= ?;
    """, (quantity, warehouse_id, item_id, quantity))
    
    success = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return success
