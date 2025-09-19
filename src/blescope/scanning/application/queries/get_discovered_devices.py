from dataclasses import dataclass
from typing import Optional, List

from blescope.scanning.application.ports.scan_repository import ScanRepository
from blescope.scanning.application.ports.device_repository import DeviceRepository

@dataclass
class GetDiscoveredDevicesQuery:
    """Query to get all discovered devices during the current scan."""
    include_details: bool = True

@dataclass
class DiscoveredDeviceDTO:
    """Data Transfer Object for a discovered device."""
    device_address: str
    name: Optional[str]
    rssi: int
    last_seen: int
    manufacturer_data: Optional[dict] = None

class GetDiscoveredDevicesQueryHandler:
    def __init__(
        self,
        scan_repo: ScanRepository,
        device_repo: DeviceRepository = None # Optional, for detailed info
    ):
        self.scan_repo = scan_repo
        self.device_repo = device_repo

    async def handle(self, query: GetDiscoveredDevicesQuery) -> List[DiscoveredDeviceDTO]:
        scan = await self.scan_repo.get_current()
        if not scan:
            return []

        devices = []

        if self.device_repo and query.include_details:
            # TODO: Fetch detailed device info from device_repo if needed
            pass
        else:
            # Just return addresses from scan
            devices = [
                DiscoveredDeviceDTO(
                    device_address=addr,
                    name=None,
                    rssi=0,
                    last_seen=-1,
                    manufacturer_data={}  # Omit detailed data
                )
                for addr in scan.discovered_devices
            ]

        return devices
