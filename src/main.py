import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from blescope.api.app import create_app
from blescope.api.dependencies import create_application_dependencies
from blescope.api.static_files import setup_static_files
from blescope.shared.infrastructure.config import Settings
from blescope.shared.infrastructure.logging_config import setup_logging

# Load settings
settings = Settings()

# Setup logging
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)

# Application dependencies
app_dependencies = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    global app_dependencies

    # Startup
    logger.info("Starting Bluetooth Scanner/Jammer Application...")
    logger.info(f"Configuration: Host={settings.host}, Port={settings.port}, Debug={settings.debug}")

    try:
        app_dependencies = create_application_dependencies()
        logger.info("Dependencies initialized.")
    except Exception as e:
        logger.error(f"Error initializing dependencies: {e}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")
    # Cleanup Bluetooth connections if needed
    if app_dependencies:
        try:
            scanner = app_dependencies.get("scanner")
            if scanner:
                await scanner.stop_scan()
                logger.info("Bluetooth scanner stopped.")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)

    logger.info("Application shutdown complete.")

# Create FastAPI app
app = create_app()
app.router.lifespan_context = lifespan

# Setup static files serving
setup_static_files(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "Bluetooth Scanner/Jammer",
        "version": settings.app_version,
    }

# Add root endpoint
@app.get("/")
async def root():
    return {
        "service": "Bluetooth Scanner/Jammer API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=settings.debug,
    )
