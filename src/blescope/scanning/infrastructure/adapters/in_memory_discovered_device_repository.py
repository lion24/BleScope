from typing import Dict, List, Optional

from blescope.scanning.application.ports.device_repository import DeviceRepository
from blescope.scanning.domain.discovered_device import DiscoveredDevice
from blescope.shared.domain.base_types import DeviceAddress

class InMemoryDiscoveredDeviceRepository(DeviceRepository):
    """In-memory implementation of DeviceRepository for storing discovered devices."""

    def __init__(self):
        self._devices: Dict[DeviceAddress, DiscoveredDevice] = {}

    async def save_discovered(self, device: DiscoveredDevice) -> None:
        """Save a discovered device."""
        self._devices[device.address] = device

    async def get(self, address: DeviceAddress) -> Optional[DiscoveredDevice]:
        """Get a discovered device by its address."""
        return self._devices.get(address)

    async def get_all(self) -> List[DiscoveredDevice]:
        """Get all discovered devices."""
        return list(self._devices.values())

    async def clear(self) -> None:
        """Clear all discovered devices."""
        self._devices.clear()
