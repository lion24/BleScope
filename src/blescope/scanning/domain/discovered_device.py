import datetime

from dataclasses import dataclass, field
from typing import Optional, Dict

from blescope.shared.domain.base_types import DeviceAddress, RSSI


@dataclass
class DiscoveredDevice:
    """Lightweight representation of a device discovered during a scan."""
    address: DeviceAddress
    rssi: RSSI
    manufacturer_data: Dict[int, bytes]
    name: Optional[str] = None
    discovered_at: datetime = field(default_factory=lambda: datetime.datetime.now(datetime.UTC))
    last_seen: datetime = field(default_factory=lambda: datetime.datetime.now(datetime.UTC))
