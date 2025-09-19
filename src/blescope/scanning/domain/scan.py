import datetime

from dataclasses import dataclass, field
from enum import Enum
from typing import Set, Optional

from blescope.shared.domain.base_types import DeviceAddress
from .exceptions import InvalidScanStateError

class ScanState(Enum):
    IDLE = "idle"
    SCANNING = "scanning"

@dataclass
class Scan:
    id: str
    state: ScanState = ScanState.IDLE
    start_time: Optional[datetime.datetime] = None
    stop_time: Optional[datetime.datetime] = None
    discovered_devices: Set[DeviceAddress] = field(default_factory=set)

    def start(self):
        if self.state != ScanState.IDLE:
            raise InvalidScanStateError("Cannot start scan - scan is already running.")
        
        self.state = ScanState.SCANNING
        self.start_time = datetime.datetime.now(datetime.UTC)
        self.discovered_devices.clear()

    def stop(self):
        if self.state != ScanState.SCANNING:
            raise InvalidScanStateError("Cannot stop scan - scan is not running.")
        
        self.state = ScanState.IDLE
        self.stop_time = datetime.datetime.now(datetime.UTC)

    def add_discovered_device(self, address: DeviceAddress):
        self.discovered_devices.add(address)
