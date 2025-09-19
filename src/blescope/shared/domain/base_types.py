from typing import NewType
from dataclasses import dataclass


DeviceAddress = NewType("DeviceAddress", str)


@dataclass(frozen=True)
class RSSI:
    value: int

    def __post_init__(self):
        if not (-127 <= self.value <= 0):
            raise ValueError("RSSI value must be between -127 and 0 dBm")
