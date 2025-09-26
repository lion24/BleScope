import logging
from typing import Optional, Callable

from blescope.device_management.application.ports.device_repository import DeviceRepository
from blescope.device_management.application.ports.device_connector import DeviceConnector
from blescope.interaction.dto.interaction_dto import (
    ReadCharacteristicDTO,
    WriteCharacteristicDTO,
    NotificationDTO
)
from blescope.interaction.domain.exceptions import (
    DeviceNotConnectedError,
    CharacteristicNotFoundError,
    CharacteristicNotReadableError,
    CharacteristicNotWritableError,
    CharacteristicNotNotifiableError
)

from blescope.shared.events.event_bus import EventBus
from blescope.shared.domain.base_types import DeviceAddress

class InteractionService:
    def __init__(
        self,
        device_repo: DeviceRepository,
        device_connector: DeviceConnector,
        event_bus: EventBus,
    ):
        self.device_repo = device_repo
        self.device_connector = device_connector
        self.event_bus = event_bus
        self._notification_handlers = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def read_characteristic(self, dto: ReadCharacteristicDTO) -> bytes:
        """Read a characteristic value from a device."""
        pass

    async def _get_connected_device(self, address: DeviceAddress):
        """Helper to ensure device is connected."""
        device = await self.device_repo.get(address)
        if not device:
            raise DeviceNotConnectedError(f"Device {address} not found.")
