from abc import ABC, abstractmethod
from typing import Optional

from blescope.device_management.domain.device import Device
from blescope.shared.domain.base_types import DeviceAddress

class DeviceRepository(ABC):
    """Repository interface for storing discovered devices during scan."""

    @abstractmethod
    async def save(self, device: Device) -> None:
        """Save a discovered device."""
        pass

    @abstractmethod
    async def get(self, address: DeviceAddress) -> Optional[Device]:
        """Get a discovered device by its address."""
        pass

    @abstractmethod
    async def get_all(self) -> list[Device]:
        """Get all discovered devices."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all discovered devices."""
        pass
