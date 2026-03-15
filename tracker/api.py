"""
API layer for RBE Resource Tracker.

Provides programmatic interface for resource management
operations including CRUD, allocation, and queries.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from .database import ResourceDatabase


class ResourceAPI:
    """
    API for resource management operations.
    
    Provides methods for:
    - Resource CRUD operations
    - Resource allocation
    - History queries
    - Feed management
    """
    
    def __init__(self, db_path: str = "rbe_resources.db"):
        """
        Initialize the API with database connection.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db = ResourceDatabase(db_path)
    
    def create_resource(self, resource_id: str, name: str, 
                        resource_type: str, unit: str,
                        initial_quantity: float = 0.0,
                        metadata: Optional[Dict] = None) -> bool:
        """
        Create a new resource.
        
        Args:
            resource_id: Unique identifier
            name: Human-readable name
            resource_type: ENERGY, WATER, or MATERIAL
            unit: Physical unit (kWh, m³, kg, unit)
            initial_quantity: Starting quantity
            metadata: Optional metadata
            
        Returns:
            True if created successfully
        """
        return self.db.add_resource(
            resource_id, name, resource_type, unit, 
            initial_quantity, metadata
        )
    
    def get_resource(self, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get resource by ID."""
        return self.db.get_resource(resource_id)
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all resources."""
        return self.db.get_all_resources()
    
    def allocate(self, resource_id: str, amount: float,
                 allocated_to: Optional[str] = None,
                 purpose: Optional[str] = None) -> bool:
        """
        Allocate resource quantity.
        
        Args:
            resource_id: Resource to allocate from
            amount: Amount to allocate
            allocated_to: Recipient entity
            purpose: Purpose of allocation
            
        Returns:
            True if allocation succeeded
        """
        return self.db.allocate_resource(
            resource_id, amount, allocated_to, purpose
        )
    
    def add_quantity(self, resource_id: str, amount: float) -> bool:
        """Add quantity to a resource."""
        return self.db.add_quantity(resource_id, amount)
    
    def get_allocation_history(self, resource_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get allocation history for a resource or all resources."""
        return self.db.get_allocation_history(resource_id)
    
    def register_feed(self, feed_id: str, name: str, 
                      source_type: str, config: Dict[str, Any]) -> bool:
        """Register a data feed source."""
        return self.db.register_feed(feed_id, name, source_type, config)
    
    def get_active_feeds(self) -> List[Dict[str, Any]]:
        """Get all active data feeds."""
        return self.db.get_active_feeds()
