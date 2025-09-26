from dataclasses import dataclass
from typing import Optional
from blescope.shared.domain.base_types import DeviceAddress

@dataclass
class ReadCharacteristicDTO:
    """Data Transfer Object for reading a characteristic."""
    device_address: DeviceAddress
    service_uuid: str
    characteristic_uuid: str

@dataclass
class WriteCharacteristicDTO:
    """Data Transfer Object for writing a characteristic."""
    device_address: DeviceAddress
    service_uuid: str
    characteristic_uuid: str
    data: bytes
    with_response: bool = True

@dataclass
class NotificationDTO:
    """Data Transfer Object for managing characteristic notifications."""
    device_address: DeviceAddress
    characteristic_uuid: str
    enable: bool  # True to start notifications, False to stop

@dataclass
class CharacteristicValueDTO:
    """Data Transfer Object for returning characteristic value."""
    device_address: str
    service_uuid: str
    characteristic_uuid: str
    value: str # base64 encoded
    timestamp: int

@dataclass
class NotificationValueDTO:
    """Data Transfer Object for returning notification value."""
    device_address: str
    characteristic_uuid: str
    value: str # base64 encoded
    timestamp: int
