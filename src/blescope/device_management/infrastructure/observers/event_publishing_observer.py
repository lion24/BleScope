import logging
import copy

from typing import Any, Dict

from blescope.device_management.application.ports.device_repository import DeviceRepositoryObserver
from blescope.device_management.domain.device import Device
from blescope.device_management.domain.events import DeviceCreated, DeviceUpdated
from blescope.shared.events.event_bus import EventBus
from blescope.shared.events.exceptions import HandlerExecutionError
from blescope.shared.domain.base_types import DeviceAddress

class EventPublishingObserver(DeviceRepositoryObserver):
    """Observer that publishes domain events when repository changes"""

    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # Track last known state for significant change detection
        self._last_known_state: Dict[DeviceAddress, Dict[str, Any]] = {}
        self._rssi_change_threshold = 5  # dB change to consider significant

    async def on_device_created(self, device: Device):
        """Publish DeviceCreated event"""
        # Store initial state
        self._last_known_state[device.address] = {
            'rssi': device.rssi.value,
            'name': device.name
        }

        event = DeviceCreated(
            device_address=str(device.address),
            name=device.name,
            rssi=device.rssi.value,
            manufacturer_data={str(k): v.hex() for k, v in device.manufacturer_data.items()},
            decoded_manufacturer=copy.deepcopy(device.decoded_manufacturer) if device.decoded_manufacturer else {}
        )

        try:
            await self._event_bus.publish(event)
            self._logger.debug(f"Published DeviceCreated event for {device.address}")
        except HandlerExecutionError as e:
            self._logger.error(f"Handler execution error while publishing DeviceCreated event for {device.address}: {e}", exc_info=True)
        except Exception as e:
            self._logger.error(f"Failed to publish DeviceCreated event for {device.address}: {e}", exc_info=True)


    async def on_device_updated(self, device: Device):
        """Publish DeviceUpdated event"""
        last_state = self._last_known_state.get(device.address, {})

        # Check for significant changes
        significant_change = False
        
        if abs(last_state.get('rssi', 0) - device.rssi.value) >= self._rssi_change_threshold:
            significant_change = True
        
        if last_state.get('name') != device.name:
            significant_change = True
        
        if significant_change:
            # Update tracked state
            self._last_known_state[device.address] = {
                'rssi': device.rssi.value,
                'name': device.name,
            }
            
            event = DeviceUpdated(
                device_address=device.address,
                changes={
                    'rssi': device.rssi.value,
                    'name': device.name
                }
            )

            self._logger.debug(f"Detected significant update for {device.address}, publishing event {event}.")
            
            try:
                await self._event_bus.publish(event)
                self._logger.debug(f"Published DeviceUpdated event for {device.address}")
            except HandlerExecutionError as e:
                self._logger.error(f"Handler execution error while publishing DeviceUpdated event for {device.address}: {e}", exc_info=True)
            except Exception as e:
                self._logger.error(f"Failed to publish DeviceUpdated event for {device.address}: {e}", exc_info=True)

    async def on_device_deleted(self, address):
        """Currently no event for device deletion"""
        self._logger.debug(f"Device deleted: {address}, no event published.")


    