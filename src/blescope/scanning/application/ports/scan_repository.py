from abc import ABC, abstractmethod
from typing import Optional
from blescope.scanning.domain.scan import Scan

class ScanRepository(ABC):
    @abstractmethod
    async def save(self, scan: Scan) -> None:
        """Saves or updates a scan."""
        pass

    @abstractmethod
    async def get(self, scan_id: str) -> Optional[Scan]:
        """Retrieves a scan by its ID."""
        pass

    @abstractmethod
    async def get_current(self) -> Optional[Scan]:
        """Retrieves the current/latest scan."""
        pass

    @abstractmethod
    async def delete(self, scan_id: str) -> None:
        """Deletes a scan."""
        pass
