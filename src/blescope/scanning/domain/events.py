import time

from datetime import datetime, UTC
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Any, Dict, Optional

from blescope.shared.domain.base_types import DeviceAddress, RSSI

@dataclass_json
@dataclass(kw_only=True)
class DomainEvent:
    """Base class for domain events.

    occurred_on is automatically set when the event instance is created and is excluded
    from the generated __init__ so subclasses can freely declare their own non-default fields
    without ordering issues.
    """
    occurred_at: int = field(default_factory=lambda: int(time.clock_gettime(time.CLOCK_REALTIME) * 1000), init=False)

@dataclass_json
@dataclass
class ScanStarted(DomainEvent):
    """Event triggered when a scan is started."""
    scan_id: str

@dataclass_json
@dataclass
class ScanStopped(DomainEvent):
    """Event triggered when a scan is stopped."""
    scan_id: str
    devices_found: int
