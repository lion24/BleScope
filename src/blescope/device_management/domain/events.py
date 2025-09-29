from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from datetime import datetime, UTC
from typing import Optional, Dict, Any

@dataclass_json
@dataclass
class DeviceEvent:
    """Base class for device-related events."""
    device_address: str
    occurred_at: int = field(default_factory=lambda: int(datetime.now(UTC).timestamp() * 1000), init=False)

@dataclass_json
@dataclass(kw_only=True)
class DeviceCreated(DeviceEvent):
    """Event triggered when a new device is created in the system."""
    rssi: int = 0
    name: Optional[str] = None
    manufacturer_data: Dict[str, Any] = field(default_factory=dict)
    decoded_manufacturer: Dict[str, Any]

@dataclass_json
@dataclass
class DeviceUpdated(DeviceEvent):
    """Event triggered when a device is updated in the repository"""
    changes: Dict[str, Any] # What changed, e.g. {"rssi": -70, "name": "New Name"}

@dataclass_json
@dataclass
class DeviceConnected(DeviceEvent):
    """Event triggered when a device is connected."""
    services_count: int

@dataclass_json
@dataclass
class DeviceDisconnected(DeviceEvent):
    """Event triggered when a device is disconnected."""
    pass
