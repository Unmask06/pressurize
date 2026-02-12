"""Logging configuration for the application."""

import logging
import os
import sys

import colorlog

# Get log level from environment variable, default to DEBUG
LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG").upper()


def configure_logging():
    """Configure the root logger with colored output formatter."""
    handler = colorlog.StreamHandler(sys.stdout)

    # Create a colored formatter with custom colors for each level
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)-8s%(reset)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
        secondary_log_colors={},
        style="%",
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
