from dataclasses import dataclass
from typing import Optional, Set

@dataclass
class Characteristic:
    uuid: str
    properties: Set[str] # e.g., {"read", "write", "notify"}
    value: Optional[bytes] = None
