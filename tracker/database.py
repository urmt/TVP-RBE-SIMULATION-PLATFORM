"""
SQLite database module for RBE Resource Tracker.

Manages real-time resource data feeds and allocation history
for energy, water, and material resources.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


class ResourceDatabase:
    """
    SQLite database manager for resource tracking.
    
    Tables:
        - resources: Current resource inventory
        - allocations: Resource allocation history
        - feeds: Real-time data feed sources
        - history: Resource quantity history over time
    """
    
    def __init__(self, db_path: str = "rbe_resources.db"):
        """
        Initialize the database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self) -> None:
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Resources table - current inventory
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resources (
                    resource_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    unit TEXT NOT NULL,
                    current_quantity REAL NOT NULL DEFAULT 0.0,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Allocations table - allocation history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS allocations (
                    allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resource_id TEXT NOT NULL,
                    allocated_quantity REAL NOT NULL,
                    allocated_to TEXT,
                    purpose TEXT,
                    allocated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (resource_id) REFERENCES resources(resource_id)
                )
            """)
            
            # Feeds table - data feed sources
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feeds (
                    feed_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    config TEXT,
                    is_active BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # History table - quantity over time
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resource_id TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (resource_id) REFERENCES resources(resource_id)
                )
            """)
            
            conn.commit()
    
    def add_resource(self, resource_id: str, name: str, resource_type: str, 
                     unit: str, quantity: float = 0.0, 
                     metadata: Optional[Dict] = None) -> bool:
        """Add a new resource to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO resources 
                       (resource_id, name, resource_type, unit, current_quantity, metadata)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (resource_id, name, resource_type, unit, quantity, 
                     json.dumps(metadata) if metadata else None)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get resource details by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM resources WHERE resource_id = ?",
                (resource_id,)
            )
            row = cursor.fetchone()
            if row:
                result = dict(row)
                if result.get("metadata"):
                    result["metadata"] = json.loads(result["metadata"])
                return result
            return None
    
    def get_all_resources(self) -> List[Dict[str, Any]]:
        """Get all resources from the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM resources")
            rows = cursor.fetchall()
            results = []
            for row in rows:
                result = dict(row)
                if result.get("metadata"):
                    result["metadata"] = json.loads(result["metadata"])
                results.append(result)
            return results
    
    def allocate_resource(self, resource_id: str, amount: float, 
                          allocated_to: Optional[str] = None,
                          purpose: Optional[str] = None) -> bool:
        """Allocate a portion of a resource."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check available quantity
            cursor.execute(
                "SELECT current_quantity FROM resources WHERE resource_id = ?",
                (resource_id,)
            )
            row = cursor.fetchone()
            if not row or row[0] < amount:
                return False
            
            # Update resource quantity
            cursor.execute(
                "UPDATE resources SET current_quantity = current_quantity - ?, updated_at = CURRENT_TIMESTAMP WHERE resource_id = ?",
                (amount, resource_id)
            )
            
            # Record allocation
            cursor.execute(
                """INSERT INTO allocations (resource_id, allocated_quantity, allocated_to, purpose)
                   VALUES (?, ?, ?, ?)""",
                (resource_id, amount, allocated_to, purpose)
            )
            
            # Record in history
            cursor.execute(
                """INSERT INTO history (resource_id, quantity)
                   VALUES (?, (SELECT current_quantity FROM resources WHERE resource_id = ?))""",
                (resource_id, resource_id)
            )
            
            conn.commit()
            return True
    
    def add_quantity(self, resource_id: str, amount: float) -> bool:
        """Add quantity to a resource."""
        if amount < 0:
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE resources SET current_quantity = current_quantity + ?, updated_at = CURRENT_TIMESTAMP WHERE resource_id = ?",
                (amount, resource_id)
            )
            if cursor.rowcount == 0:
                return False
            
            # Record in history
            cursor.execute(
                """INSERT INTO history (resource_id, quantity)
                   VALUES (?, (SELECT current_quantity FROM resources WHERE resource_id = ?))""",
                (resource_id, resource_id)
            )
            
            conn.commit()
            return True
    
    def get_allocation_history(self, resource_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get allocation history for a resource or all resources."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if resource_id:
                cursor.execute(
                    """SELECT a.*, r.name as resource_name, r.unit 
                       FROM allocations a 
                       JOIN resources r ON a.resource_id = r.resource_id
                       WHERE a.resource_id = ?
                       ORDER BY a.allocated_at DESC""",
                    (resource_id,)
                )
            else:
                cursor.execute(
                    """SELECT a.*, r.name as resource_name, r.unit 
                       FROM allocations a 
                       JOIN resources r ON a.resource_id = r.resource_id
                       ORDER BY a.allocated_at DESC"""
                )
            
            return [dict(row) for row in cursor.fetchall()]
    
    def register_feed(self, feed_id: str, name: str, source_type: str, 
                      config: Dict[str, Any]) -> bool:
        """Register a new data feed source."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO feeds (feed_id, name, source_type, config)
                       VALUES (?, ?, ?, ?)""",
                    (feed_id, name, source_type, json.dumps(config))
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_active_feeds(self) -> List[Dict[str, Any]]:
        """Get all active data feeds."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM feeds WHERE is_active = 1 ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()
            results = []
            for row in rows:
                result = dict(row)
                if result.get("config"):
                    result["config"] = json.loads(result["config"])
                results.append(result)
            return results
