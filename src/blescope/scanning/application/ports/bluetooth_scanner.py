from abc import ABC, abstractmethod
from typing import AsyncIterator
from blescope.scanning.domain.discovered_device import DiscoveredDevice

class BluetoothScanner(ABC):
    @abstractmethod
    async def start_scan(self) -> AsyncIterator[DiscoveredDevice]:
        """Start scanning and yield discovered devices."""
        pass

    @abstractmethod
    async def stop_scan(self) -> None:
        """Stops the current scan."""
        pass
