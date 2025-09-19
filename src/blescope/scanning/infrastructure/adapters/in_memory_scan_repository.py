from typing import Optional, Dict
from blescope.scanning.application.ports.scan_repository import ScanRepository
from blescope.scanning.domain.scan import Scan


class InMemoryScanRepository(ScanRepository):
    def __init__(self):
        self._scans: Dict[str, Scan] = {}
        self._current_scan_id: Optional[str] = None

    async def save(self, scan):
        self._scans[scan.id] = scan
        self._current_scan_id = scan.id

    async def get(self, scan_id) -> Optional[Scan]:
        return self._scans.get(scan_id)

    async def get_current(self) -> Optional[Scan]:
        if self._current_scan_id:
            return self._scans.get(self._current_scan_id)
        return None

    async def delete(self, scan_id):
        if scan_id in self._scans:
            del self._scans[scan_id]
            if self._current_scan_id == scan_id:
                self._current_scan_id = None
