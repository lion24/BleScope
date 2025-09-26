import time

from datetime import datetime, UTC
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from serde import serde

from blescope.shared.domain.base_types import DeviceAddress, RSSI

@serde
@dataclass(kw_only=True)
class DomainEvent:
    """Base class for domain events.

    occurred_on is automatically set when the event instance is created and is excluded
    from the generated __init__ so subclasses can freely declare their own non-default fields
    without ordering issues.
    """
    occurred_at: int = field(default_factory=lambda: int(time.clock_gettime(time.CLOCK_REALTIME) * 1000), init=False)

@serde
@dataclass
class ScanStarted(DomainEvent):
    """Event triggered when a scan is started."""
    scan_id: str

@serde
@dataclass
class ScanStopped(DomainEvent):
    """Event triggered when a scan is stopped."""
    scan_id: str
    devices_found: int
