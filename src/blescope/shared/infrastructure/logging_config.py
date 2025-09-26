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
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 5,
            }
        },
        "root": {  # root logger (keep minimal or silence it)
            "handlers": [],
            "level": "WARNING",  # prevents noisy libs
        },
        "loggers": {
            "blescope": {  # your application namespace
                "handlers": ["console", "file"],
                "level": "DEBUG",
                "propagate": False,  # don't bubble up to root
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "fastapi": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
        }
    }

def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration."""
    import os
    os.makedirs("logs", exist_ok=True)

    config = get_logging_config(log_level)
    logging.config.dictConfig(config)
