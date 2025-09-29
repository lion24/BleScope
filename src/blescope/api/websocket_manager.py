import logging
from fastapi import WebSocket
from typing import List, Dict

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
        self.event_bus.subscribe("DeviceCreated", self._handle_device_created)
        self.event_bus.subscribe("DeviceUpdated", self._handle_device_update)
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.logger.info("WebSocket client connected")
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Send message to all connected clients."""

        for connection in self.active_connections:
            try:
                self.logger.debug(f"Sending message to client: {message}")
                await connection.send_json(message)
            except Exception as e:
                self.logger.error(f"Error sending message to client: {e}", exc_info=True)

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

    async def _handle_device_created(self, event):
        """Handle both device created and updated events"""
        try:
            message = {
                "type": "device_created",
                "data": {
                    "address": event.data["device_address"],
                    "name": event.data["name"],
                    "rssi": event.data["rssi"],
                    "timestamp": event.data["occurred_at"],
                    "manufacturer_data": event.data.get("manufacturer_data", {}),
                    "decoded_manufacturer": event.data.get("decoded_manufacturer", {})
                }
            }

            await self.broadcast(message)
            self.logger.debug(f"Broadcast device_discovered for {message['data']['address']}")
        except Exception as e:
            self.logger.error(f"Error broadcasting device_created: {e}", exc_info=True)
        
    async def _handle_device_update(self, event):
        await self.broadcast({
            "type": "device_updated",
            "data": {
                "address": event.data["device_address"],
                "changes": event.data["changes"],
                "timestamp": event.data["occurred_at"]
            }
        })
