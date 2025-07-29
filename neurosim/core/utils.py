"""
Utility functions for NeuroSim.

This module provides small helper functions used across the project.
"""

from __future__ import annotations

from datetime import datetime


def timestamp() -> str:
    """Return the current timestamp in ISO 8601 format."""
    return datetime.utcnow().isoformat()