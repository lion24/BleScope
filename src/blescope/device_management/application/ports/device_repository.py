from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

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
    async def delete(self, address: DeviceAddress) -> None:
        """Delete a device"""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all discovered devices."""
        pass

class DeviceRepositoryObserver(ABC):
    """Observer interface for device repository events."""

    @abstractmethod
    async def on_device_created(self, device: Device) -> None:
        """Called when a new device is created."""
        pass

    @abstractmethod
    async def on_device_updated(self, device: Device) -> None:
        """Called when a device is updated - observer can decide what to do."""
        pass

    @abstractmethod
    async def on_device_deleted(self, address: DeviceAddress) -> None:
        """Called when a device is deleted."""
        pass

class ObservableDeviceRepository(ABC):
    """Interface for a device repository that can notify observers of events."""

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
    async def delete(self, address: DeviceAddress) -> None:
        """Delete a device"""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all discovered devices."""
        pass

    @abstractmethod
    def subscribe(self, observer: DeviceRepositoryObserver) -> None:
        """Register an observer to receive device repository events."""
        pass

    @abstractmethod
    def unsubscribe(self, observer: DeviceRepositoryObserver) -> None:
        """Unregister an observer from receiving device repository events."""
        pass
