from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

from blescope.scanning.application.ports.scan_repository import ScanRepository
from blescope.device_management.application.ports.device_repository import DeviceRepository

@dataclass
class GetDevicesQuery:
    """Query to get all devices found during the current scan."""
    include_details: bool = True

@dataclass
class DeviceDTO:
    """Data Transfer Object for a device."""
    device_address: str
    name: Optional[str]
    rssi: int
    last_seen: int
    manufacturer_data: Optional[dict] = None
    decoded_manufacturer: Dict[int, Any] = field(default_factory=dict)

class GetDevicesQueryHandler:
    def __init__(
        self,
        scan_repo: ScanRepository,
        device_repo: DeviceRepository
    ):
        self.scan_repo = scan_repo
        self.device_repo = device_repo

    async def handle(self, query: GetDevicesQuery) -> List[DeviceDTO]:
        scan = await self.scan_repo.get_current()
        if not scan:
            return []

        devices = []

        if self.device_repo and query.include_details:
            for device in await self.device_repo.get_all():
                if device:
                    devices.append(
                        DeviceDTO(
                            device_address=device.address,
                            name=device.name,
                            rssi=device.rssi,
                            last_seen=int(device.last_seen.timestamp()) if device.last_seen else -1,
                            manufacturer_data={k: v.hex() for k, v in device.manufacturer_data.items()},
                            decoded_manufacturer=device.decoded_manufacturer
                        )
                    )

        return devices
