import os

from fastapi import APIRouter, Query
from typing import List, Optional

router = APIRouter(tags=["logs"])

@router.get("/recent", summary="Get recent log entries")
async def get_recent_logs(
    limit: int = Query(100, ge=1, le=1000, description="Number of log entries to retrieve"),
    level: Optional[str] = Query(None, regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$", description="Filter logs by level")
):
    """Get recent log entries."""
    log_file = "logs/app.log" # TODO: fetch dynamically from config

    if not os.path.exists(log_file):
        return {"logs": []}
    
    with open(log_file, "r") as f:
        all_lines = f.readlines()

    # Get last 'limit' lines
    recent_lines = all_lines[-limit:]

    # Filter by level if specified
    if level:
        recent_lines = [
            line for line in recent_lines
            if f" {level} " in line
        ]

    return {"logs": recent_lines}
