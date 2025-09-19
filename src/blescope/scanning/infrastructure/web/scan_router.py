from fastapi import APIRouter, Depends, HTTPException

from blescope.scanning.application.services.scan_manager import ScanManager
from blescope.scanning.application.queries.get_scan_status import GetScanStatusQuery, GetScanStatusQueryHandler
from blescope.scanning.domain.exceptions import InvalidScanStateError
from blescope.api.dependencies import get_scan_manager, get_scan_query_handler

router = APIRouter(prefix="/scan", tags=["scanning"])

@router.post("/start", summary="Start a new scan")
async def start_scan(
    scan_manager: ScanManager = Depends(get_scan_manager)
):
    """Start bluetooth scanning."""
    try:
        scan_id = await scan_manager.start_scan()
        return {
            "status": "Scanning started",
            "scan_id": scan_id
        }
    except InvalidScanStateError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/stop", summary="Stop the current scan")
async def stop_scan(
    scan_manager: ScanManager = Depends(get_scan_manager)
):
    """Stop bluetooth scanning."""
    try:
        await scan_manager.stop_scan()
        return {"status": "Scanning stopped"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status", summary="Get the current scan status")
async def get_scan_status(
    handlers: dict = Depends(get_scan_query_handler)
):
    """Get current scan status."""
    handler: GetScanStatusQueryHandler = handlers["get_scan_status"]
    result = await handler.handle(GetScanStatusQuery())
    return result
