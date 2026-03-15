"""
Unit tests for Resource models and database operations.
"""

import unittest
import os
import tempfile
import sys

sys.path.insert(0, '/home/student/RBE-TVP-SIM')

from rbe.models.resource import (
    Resource, EnergyResource, WaterResource, MaterialResource,
    ResourceType, ResourceUnit
)
from tracker.database import ResourceDatabase
from tracker.api import ResourceAPI


class TestResourceModels(unittest.TestCase):
    """Test cases for Resource model classes."""
    
    def test_energy_resource_creation(self):
        """Test EnergyResource creation with kWh unit."""
        energy = EnergyResource(name="Solar Array A", quantity=1000.0)
        self.assertEqual(energy.name, "Solar Array A")
        self.assertEqual(energy.quantity, 1000.0)
        self.assertEqual(energy.unit, ResourceUnit.KWH)
        self.assertEqual(energy.resource_type, ResourceType.ENERGY)
    
    def test_water_resource_creation(self):
        """Test WaterResource creation with m3 unit."""
        water = WaterResource(name="Fresh Water Reserve", quantity=500.0)
        self.assertEqual(water.name, "Fresh Water Reserve")
        self.assertEqual(water.quantity, 500.0)
        self.assertEqual(water.unit, ResourceUnit.CUBIC_METER)
        self.assertEqual(water.resource_type, ResourceType.WATER)
    
    def test_material_resource_creation(self):
        """Test MaterialResource creation with kg and unit."""
        steel = MaterialResource(name="Steel Stock", quantity=1000.0, is_discrete=False)
        components = MaterialResource(name="Circuit Boards", quantity=50.0, is_discrete=True)
        self.assertEqual(steel.unit, ResourceUnit.KILOGRAM)
        self.assertEqual(components.unit, ResourceUnit.UNIT)
    
    def test_resource_allocation(self):
        """Test resource allocation reduces quantity."""
        energy = EnergyResource(name="Battery Bank", quantity=100.0)
        allocated = energy.allocate(30.0)
        self.assertEqual(allocated, 30.0)
        self.assertEqual(energy.quantity, 70.0)
    
    def test_resource_allocation_insufficient(self):
        """Test allocation when insufficient quantity."""
        energy = EnergyResource(name="Small Battery", quantity=10.0)
        allocated = energy.allocate(50.0)
        self.assertEqual(allocated, 10.0)
        self.assertEqual(energy.quantity, 0.0)
    
    def test_resource_add_quantity(self):
        """Test adding quantity to resource."""
        water = WaterResource(name="Reservoir", quantity=100.0)
        water.add(50.0)
        self.assertEqual(water.quantity, 150.0)
    
    def test_resource_negative_quantity_error(self):
        """Test that negative quantity raises error."""
        with self.assertRaises(ValueError):
            EnergyResource(name="Invalid", quantity=-10.0)
    
    def test_resource_to_dict(self):
        """Test resource serialization to dict."""
        energy = EnergyResource(name="Solar", quantity=500.0)
        data = energy.to_dict()
        self.assertEqual(data["name"], "Solar")
        self.assertEqual(data["quantity"], 500.0)
        self.assertEqual(data["unit"], "kWh")
        self.assertIn("resource_id", data)


class TestResourceDatabase(unittest.TestCase):
    """Test cases for ResourceDatabase operations."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.db = ResourceDatabase(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database."""
        import os
        os.unlink(self.temp_db.name)
    
    def test_add_resource(self):
        """Test adding resource to database."""
        success = self.db.add_resource(
            "res-001", "Solar Array", "ENERGY", "kWh", 1000.0
        )
        self.assertTrue(success)
        success = self.db.add_resource(
            "res-001", "Solar Array", "ENERGY", "kWh", 1000.0
        )
        self.assertFalse(success)
    
    def test_get_resource(self):
        """Test retrieving resource from database."""
        self.db.add_resource("res-002", "Water Tank", "WATER", "m³", 500.0)
        resource = self.db.get_resource("res-002")
        self.assertIsNotNone(resource)
        self.assertEqual(resource["name"], "Water Tank")
        resource = self.db.get_resource("non-existent")
        self.assertIsNone(resource)
    
    def test_allocate_resource(self):
        """Test resource allocation."""
        self.db.add_resource("res-003", "Battery", "ENERGY", "kWh", 100.0)
        success = self.db.allocate_resource("res-003", 30.0, "Factory A", "Production")
        self.assertTrue(success)
        resource = self.db.get_resource("res-003")
        self.assertEqual(resource["current_quantity"], 70.0)
        success = self.db.allocate_resource("res-003", 100.0)
        self.assertFalse(success)
    
    def test_allocation_history(self):
        """Test allocation history retrieval."""
        self.db.add_resource("res-005", "Copper", "MATERIAL", "kg", 500.0)
        self.db.allocate_resource("res-005", 100.0, "Electronics", "Wiring")
        self.db.allocate_resource("res-005", 50.0, "Plumbing", "Pipes")
        history = self.db.get_allocation_history("res-005")
        self.assertEqual(len(history), 2)


class TestResourceAPI(unittest.TestCase):
    """Test cases for ResourceAPI."""
    
    def setUp(self):
        """Set up test API."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.temp_db.close()
        self.api = ResourceAPI(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database."""
        import os
        os.unlink(self.temp_db.name)
    
    def test_full_workflow(self):
        """Test complete resource management workflow."""
        self.api.create_resource("res-007", "Water Reservoir", "WATER", "m³", 10000.0)
        self.api.add_quantity("res-007", 5000.0)
        resource = self.api.get_resource("res-007")
        self.assertEqual(resource["current_quantity"], 15000.0)
        self.api.allocate("res-007", 3000.0, "Agriculture", "Irrigation")
        resource = self.api.get_resource("res-007")
        self.assertEqual(resource["current_quantity"], 12000.0)
        history = self.api.get_allocation_history("res-007")
        self.assertEqual(len(history), 1)


if __name__ == "__main__":
    unittest.main()
