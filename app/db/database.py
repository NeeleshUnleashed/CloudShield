import sqlite3
from typing import Generator
from app.config import settings

def get_connection() -> sqlite3.Connection:
    """Creates a connection to the local SQLite database."""
    conn = sqlite3.connect(str(settings.DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes schema tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS warehouses (
        warehouse_id TEXT PRIMARY KEY,
        warehouse_name TEXT NOT NULL,
        location TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory_items (
        item_id TEXT PRIMARY KEY,
        item_name TEXT NOT NULL,
        category TEXT NOT NULL,
        unit TEXT NOT NULL
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS warehouse_stock (
        warehouse_id TEXT NOT NULL,
        item_id TEXT NOT NULL,
        quantity_available INTEGER NOT NULL CHECK(quantity_available >= 0),
        reserved_quantity INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (warehouse_id, item_id),
        FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
        FOREIGN KEY (item_id) REFERENCES inventory_items(item_id)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS disaster_logs (
        incident_id TEXT PRIMARY KEY,
        incident_name TEXT NOT NULL,
        disaster_type TEXT NOT NULL,
        region TEXT NOT NULL,
        affected_population INTEGER NOT NULL,
        displaced_population INTEGER NOT NULL,
        dpri_score REAL NOT NULL,
        risk_level TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'PENDING_APPROVAL',
        created_by_role TEXT NOT NULL DEFAULT 'EMERGENCY_OFFICER',
        approved_by_role TEXT,
        approved_at TEXT,
        rejection_reason TEXT,
        proposed_allocation_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Safe column migrations for existing databases
    cursor.execute("PRAGMA table_info(disaster_logs);")
    existing_cols = [row["name"] for row in cursor.fetchall()]
    if "status" not in existing_cols:
        cursor.execute("ALTER TABLE disaster_logs ADD COLUMN status TEXT NOT NULL DEFAULT 'PENDING_APPROVAL';")
    if "created_by_role" not in existing_cols:
        cursor.execute("ALTER TABLE disaster_logs ADD COLUMN created_by_role TEXT NOT NULL DEFAULT 'EMERGENCY_OFFICER';")
    if "approved_by_role" not in existing_cols:
        cursor.execute("ALTER TABLE disaster_logs ADD COLUMN approved_by_role TEXT;")
    if "approved_at" not in existing_cols:
        cursor.execute("ALTER TABLE disaster_logs ADD COLUMN approved_at TEXT;")
    if "rejection_reason" not in existing_cols:
        cursor.execute("ALTER TABLE disaster_logs ADD COLUMN rejection_reason TEXT;")
    if "proposed_allocation_json" not in existing_cols:
        cursor.execute("ALTER TABLE disaster_logs ADD COLUMN proposed_allocation_json TEXT;")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dispatch_manifests (
        dispatch_id TEXT PRIMARY KEY,
        incident_id TEXT NOT NULL,
        warehouse_id TEXT NOT NULL,
        item_id TEXT NOT NULL,
        quantity_dispatched INTEGER NOT NULL,
        status TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (incident_id) REFERENCES disaster_logs(incident_id),
        FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id),
        FOREIGN KEY (item_id) REFERENCES inventory_items(item_id)
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications_log (
        message_id TEXT PRIMARY KEY,
        incident_id TEXT NOT NULL,
        topic_arn TEXT NOT NULL,
        subject TEXT NOT NULL,
        message TEXT NOT NULL,
        severity TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    conn.commit()
    conn.close()
