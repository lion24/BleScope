from abc import ABC, abstractmethod
from typing import AsyncIterator
from blescope.device_management.domain.device import Device

class BluetoothScanner(ABC):
    @abstractmethod
    async def start_scan(self) -> AsyncIterator[Device]:
        """Start scanning and yield discovered devices."""
        pass

    @abstractmethod
    async def stop_scan(self) -> None:
        """Stops the current scan."""
        pass
