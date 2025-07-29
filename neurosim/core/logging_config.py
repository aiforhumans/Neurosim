"""
Logging configuration for NeuroSim.

This module provides centralised logging configuration for the NeuroSim
application. It creates structured logs with different levels and
agent-specific formatting to help with debugging and monitoring.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from neurosim.core.config import settings


class NeuroSimFormatter(logging.Formatter):
    """Custom formatter for NeuroSim logs."""

    def __init__(self) -> None:
        super().__init__()
        self.base_format = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"

    def format(self, record: logging.LogRecord) -> str:
        # Add agent type if available
        if hasattr(record, 'agent_type'):
            record.name = f"{record.name}[{record.agent_type}]"

        # Colour coding for console output
        if record.levelno >= logging.ERROR:
            self._style._fmt = f"\033[91m{self.base_format}\033[0m"  # Red
        elif record.levelno >= logging.WARNING:
            self._style._fmt = f"\033[93m{self.base_format}\033[0m"  # Yellow
        elif record.levelno >= logging.INFO:
            self._style._fmt = f"\033[92m{self.base_format}\033[0m"  # Green
        else:
            self._style._fmt = self.base_format
        return super().format(record)


def setup_logging(log_level: str = "INFO", log_file: Optional[Path] = None) -> None:
    """
    Configure logging for NeuroSim.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create logs directory if needed
    logs_dir = Path(settings.memories_dir.parent / "logs")
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Default log file if none provided
    if log_file is None:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"neurosim_{timestamp_str}.log"

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(NeuroSimFormatter())
    root_logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # Always log everything to file
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)

    logging.info(f"NeuroSim logging initialized - Level: {log_level}, File: {log_file}")


def get_agent_logger(agent_name: str, agent_type: str = "") -> logging.Logger:
    """
    Get a logger instance for a specific agent.

    Args:
        agent_name: Name of the agent class
        agent_type: Type identifier for the agent

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(f"neurosim.{agent_name.lower()}")

    # Add agent type to log records
    def add_agent_type(record: logging.LogRecord) -> bool:
        record.agent_type = agent_type
        return True

    logger.addFilter(add_agent_type)
    return logger


# Initialise logging on module import
setup_logging()