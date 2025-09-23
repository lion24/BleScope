from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, UTC
from enum import Enum

from blescope.shared.domain.base_types import DeviceAddress, RSSI
from blescope.device_management.domain.service import Service
from blescope.device_management.domain.exceptions import InvalidDeviceStateError

class DeviceState(Enum):
    CONNECTED = "connected"
    CONNECTING = "connecting"
    DISCONNECTED = "disconnected"

@dataclass
class Device:
    address: DeviceAddress
    rssi: RSSI
    name: Optional[str] = None
    state: DeviceState = DeviceState.DISCONNECTED
    services: List[Service] = field(default_factory=list)
    connected_at: Optional[datetime] = None
    last_seen: Optional[datetime] = field(default_factory=lambda: datetime.now(UTC))

    # Additional fields for manufacturer data
    manufacturer_data: Dict[int, bytes] = field(default_factory=dict)
    decoded_manufacturer: Dict[int, Any] = field(default_factory=dict)
    beacon_info: Optional[Dict[str, Any]] = None # e.g., for iBeacon details

    def connect(self):
        if self.state != DeviceState.DISCONNECTED:
            raise InvalidDeviceStateError(f"Cannot connect: Device is currently {self.state.value}.")
        self.state = DeviceState.CONNECTING
    
    def mark_connected(self):
        self.state = DeviceState.CONNECTED
        self.connected_at = datetime.now(UTC)

    def disconnect(self):
        self.state = DeviceState.DISCONNECTED
        self.connected_at = None
        self.services.clear()

    def update_service(self, services: List[Service]):
        self.services = services
