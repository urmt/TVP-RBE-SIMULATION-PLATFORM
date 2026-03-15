"""
Resource model for tracking energy (kWh), water (m³), and materials in physical units.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Optional, Dict, Any
import uuid


class ResourceType(Enum):
    """Enumeration of supported resource types."""
    ENERGY = auto()
    WATER = auto()
    MATERIAL = auto()


class ResourceUnit(Enum):
    """Physical units for resource measurement."""
    KWH = "kWh"
    CUBIC_METER = "m³"
    KILOGRAM = "kg"
    UNIT = "unit"


@dataclass
class Resource(ABC):
    """Abstract base class for all resource types."""
    
    name: str
    quantity: float
    unit: ResourceUnit
    resource_type: ResourceType
    resource_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.quantity < 0:
            raise ValueError(f"Resource quantity cannot be negative: {self.quantity}")
        if not self.name or not self.name.strip():
            raise ValueError("Resource name cannot be empty")
    
    def allocate(self, amount: float) -> float:
        if amount < 0:
            raise ValueError(f"Allocation amount cannot be negative: {amount}")
        allocated = min(amount, self.quantity)
        self.quantity -= allocated
        return allocated
    
    def add(self, amount: float) -> None:
        if amount < 0:
            raise ValueError(f"Cannot add negative amount: {amount}")
        self.quantity += amount
    
    def get_availability(self) -> float:
        return self.quantity
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit.value,
            "resource_type": self.resource_type.name,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    @abstractmethod
    def get_unit(cls) -> ResourceUnit:
        pass


@dataclass
class EnergyResource(Resource):
    """Energy resource measured in kilowatt-hours (kWh)."""
    
    def __init__(self, name: str, quantity: float, **kwargs):
        super().__init__(
            name=name,
            quantity=quantity,
            unit=ResourceUnit.KWH,
            resource_type=ResourceType.ENERGY,
            **kwargs
        )
    
    @classmethod
    def get_unit(cls) -> ResourceUnit:
        return ResourceUnit.KWH


@dataclass
class WaterResource(Resource):
    """Water resource measured in cubic meters (m³)."""
    
    def __init__(self, name: str, quantity: float, **kwargs):
        super().__init__(
            name=name,
            quantity=quantity,
            unit=ResourceUnit.CUBIC_METER,
            resource_type=ResourceType.WATER,
            **kwargs
        )
    
    @classmethod
    def get_unit(cls) -> ResourceUnit:
        return ResourceUnit.CUBIC_METER


@dataclass
class MaterialResource(Resource):
    """Material resource measured in kilograms (kg) or discrete units."""
    
    def __init__(self, name: str, quantity: float, is_discrete: bool = False, **kwargs):
        unit = ResourceUnit.UNIT if is_discrete else ResourceUnit.KILOGRAM
        super().__init__(
            name=name,
            quantity=quantity,
            unit=unit,
            resource_type=ResourceType.MATERIAL,
            **kwargs
        )
    
    @classmethod
    def get_unit(cls) -> ResourceUnit:
        return ResourceUnit.KILOGRAM
