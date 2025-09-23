import asyncio
import logging
import datetime
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from typing import AsyncIterator, Set

from blescope.scanning.application.ports.bluetooth_scanner import BluetoothScanner
from blescope.device_management.application.ports.device_repository import DeviceRepository
from blescope.device_management.domain.device import Device, DeviceState
from blescope.shared.domain.base_types import DeviceAddress, RSSI

from blescope_dissector import (
    ManufacturerDataDecoder,
    IBeaconAdvertisement
)

class BleakScannerAdapter(BluetoothScanner):
    def __init__(self, device_repo: DeviceRepository):
        self._scanner = None
        self._scanning = False
        self._discovered_queue = asyncio.Queue()
        self._device_repo = device_repo
        self._deocder = ManufacturerDataDecoder()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._rssi_change_threshold = 5  # dB change to consider significant

    async def start_scan(self) -> AsyncIterator[Device]:
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

            # Decode manufacturer data if possible
            decoded_manufacturer = {}
            beacon_info = None

            if advertisement_data.manufacturer_data:
                decoded_list = self._deocder.decode(dict(advertisement_data.manufacturer_data))

                for decoded in decoded_list:
                    # Log decoded information
                    self.logger.debug(
                        f"Decoded {decoded.company.company_name} advertisement "
                        f"for {device.address}: {decoded.advertisement.description}"
                    )

                    # Store decoded data
                    decoded_data = {
                        "company_name": decoded.company.company_name,
                        "company_id": decoded.company.company_id,
                        "description": decoded.advertisement.description,
                        "raw_data": decoded.raw_data.hex() if decoded.raw_data else None
                    }

                    if isinstance(decoded.advertisement, IBeaconAdvertisement):
                        beacon = decoded.advertisement
                        # Create beacon info
                        beacon_info = {
                            "type": "iBeacon",
                            "uuid": str(beacon.uuid),
                            "major": beacon.major,
                            "minor": beacon.minor,
                            "tx_power": beacon.tx_power
                        }
                        
                        decoded_data.update(beacon_info)
                        
                        if beacon.tx_power:
                            distance = beacon.estimate_distance(advertisement_data.rssi)
                            if distance:
                                decoded_data["estimated_distance_m"] = round(distance, 2)
                                beacon_info['distance'] = round(distance, 2)
                                self.logger.info(
                                    f"iBeacon {beacon.uuid} detected at ~{distance:.2f}m"
                                )


            existing_device = await self._device_repo.get(device_address)
            should_enqueue = False

            # Only enqueue if not seen recently
            # (or if RSSI has changed significantly)
            if not existing_device:
                should_enqueue = True

                new_device = Device(
                    address=device_address,
                    name=device.name or advertisement_data.local_name,
                    rssi=RSSI(advertisement_data.rssi),
                    state=DeviceState.DISCONNECTED,
                    last_seen=datetime.datetime.now(datetime.UTC),
                    manufacturer_data=advertisement_data.manufacturer_data,
                    decoded_manufacturer=decoded_manufacturer,
                    beacon_info=beacon_info
                )

                # Log discovery
                self.logger.debug(
                    f"New discovered device {device.address} "
                    f"Name={device.name}, "
                    f"rssi={advertisement_data.rssi}, "
                    f"Type: {beacon_info['type'] if beacon_info else 'Generic'})"
                )

                # Save to repository
                await self._device_repo.save(new_device)

                # Use new device for queue
                existing_device = new_device
            else:
                # Existing device, check RSSI change
                rssi_delta = abs(existing_device.rssi.value - existing_device.rssi.value)
                named_changed = (device.name != existing_device.name and device.name is not None)
                manufacturer_changed = (dict(advertisement_data.manufacturer_data) != existing_device.manufacturer_data 
                                      if advertisement_data.manufacturer_data else False)

                if rssi_delta >= self._rssi_change_threshold or named_changed or manufacturer_changed:
                    should_enqueue = True


                    # Update manufacturer data if changed
                    if manufacturer_changed:
                        existing_device.manufacturer_data = dict(advertisement_data.manufacturer_data)
                        existing_device.decoded_manufacturer = decoded_manufacturer
                        existing_device.beacon_info = beacon_info
                        
                        self.logger.debug(
                            f"Updated manufacturer data for {device.address}"
                        )

                        existing_device.manufacturer_data = advertisement_data.manufacturer_data

                    if rssi_delta >= self._rssi_change_threshold:
                        self.logger.debug(
                            f"Device {device.address} RSSI changed: "
                            f"{existing_device.rssi.value} -> {advertisement_data.rssi} (Δ{rssi_delta})"
                        )
                        # Update device in repository
                        existing_device.rssi = RSSI(advertisement_data.rssi)

                    if named_changed:
                        self.logger.info(
                            f"Device {device.address} name changed: "
                            f"{existing_device.name} -> {device.name or advertisement_data.local_name}"
                        )
                        if existing_device.name:
                            existing_device.name = device.name or advertisement_data.local_name

                    
                    existing_device.last_seen = datetime.datetime.now(datetime.UTC)

                    await self._device_repo.save(existing_device)

            if should_enqueue:
                try:
                    self._discovered_queue.put_nowait(existing_device)
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

    def get_decoder(self) -> ManufacturerDataDecoder:
        """Get the manufacturer data decoder (for registering custom decoders)."""
        return self._decoder
