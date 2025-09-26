import asyncio
import logging
from typing import Dict, List, Optional, Set, Any
from blescope.device_management.application.ports.device_repository import (
    ObservableDeviceRepository,
    DeviceRepositoryObserver,
)

from blescope.device_management.domain.device import Device
from blescope.shared.domain.base_types import DeviceAddress

class InMemoryObservableDeviceRepository(ObservableDeviceRepository):
    """In-memory device repository with observer support."""

    def __init__(self):
        self._devices: Dict[DeviceAddress, Device] = {}
        self._observers: Set[DeviceRepositoryObserver] = set()
        self._lock = asyncio.Lock()
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def save(self, device: Device) -> None:
        """save or update a device and notify observers."""
        async with self._lock:
            is_new = device.address not in self._devices

            # Save the device
            self._devices[device.address] = device

            if is_new:
                self._logger.debug(f"Device created: {device.address}")
                await self._notify_device_created(device)
            else:
                # Always notify update - let observers decide if they care
                self._logger.debug(f"Device updated: {device.address}")
                await self._notify_device_updated(device)

    async def get(self, address: DeviceAddress) -> Optional[Device]:
        """Get a discovered device by its address."""
        async with self._lock:
            return self._devices.get(address)
        
    async def get_all(self) -> List[Device]:
        """Get all discovered devices."""
        async with self._lock:
            return list(self._devices.values())
        
    async def delete(self, address: DeviceAddress) -> None:
        """Delete a device and notify observers."""
        async with self._lock:
            if address in self._devices:
                device = self._devices[address]
                del self._devices[address]
                self._logger.debug(f"Device deleted: {address}")
                await self._notify_device_deleted(address)

    async def clear(self) -> None:
        """Clear all discovered devices"""
        async with self._lock:
            self._devices.clear()

    def subscribe(self, observer: DeviceRepositoryObserver) -> None:
        """Subscribe an observer to device repository updates."""
        self._observers.add(observer)
        self._logger.debug(f"Observer {observer.__class__.__name__} subscribed")

    def unsubscribe(self, observer: DeviceRepositoryObserver) -> None:
        """Unsubscribe an observer from device repository updates."""
        self._observers.discard(observer)
        self._logger.debug(f"Observer {observer.__class__.__name__} unsubscribed")

    async def _notify_device_created(self, device: Device) -> None:
        """Notify all observers about a new device."""
        tasks = []

        for observer in self._observers:
            try:
                task = asyncio.create_task(observer.on_device_created(device))
                tasks.append(task)
            except Exception as e:
                self._logger.error(f"Error notifying observer {observer.__class__.__name__} of device creation: {e}")

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _notify_device_updated(self, device: Device) -> None:
        """Notify all observers about a device update."""
        tasks = []

        for observer in self._observers:
            try:
                task = asyncio.create_task(observer.on_device_updated(device))
                tasks.append(task)
            except Exception as e:
                self._logger.error(f"Error notifying observer {observer.__class__.__name__} of device update: {e}")

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _notify_device_deleted(self, device_address: DeviceAddress) -> None:
        """Notify all observers about a device deletion."""
        tasks = []

        for observer in self._observers:
            try:
                task = asyncio.create_task(observer.on_device_deleted(device_address))
                tasks.append(task)
            except Exception as e:
                self._logger.error(f"Error notifying observer {observer.__class__.__name__} of device deletion: {e}")

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


