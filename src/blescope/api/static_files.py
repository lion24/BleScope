from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

def setup_static_files(app: FastAPI):
    """Setup static file serving"""
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)

    # Mount static files
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Serve index.html at root
    @app.get("/")
    async def serve_frontend():
        return FileResponse(static_dir / "index.html")
