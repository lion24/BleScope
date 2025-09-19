from abc import ABC, abstractmethod
from typing import Optional

from blescope.scanning.domain.discovered_device import DiscoveredDevice
from blescope.shared.domain.base_types import DeviceAddress

class DeviceRepository(ABC):
    """Repository interface for storing discovered devices during scan."""

    @abstractmethod
    async def save_discovered(self, device: DiscoveredDevice) -> None:
        """Save a discovered device."""
        pass

    @abstractmethod
    async def get(self, address: DeviceAddress) -> Optional[DiscoveredDevice]:
        """Get a discovered device by its address."""
        pass

    @abstractmethod
    async def get_all(self) -> list[DiscoveredDevice]:
        """Get all discovered devices."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all discovered devices."""
        pass
