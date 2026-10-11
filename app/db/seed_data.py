from app.db.database import get_connection, init_db

WAREHOUSES_SEED = [
    ("WH-SYD", "Central Depot Sydney", "Sydney, NSW", -33.8688, 151.2093),
    ("WH-BNE", "Northern Logistics Hub Brisbane", "Brisbane, QLD", -27.4698, 153.0251),
    ("WH-MEL", "Southern Emergency Depot Melbourne", "Melbourne, VIC", -37.8136, 144.9631),
    ("WH-PER", "Western Supply Center Perth", "Perth, WA", -31.9505, 115.8605),
]

ITEMS_SEED = [
    ("ITEM-WATER", "Clean Drinking Water & Purification", "WATER", "liters"),
    ("ITEM-FOOD", "Emergency Ready-to-Eat Food Rations", "FOOD", "ration packs"),
    ("ITEM-MED", "Emergency Trauma & First-Aid Kits", "MEDICAL", "kits"),
    ("ITEM-SHELTER", "All-Weather Family Shelter Tents", "SHELTER", "tents"),
    ("ITEM-POWER", "Mobile Emergency Power Generators", "POWER", "units"),
]

INITIAL_STOCK = {
    "WH-SYD": {"ITEM-WATER": 45000, "ITEM-FOOD": 18000, "ITEM-MED": 1500, "ITEM-SHELTER": 850, "ITEM-POWER": 75},
    "WH-BNE": {"ITEM-WATER": 35000, "ITEM-FOOD": 14000, "ITEM-MED": 1200, "ITEM-SHELTER": 650, "ITEM-POWER": 50},
    "WH-MEL": {"ITEM-WATER": 40000, "ITEM-FOOD": 16000, "ITEM-MED": 1350, "ITEM-SHELTER": 750, "ITEM-POWER": 60},
    "WH-PER": {"ITEM-WATER": 25000, "ITEM-FOOD": 10000, "ITEM-MED": 850, "ITEM-SHELTER": 400, "ITEM-POWER": 35},
}

def seed_database(force_reset: bool = False):
    """Seeds the initial warehouses, relief supply items, and baseline inventory."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    
    if force_reset:
        cursor.execute("DELETE FROM dispatch_manifests;")
        cursor.execute("DELETE FROM warehouse_stock;")
        cursor.execute("DELETE FROM inventory_items;")
        cursor.execute("DELETE FROM warehouses;")
        cursor.execute("DELETE FROM disaster_logs;")
        cursor.execute("DELETE FROM notifications_log;")
        
    # Insert Warehouses
    cursor.executemany("""
    INSERT OR IGNORE INTO warehouses (warehouse_id, warehouse_name, location, latitude, longitude)
    VALUES (?, ?, ?, ?, ?);
    """, WAREHOUSES_SEED)
    
    # Insert Items
    cursor.executemany("""
    INSERT OR IGNORE INTO inventory_items (item_id, item_name, category, unit)
    VALUES (?, ?, ?, ?);
    """, ITEMS_SEED)
    
    # Insert Stock
    for wh_id, items in INITIAL_STOCK.items():
        for it_id, qty in items.items():
            cursor.execute("""
            INSERT OR IGNORE INTO warehouse_stock (warehouse_id, item_id, quantity_available, reserved_quantity)
            VALUES (?, ?, ?, 0);
            """, (wh_id, it_id, qty))
            
    conn.commit()
    conn.close()
