import logging
from fastapi import WebSocket
from typing import List, Dict
from serde.json import to_json

from blescope.shared.events.event_bus import EventBus

class WebSocketManager:
    def __init__(self, event_bus: EventBus):
        self.active_connections: List[WebSocket] = []
        self.event_bus = event_bus
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._setup_event_handlers()

    def _setup_event_handlers(self):
        # Subscribe to all domain events
        self.event_bus.subscribe("ScanStarted", self._handle_scan_started)
        self.event_bus.subscribe("ScanStopped", self._handle_scan_stopped)
        self.event_bus.subscribe("DeviceDiscovered", self._handle_device_discovered)
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.logger.info("WebSocket client connected")
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Send message to all connected clients."""
        disconnects = []

        for connection in self.active_connections:
            try:
                self.logger.debug(f"Sending message to client: {message}")
                await connection.send_text(to_json(message))
            except Exception as e:
                self.logger.error(f"Error sending message to client: {e}", exc_info=True)
                disconnects.append(connection)

        # Clean up disconnected clients
        for connection in disconnects:
            self.active_connections.remove(connection)

    async def _handle_scan_started(self, event):
        self.logger.info(f"Scan started: {event}")
        await self.broadcast({
            "type": "scan_started",
            "data": {
                "scan_id": event.data["scan_id"],
                "timestamp": event.data["occurred_at"]
            }
        })

    async def _handle_scan_stopped(self, event):
        self.logger.info(f"Scan stopped: {event}")
        await self.broadcast({
            "type": "scan_stopped",
            "data": {
                "scan_id": event.data["scan_id"],
                "timestamp": event.data["occurred_at"]
            }
        })

    async def _handle_device_discovered(self, event):
        self.logger.info(f"Device discovered: {event}")
        await self.broadcast({
            "type": "device_discovered",
            "data": {
                "address": event.data["device_address"],
                "name": event.data["device_name"],
                "rssi": event.data["rssi"],
                "timestamp": event.data["occurred_at"]
            }
        })
