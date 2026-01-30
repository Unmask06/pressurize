"""Logging configuration for the application."""

import logging
import os
import sys

# Get log level from environment variable, default to INFO
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

def configure_logging():
    """Configure the root logger and formatters."""
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    
    # Remove existing handlers to avoid duplicates if re-configured
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    root_logger.addHandler(handler)

    # Set pressurize logger specifically if needed, but root should cover it
    logger = logging.getLogger("pressurize")
    logger.setLevel(LOG_LEVEL)
    
    return logger
