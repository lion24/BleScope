import asyncio
import logging
from typing import Optional
import uuid

from blescope.scanning.application.ports.bluetooth_scanner import BluetoothScanner
from blescope.scanning.application.ports.scan_repository import ScanRepository
from blescope.shared.events.event_bus import EventBus
from blescope.scanning.domain.scan import Scan, ScanState
from blescope.scanning.domain.exceptions import InvalidScanStateError
from blescope.scanning.domain.events import ScanStarted, ScanStopped, DeviceDiscovered

def generate_scan_id() -> str:
    return str(uuid.uuid4())

class ScanManager:
    """Manage background scanning tasks"""

    def __init__(
            self,
            scanner: BluetoothScanner,
            scan_repo: ScanRepository,
            event_bus: EventBus,
    ):
        self.scanner = scanner
        self.scan_repo = scan_repo
        self.event_bus = event_bus
        self._scan_task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def start_scan(self) -> str:
        """Start scanning in the background and return the scan ID."""
        if self._scan_task and not self._scan_task.done():
            raise InvalidScanStateError("A scan is already running.")
        
        # Get or create scan
        scan = await self.scan_repo.get_current()
        if not scan:
            scan = Scan(id=generate_scan_id())

        # Start scan
        scan.start()
        await self.scan_repo.save(scan)

        # Publish event
        await self.event_bus.publish(ScanStarted(scan_id=scan.id))

        # Start background task
        self._scan_task = asyncio.create_task(self._scan_loop(scan))

        self.logger.info(f"Scan {scan.id} started in background.")
        return scan.id

    async def _scan_loop(self, scan: Scan):
        """Background scan loop"""
        try:
            async for device in self.scanner.start_scan():
                # Check if should continue
                current_scan = await self.scan_repo.get_current()
                if not current_scan or current_scan.state != ScanState.SCANNING:
                    break
                
                self.logger.info(
                    f"Discovered device: {device.address} "
                    f"(Name: {device.name or 'Unknown'}, RSSI: {device.rssi.value})"
                )
                
                scan.add_discovered_device(device.address)
                await self.scan_repo.save(scan)

                # Publish device discovered event
                await self.event_bus.publish(
                    DeviceDiscovered(
                        device_address=device.address,
                        device_name=device.name,
                        rssi=device.rssi,
                        manufacturer_data=device.manufacturer_data,
                    )
                )

        except asyncio.CancelledError:
            self.logger.info(f"Scan {scan.id} cancelled.")
        except Exception as e:
            self.logger.error(f"Scan error: {e}", exc_info=True)

    async def stop_scan(self) -> None:
        """Stop the current scan."""
        scan = await self.scan_repo.get_current()
        if not scan or scan.state != ScanState.SCANNING:
            raise InvalidScanStateError("No scan is currently running.")
        
        # Update scan state
        scan.stop()
        await self.scan_repo.save(scan)

        # Stop scanner
        await self.scanner.stop_scan()

        # Cancel task if running
        if self._scan_task and not self._scan_task.done():
            self._scan_task.cancel()
            try:
                await self._scan_task
            except asyncio.CancelledError:
                pass
        
        # Publish event
        await self.event_bus.publish(
            ScanStopped(
                scan_id=scan.id,
                devices_found=len(scan.discovered_devices)
            )
        )

        self.logger.info(f"Scan {scan.id} stopped.")
