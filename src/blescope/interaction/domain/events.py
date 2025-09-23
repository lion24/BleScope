from dataclasses import dataclass, field
from datetime import datetime, UTC

from blescope.shared.domain.base_types import DeviceAddress

@dataclass
class CharacteristicNotification:
    """Event raised when a characteristic notification is received."""
    device_address: DeviceAddress
    characteristic_uuid: str
    value: bytes
    occured_at: datetime = field(default_factory=lambda: datetime.now(UTC))
