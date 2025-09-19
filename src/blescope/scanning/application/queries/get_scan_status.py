import datetime

from dataclasses import dataclass
from typing import Optional

from blescope.scanning.application.ports.scan_repository import ScanRepository
from blescope.scanning.domain.scan import ScanState

@dataclass
class GetScanStatusQuery:
    """Query to get the current status of a scan."""
    pass

@dataclass
class ScanStatusDTO:
    """Data Transfer Object for scan status."""
    is_scanning: bool
    state: str
    devices_found: int = 0
    scan_id: Optional[str] = None
    started_at: Optional[datetime.datetime] = None

class GetScanStatusQueryHandler:
    def __init__(self, scan_repo: ScanRepository):
        self.scan_repo = scan_repo

    async def handle(self, query: GetScanStatusQuery) -> ScanStatusDTO:
        """Handle the GetScanStatusQuery and return the current scan status."""
        scan = await self.scan_repo.get_current()
        
        if not scan:
            return ScanStatusDTO(
                is_scanning=False,
                state="idle"
            )
        
        return ScanStatusDTO(
            is_scanning=scan.state == ScanState.SCANNING,
            scan_id=scan.id,
            devices_found=len(scan.discovered_devices),
            started_at=scan.start_time,
            state=scan.state.value
        )
