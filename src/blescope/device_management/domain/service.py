from dataclasses import dataclass, field
from typing import List

from blescope.device_management.domain.characteristic import Characteristic

@dataclass
class Service:
    uuid: str
    is_primary: bool = True
    characteristics: List[Characteristic] = field(default_factory=list)
