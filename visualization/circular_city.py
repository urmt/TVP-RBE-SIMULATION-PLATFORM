"""Circular City Visualization Module - Fresco's Concentric Ring Design."""
import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class RingType(Enum):
    CENTER = "center"
    RESIDENTIAL = "residential"
    AGRICULTURAL = "agricultural"
    INDUSTRIAL = "industrial"
    RECREATION = "recreation"
    TRANSPORT = "transport"


@dataclass
class CityRing:
    ring_type: RingType
    radius_inner: float
    radius_outer: float
    color: str
    description: str
    facilities: List[str] = None
    
    def __post_init__(self):
        if self.facilities is None:
            self.facilities = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "ring_type": self.ring_type.value,
            "radius_inner": self.radius_inner,
            "radius_outer": self.radius_outer,
            "color": self.color,
            "description": self.description,
            "facilities": self.facilities
        }


@dataclass
class ResourceZone:
    zone_id: str
    name: str
    ring_type: RingType
    resource_type: str
    capacity: float
    current_usage: float
    unit: str
    
    def utilization_rate(self) -> float:
        if self.capacity == 0:
            return 0.0
        return (self.current_usage / self.capacity) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "name": self.name,
            "ring_type": self.ring_type.value,
            "resource_type": self.resource_type,
            "capacity": self.capacity,
            "current_usage": self.current_usage,
            "unit": self.unit,
            "utilization_rate": round(self.utilization_rate(), 2)
        }


class CircularCity:
    COLORS = {
        RingType.CENTER: "#2C3E50",
        RingType.RESIDENTIAL: "#3498DB",
        RingType.AGRICULTURAL: "#27AE60",
        RingType.INDUSTRIAL: "#E74C3C",
        RingType.RECREATION: "#F39C12",
        RingType.TRANSPORT: "#9B59B6",
    }
    
    def __init__(self, city_name: str = "Fresco Circular City"):
        self.city_name = city_name
        self.rings: List[CityRing] = []
        self.resource_zones: List[ResourceZone] = []
        self._init_default_rings()
    
    def _init_default_rings(self):
        ring_configs = [
            (RingType.CENTER, 0, 500, "Central dome with city control systems"),
            (RingType.RESIDENTIAL, 500, 2000, "Housing and living spaces"),
            (RingType.AGRICULTURAL, 2000, 3500, "Food production and hydroponics"),
            (RingType.INDUSTRIAL, 3500, 5000, "Manufacturing and production facilities"),
            (RingType.RECREATION, 5000, 6000, "Parks, entertainment, and leisure"),
            (RingType.TRANSPORT, 6000, 6500, "Transportation infrastructure"),
        ]
        
        for ring_type, inner, outer, desc in ring_configs:
            self.add_ring(CityRing(
                ring_type=ring_type,
                radius_inner=inner,
                radius_outer=outer,
                color=self.COLORS[ring_type],
                description=desc
            ))
    
    def add_ring(self, ring: CityRing) -> None:
        self.rings.append(ring)
    
    def add_resource_zone(self, zone: ResourceZone) -> None:
        self.resource_zones.append(zone)
    
    def get_ring_by_type(self, ring_type: RingType) -> Optional[CityRing]:
        for ring in self.rings:
            if ring.ring_type == ring_type:
                return ring
        return None
    
    def get_zones_by_resource_type(self, resource_type: str) -> List[ResourceZone]:
        return [z for z in self.resource_zones if z.resource_type == resource_type]
    
    def get_city_stats(self) -> Dict[str, Any]:
        stats = {
            "city_name": self.city_name,
            "total_rings": len(self.rings),
            "total_resource_zones": len(self.resource_zones),
            "rings": [r.to_dict() for r in self.rings],
            "resource_summary": {}
        }
        
        for zone in self.resource_zones:
            rt = zone.resource_type
            if rt not in stats["resource_summary"]:
                stats["resource_summary"][rt] = {
                    "total_capacity": 0,
                    "total_usage": 0,
                    "zones": 0
                }
            stats["resource_summary"][rt]["total_capacity"] += zone.capacity
            stats["resource_summary"][rt]["total_usage"] += zone.current_usage
            stats["resource_summary"][rt]["zones"] += 1
        
        return stats
    
    def to_json(self) -> str:
        return json.dumps(self.get_city_stats(), indent=2)


def create_sample_city() -> CircularCity:
    city = CircularCity("Sample RBE City")
    
    city.add_resource_zone(ResourceZone(
        zone_id="energy-001",
        name="Solar Farm Alpha",
        ring_type=RingType.AGRICULTURAL,
        resource_type="energy",
        capacity=10000.0,
        current_usage=7500.0,
        unit="kWh"
    ))
    
    city.add_resource_zone(ResourceZone(
        zone_id="energy-002",
        name="Wind Turbine Cluster",
        ring_type=RingType.INDUSTRIAL,
        resource_type="energy",
        capacity=15000.0,
        current_usage=12000.0,
        unit="kWh"
    ))
    
    city.add_resource_zone(ResourceZone(
        zone_id="water-001",
        name="Reservoir Central",
        ring_type=RingType.CENTER,
        resource_type="water",
        capacity=50000.0,
        current_usage=35000.0,
        unit="m3"
    ))
    
    city.add_resource_zone(ResourceZone(
        zone_id="water-002",
        name="Water Treatment Plant",
        ring_type=RingType.INDUSTRIAL,
        resource_type="water",
        capacity=20000.0,
        current_usage=15000.0,
        unit="m3"
    ))
    
    city.add_resource_zone(ResourceZone(
        zone_id="mat-001",
        name="Steel Production",
        ring_type=RingType.INDUSTRIAL,
        resource_type="material",
        capacity=5000.0,
        current_usage=3200.0,
        unit="kg"
    ))
    
    city.add_resource_zone(ResourceZone(
        zone_id="mat-002",
        name="Component Storage",
        ring_type=RingType.INDUSTRIAL,
        resource_type="material",
        capacity=10000.0,
        current_usage=8500.0,
        unit="unit"
    ))
    
    return city


if __name__ == "__main__":
    city = create_sample_city()
    print(city.to_json())
