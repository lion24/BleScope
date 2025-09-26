from fastapi import APIRouter, Depends, HTTPException

from blescope.device_management.application.queries.get_devices import GetDevicesQuery, GetDevicesQueryHandler
from blescope.api.dependencies import get_device_query_handler

router = APIRouter(prefix="/devices", tags=["device_management"])

@router.get("/", summary="Get all known devices")
async def get_all_devices(
    handlers: dict = Depends(get_device_query_handler)
):
    """Get all devices found during the current scan."""
    handler: GetDevicesQueryHandler = handlers["get_devices"]
    result = await handler.handle(GetDevicesQuery())
    return {"devices": result}
