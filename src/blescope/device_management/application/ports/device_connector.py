from abc import ABC, abstractmethod
from typing import List, Callable
from blescope.shared.domain.base_types import DeviceAddress
from blescope.device_management.domain.service import Service

class DeviceConnector(ABC):
    @abstractmethod
    async def connect(self, address: DeviceAddress) -> None:
        """Connect to a device given its address."""
        pass

    @abstractmethod
    async def disconnect(self, address: DeviceAddress) -> None:
        """Disconnect from a device given its address."""
        pass

    @abstractmethod
    async def discover_services(self, address: DeviceAddress) -> List[Service]:
        """Discover services of a connected device."""
        pass

    @abstractmethod
    async def is_connected(self, address: DeviceAddress) -> bool:
        """Check if a device is currently connected."""
        pass

    @abstractmethod
    async def read_characteristic(
        self, 
        address: DeviceAddress, 
        service_uuid: str, 
        characteristic_uuid: str
    ) -> bytes:
        """Read a characteristic value"""
        pass
    
    @abstractmethod
    async def write_characteristic(
        self,
        address: DeviceAddress,
        service_uuid: str,
        characteristic_uuid: str,
        data: bytes,
        with_response: bool = True
    ) -> None:
        """Write data to a characteristic"""
        pass
    
    @abstractmethod
    async def start_notify(
        self,
        address: DeviceAddress,
        characteristic_uuid: str,
        callback: Callable
    ) -> None:
        """Start notifications for a characteristic"""
        pass
    
    @abstractmethod
    async def stop_notify(
        self,
        address: DeviceAddress,
        characteristic_uuid: str
    ) -> None:
        """Stop notifications for a characteristic"""
        pass
    
    @abstractmethod
    async def disconnect_all(self) -> None:
        """Disconnect from all connected devices"""
        pass
