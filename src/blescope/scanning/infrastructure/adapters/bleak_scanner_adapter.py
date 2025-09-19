import asyncio
import logging
import datetime
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from typing import AsyncIterator, Set

from blescope.scanning.application.ports.bluetooth_scanner import BluetoothScanner
from blescope.scanning.application.ports.device_repository import DeviceRepository
from blescope.scanning.domain.discovered_device import DiscoveredDevice
from blescope.shared.domain.base_types import DeviceAddress, RSSI

class BleakScannerAdapter(BluetoothScanner):
    def __init__(self, device_repo: DeviceRepository):
        self._scanner = None
        self._scanning = False
        self._discovered_queue = asyncio.Queue()
        self._device_repo = device_repo
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._rssi_change_threshold = 5  # dB change to consider significant

    async def start_scan(self) -> AsyncIterator[DiscoveredDevice]:
        self.logger.info("Starting Bluetooth scan with Bleak")
        self._scanning = True

        # Create scanner with detection callback
        self._scanner = BleakScanner(detection_callback=self._detection_callback)

        try:
            # Start scanner in background
            await self._scanner.start()
            self.logger.info("Scanner started successfully")

            while self._scanning:
                try:
                    device = await asyncio.wait_for(
                        self._discovered_queue.get(),
                        timeout=0.5
                    )
                    yield device
                except asyncio.TimeoutError:
                    continue

        except Exception as e:
            self.logger.error(f"Scanner error: {e}", exc_info=True)
            raise
        finally:
            await self._cleanup()

    def _detection_callback(self, device: BLEDevice, advertisement_data: AdvertisementData):
        """Callback for when a device is detected."""
        asyncio.create_task(self._process_detection(device, advertisement_data))

    async def _process_detection(self, device: BLEDevice, advertisement_data: AdvertisementData):
        try:
            device_address = DeviceAddress(device.address)

            discovered_device = DiscoveredDevice(
                address=device_address,
                name=advertisement_data.local_name or device.name,
                rssi=RSSI(advertisement_data.rssi),
                manufacturer_data=dict(advertisement_data.manufacturer_data)
            )

            # Log discovery
            self.logger.debug(
                f"Detected device {device.address} "
                f"Name={discovered_device.name}, "
                f"rssi={advertisement_data.rssi}, "
                f"tx_power={advertisement_data.tx_power}, "
                f"manufacturer_data={list(advertisement_data.manufacturer_data.keys())}"
            )

            existing_device = await self._device_repo.get(device_address)
            should_enqueue = False

            # Only enqueue if not seen recently
            # (or if RSSI has changed significantly)
            if not existing_device:
                should_enqueue = True
                self.logger.info(
                    f"New discovered device: {device.address} "
                    f"(Name: {discovered_device.name or 'Unknown'}, RSSI: {advertisement_data.rssi})"
                )

                # Save to repository
                await self._device_repo.save_discovered(discovered_device)
            else:
                # Existing device, check RSSI change
                rssi_delta = abs(discovered_device.rssi.value - existing_device.rssi.value)
                named_changed = (discovered_device.name != existing_device.name and discovered_device.name is not None)

                if rssi_delta >= self._rssi_change_threshold or named_changed:
                    should_enqueue = True

                    if rssi_delta >= self._rssi_change_threshold:
                        self.logger.debug(
                            f"Device {device.address} RSSI changed: "
                            f"{existing_device.rssi.value} -> {advertisement_data.rssi} (Δ{rssi_delta})"
                        )
                    if named_changed:
                        self.logger.info(
                            f"Device {device.address} name changed: "
                            f"{existing_device.name} -> {discovered_device.name}"
                        )

                    # Update device in repository
                    existing_device.rssi = RSSI(advertisement_data.rssi)
                    if discovered_device.name:
                        existing_device.name = discovered_device.name

                    existing_device.manufacturer_data = discovered_device.manufacturer_data
                    existing_device.last_seen = datetime.datetime.now(datetime.UTC)

                    await self._device_repo.save_discovered(existing_device)

                    # Use updated device for queue
                    discovered_device = existing_device

            if should_enqueue:
                try:
                    self._discovered_queue.put_nowait(discovered_device)
                except asyncio.QueueFull:
                    self.logger.warning("Discovered device queue is full, dropping device.")

        except Exception as e:
            self.logger.warning(
                f"Failed to process detected device {device.address}: {e}",
            )

    async def stop_scan(self) -> None:
        self.logger.info("Stopping Bluetooth scan")
        self._scanning = False
        await self._cleanup()

    async def _cleanup(self):
        """Cleanup scanner resources."""
        if self._scanner:
            try:
                await self._scanner.stop()
                self.logger.info("Scanner stopped")
            except Exception as e:
                self.logger.error(f"Error stopping scanner: {e}")
        
        self._scanner = None

        # Clear any remaining items in the queue
        while not self._discovered_queue.empty():
            try:
                self._discovered_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
