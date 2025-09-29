import asyncio
import logging
import datetime
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from typing import Dict, Any

from blescope.scanning.application.ports.bluetooth_scanner import BluetoothScanner
from blescope.device_management.application.ports.device_repository import ObservableDeviceRepository
from blescope.device_management.domain.device import Device, DeviceState
from blescope.shared.domain.base_types import DeviceAddress, RSSI

from blescope_dissector import (
    ManufacturerDataDecoder,
    IBeaconAdvertisement
)

class BleakScannerAdapter(BluetoothScanner):
    def __init__(self, device_repo: ObservableDeviceRepository):
        self._scanner = None
        self._scanning = False
        self._device_repo = device_repo
        self._manufacturer_decoder = ManufacturerDataDecoder()
        self._processing_queue = asyncio.Queue()
        self._processor_task = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def start_scan(self) -> None:
        self.logger.info("Starting Bluetooth scan with Bleak")
        self._scanning = True

        # Start the processor task
        self._processor_task = asyncio.create_task(self.__process_queue())

        # Create scanner with detection callback
        self._scanner = BleakScanner(detection_callback=self.__detection_callback)

        try:
            # Start scanner in background
            await self._scanner.start()
            self.logger.info("Scanner started successfully")

            while self._scanning:
                await asyncio.sleep(1)

        except Exception as e:
            self.logger.error(f"Scanner error: {e}", exc_info=True)
            raise
        finally:
            await self.__cleanup()

    def __detection_callback(self, device: BLEDevice, advertisement_data: AdvertisementData):
        """Callback for when a device is detected."""
        try:
            self._processing_queue.put_nowait((device, advertisement_data))
        except asyncio.QueueFull:
            self.logger.warning("Processing queue is full, dropping detected device.")

    async def __process_queue(self):
        """Process detected device from queue"""
        while self._scanning or not self._processing_queue.empty():
            try:
                device, adv_data = await asyncio.wait_for(
                    self._processing_queue.get(),
                    timeout=1.0
                )

                await self.__process_device(device, adv_data)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing device from queue: {e}", exc_info=True)

    async def __process_device(self, device: BLEDevice, advertisement_data: AdvertisementData):
        """Process a single device detection"""
        # Create device entity from advertisement data
        decoded_mfd = self.__decode_manufacturer_data(advertisement_data)

        device_entity = Device(
            address=DeviceAddress(device.address),
            name=advertisement_data.local_name or device.name,
            rssi=RSSI(advertisement_data.rssi),
            state=DeviceState.DISCONNECTED,
            last_seen=datetime.datetime.now(datetime.UTC),
            manufacturer_data=advertisement_data.manufacturer_data if advertisement_data.manufacturer_data else {},
            decoded_manufacturer=decoded_mfd
        )
        
        # Save and let repository/observers handle the rest
        await self._device_repo.save(device_entity)

    def __decode_manufacturer_data(self, advertisement_data: AdvertisementData) -> Dict[int, Any]:
        """Decode manufacturer data"""
        decoded = {}
        
        if not advertisement_data.manufacturer_data:
            return decoded
        
        # Basic vendor info for all
        for company_id, data_bytes in advertisement_data.manufacturer_data.items():
            vendor_name = self._manufacturer_decoder.get_manufacturer_name(company_id)
            decoded[str(company_id)] = { # Use str keys for JSON compatibility
                'company_id': company_id,
                'company_name': vendor_name,
                'raw_hex': data_bytes.hex(),
                'raw_length': len(data_bytes)
            }
        
        # Try specific decoding
        decoded_list = self._manufacturer_decoder.decode(dict(advertisement_data.manufacturer_data))
        for decoded_item in decoded_list:
            # Enhance with decoded information
            if decoded_item.advertisement:
                decoded[str(decoded_item.company.company_id)].update(
                    self.__extract_advertisement_data(advertisement_data.rssi, decoded_item.advertisement)
                )

        return decoded

    @staticmethod
    def __extract_advertisement_data(rssi: int, advertisement: Any) -> Dict[str, Any]:
        """Extract data from decoded advertisement"""
        # Implementation depends on advertisement type
        # This keeps the decoding logic separate
        data = {}
        
        if isinstance(advertisement, IBeaconAdvertisement):
            data.update({
                'type': 'ibeacon',
                'uuid': str(advertisement.uuid),
                'major': advertisement.major,
                'minor': advertisement.minor,
                'tx_power': advertisement.tx_power,
                'estimated_distance': advertisement.estimate_distance(rssi)  # in meters
            })

        # TODO: Add other advertisement types as needed
        
        return data

    async def stop_scan(self) -> None:
        self.logger.info("Stopping Bluetooth scan")
        self._scanning = False
        await self.__cleanup()

    async def __cleanup(self):
        """Cleanup scanner resources."""
        if self._scanner:
            try:
                await self._scanner.stop()
                self.logger.info("Scanner stopped")
            except Exception as e:
                self.logger.error(f"Error stopping scanner: {e}")
        
        self._scanner = None

        # Clear any remaining items in the queue
        while not self._processing_queue.empty():
            try:
                self._processing_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

    def get_decoder(self) -> ManufacturerDataDecoder:
        """Get the manufacturer data decoder (for registering custom decoders)."""
        return self._manufacturer_decoder
