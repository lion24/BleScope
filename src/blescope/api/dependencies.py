"""Wire up dependencies for all modules"""
from functools import lru_cache
from typing import Dict, Any

from blescope.scanning.application.queries.get_scan_status import GetScanStatusQueryHandler
from blescope.scanning.application.services.scan_manager import ScanManager
from blescope.scanning.infrastructure.adapters.bleak_scanner_adapter import BleakScannerAdapter
from blescope.scanning.application.ports.scan_repository import ScanRepository
from blescope.scanning.application.ports.device_repository import DeviceRepository
from blescope.scanning.infrastructure.adapters.in_memory_discovered_device_repository import InMemoryDiscoveredDeviceRepository
from blescope.scanning.application.ports.bluetooth_scanner import BluetoothScanner
from blescope.scanning.infrastructure.adapters.in_memory_scan_repository import InMemoryScanRepository
from blescope.shared.events.event_bus import EventBus

from blescope.api.websocket_manager import WebSocketManager

# Singleton instances
event_bus = EventBus()

@lru_cache()
def get_event_bus() -> EventBus:
    """Dependency to get the singleton EventBus instance."""
    return event_bus

@lru_cache()
def get_bluetooth_scanner() -> BluetoothScanner:
    """Dependency to get the singleton BluetoothScanner instance."""
    device_repo = get_discovered_device_repository()
    return BleakScannerAdapter(device_repo=device_repo)

@lru_cache()
def get_discovered_device_repository() -> DeviceRepository:
    """Dependency to get the singleton DeviceRepository instance."""
    return InMemoryDiscoveredDeviceRepository()

@lru_cache()
def get_scan_repository() -> ScanRepository:
    """Dependency to get the singleton ScanRepository instance."""
    return InMemoryScanRepository()

def get_scan_query_handler() -> Dict[str, Any]:
    """Get all query handlers for scanning module."""
    scan_repo = get_scan_repository()

    return {
        "get_scan_status": GetScanStatusQueryHandler(scan_repo=scan_repo),
    }

def get_scan_manager() -> Any:
    """Get the ScanManager service."""
    event_bus = get_event_bus()
    scanner = get_bluetooth_scanner()
    scan_repo = get_scan_repository()

    return ScanManager(
        scanner=scanner,
        scan_repo=scan_repo,
        event_bus=event_bus,
    )

def get_websocket_manager() -> WebSocketManager:
    """Get the WebSocketManager service."""
    event_bus = get_event_bus()
    return WebSocketManager(event_bus=event_bus)

def create_application_dependencies():
    """Initialize all dependencies and set up event handlers."""
    event_bus = get_event_bus()

    return {
        "event_bus": event_bus,
        "scanner": get_bluetooth_scanner(),
    }
