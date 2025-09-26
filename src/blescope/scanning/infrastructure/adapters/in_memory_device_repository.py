from typing import Dict, List, Optional

from blescope.device_management.application.ports.device_repository import DeviceRepository
from blescope.device_management.domain.device import Device
from blescope.shared.domain.base_types import DeviceAddress

class InMemoryDeviceRepository(DeviceRepository):
    """In-memory implementation of DeviceRepository for storing devices."""

    def __init__(self):
        self._devices: Dict[DeviceAddress, Device] = {}

    async def save(self, device: Device) -> None:
        """Save a discovered device."""
        self._devices[device.address] = device

    async def get(self, address: DeviceAddress) -> Optional[Device]:
        """Get a discovered device by its address."""
        return self._devices.get(address)

    async def get_all(self) -> List[Device]:
        """Get all discovered devices."""
        return list(self._devices.values())
    
    async def delete(self, address: DeviceAddress) -> None:
        """Delete a device"""
        if address in self._devices:
            del self._devices[address]

    async def clear(self) -> None:
        """Clear all discovered devices."""
        self._devices.clear()
