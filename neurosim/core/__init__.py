"""
Core package for NeuroSim.

This package exports the Settings object used across the
application. Importing this module will initialise the global
``settings`` instance with validated environment variables.
"""

from .config import Settings, settings  # noqa: F401