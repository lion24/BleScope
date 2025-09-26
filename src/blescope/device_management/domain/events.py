from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Optional, Dict, Any
from blescope.shared.domain.base_types import DeviceAddress
from serde import serde

@serde
@dataclass
class DeviceEvent:
    """Base class for device-related events."""
    device_address: str
    occurred_at: int = field(default_factory=lambda: int(datetime.now(UTC).timestamp() * 1000), init=False)

@serde
@dataclass(kw_only=True)
class DeviceCreated(DeviceEvent):
    """Event triggered when a new device is created in the system."""
    rssi: int = 0
    name: Optional[str] = None
    manufacturer_data: Dict[str, Any] = field(default_factory=dict)
    decoded_manufacturer: Dict[str, Any]
    beacon_info: Optional[Dict[str, Any]] = None # e.g., for ibeacon details

@serde
@dataclass
class DeviceUpdated(DeviceEvent):
    """Event triggered when a device is updated in the repository"""
    changes: Dict[str, Any] # What changed, e.g. {"rssi": -70, "name": "New Name"}

@serde
@dataclass
class DeviceConnected(DeviceEvent):
    """Event triggered when a device is connected."""
    services_count: int

@serde
@dataclass
class DeviceDisconnected(DeviceEvent):
    """Event triggered when a device is disconnected."""
    pass
