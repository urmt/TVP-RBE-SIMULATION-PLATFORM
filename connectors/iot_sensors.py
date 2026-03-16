"""IoT Sensor Data Connector for RBE-TVP-SIM."""
import random
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class SensorReading:
    sensor_id: str
    resource_type: str
    value: float
    unit: str
    timestamp: datetime
    location: str
    quality: float
    metadata: Dict[str, Any]

class MockIoTSensor:
    def __init__(self, sensor_id: str, resource_type: str, location: str,
                 base_value: float = 100.0, variance: float = 0.1, unit: str = "kWh"):
        self.sensor_id = sensor_id
        self.resource_type = resource_type
        self.location = location
        self.base_value = base_value
        self.variance = variance
        self.unit = unit
        self.readings: List[SensorReading] = []
    
    def generate_reading(self) -> SensorReading:
        noise = random.uniform(-self.variance, self.variance)
        value = self.base_value * (1 + noise)
        quality = random.uniform(0.85, 0.99)
        reading = SensorReading(
            sensor_id=self.sensor_id,
            resource_type=self.resource_type,
            value=round(value, 2),
            unit=self.unit,
            timestamp=datetime.now(),
            location=self.location,
            quality=round(quality, 2),
            metadata={}
        )
        self.readings.append(reading)
        return reading
