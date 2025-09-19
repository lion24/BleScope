import logging
import logging.config
from typing import Dict, Any

def get_logging_config(log_level: str = "INFO") -> Dict[str, Any]:
    """Return logging configuration dictionary."""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": log_level,
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "level": "DEBUG",
                "filename": "logs/app.log",
                "mode": "a",
                "maxBytes": 10 * 1024 * 1024,  # 10 MB
                "backupCount": 5,
            }
        },
        "loggers": {
            "": { # root logger
                "handlers": ["console", "file"],
                "level": "DEBUG"
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO"
            },
            "fastapi": {
                "handlers": ["console"],
                "level": "INFO"
            }
        }
    }

def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration."""
    import os
    os.makedirs("logs", exist_ok=True)

    config = get_logging_config(log_level)
    logging.config.dictConfig(config)
