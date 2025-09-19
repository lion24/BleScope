import logging
from fastapi import FastAPI, WebSocket, Depends

from blescope.scanning.infrastructure.web.scan_router import router as scan_router
from .log_router import router as log_router
from blescope.api.websocket_manager import WebSocketManager
from blescope.api.dependencies import get_websocket_manager

logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(title="Bluetooth Scanner / Jammer API")

    app.include_router(scan_router, prefix="/api/v1")
    app.include_router(log_router, prefix="/logs")

    @app.websocket("/ws")
    async def websocket_endpoint(
        websocket: WebSocket,
        websocket_manager: WebSocketManager = Depends(get_websocket_manager)
    ):
        await websocket_manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()  # Keep the connection open
                await websocket.send_text(data)
        except Exception:
            pass
        finally:
            websocket_manager.disconnect(websocket)

    return app
