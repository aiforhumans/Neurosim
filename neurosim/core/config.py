"""
Global configuration for the NeuroSim project.

This module defines a simple configuration class that reads values
from environment variables and falls back to sensible defaults.
Using a dataclass instead of a Pydantic Settings class avoids
compatibility issues across different Pydantic versions and removes
optional dependencies.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


def _resolve_data_path(sub_path: str) -> Path:
    """Compute a data subpath relative to the project root."""
    return Path(__file__).resolve().parents[2] / "data" / sub_path


@dataclass
class Settings:
    """
    Configuration object for NeuroSim.

    Environment variables prefixed with ``NEUROSIM_`` may override
    individual fields. For example ``NEUROSIM_BASE_URL`` will override
    ``base_url``.
    """

    # LLM settings
    base_url: str = field(default_factory=lambda: os.getenv("NEUROSIM_BASE_URL", "http://localhost:1234/v1"))
    api_key: str = field(default_factory=lambda: os.getenv("NEUROSIM_API_KEY", "not-needed"))
    model: str = field(default_factory=lambda: os.getenv("NEUROSIM_MODEL", "gpt-3.5-turbo"))
    temperature: float = field(
        default_factory=lambda: float(os.getenv("NEUROSIM_TEMPERATURE", "0.7"))
    )

    # Data directories
    characters_dir: Path = field(
        default_factory=lambda: Path(os.getenv("NEUROSIM_CHARACTERS_DIR", str(_resolve_data_path("characters"))))
    )
    memories_dir: Path = field(
        default_factory=lambda: Path(os.getenv("NEUROSIM_MEMORIES_DIR", str(_resolve_data_path("memories"))))
    )
    embeddings_dir: Path = field(
        default_factory=lambda: Path(os.getenv("NEUROSIM_EMBEDDINGS_DIR", str(_resolve_data_path("embeddings"))))
    )
    memory_file: Path = field(
        default_factory=lambda: Path(os.getenv("NEUROSIM_MEMORY_FILE", str(_resolve_data_path("memories") / "memory.json")))
    )

    # Vector store
    vector_store_type: str = field(default_factory=lambda: os.getenv("NEUROSIM_VECTOR_STORE_TYPE", "chroma"))
    qdrant_url: str = field(default_factory=lambda: os.getenv("NEUROSIM_QDRANT_URL", "http://localhost:6333"))
    qdrant_api_key: str = field(default_factory=lambda: os.getenv("NEUROSIM_QDRANT_API_KEY", ""))
    embedding_model_name: str = field(
        default_factory=lambda: os.getenv("NEUROSIM_EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    )
    max_memory_entries: int = field(
        default_factory=lambda: int(os.getenv("NEUROSIM_MAX_MEMORY_ENTRIES", "5"))
    )

    def __post_init__(self) -> None:
        # Ensure directories exist
        self.characters_dir = Path(self.characters_dir)
        self.memories_dir = Path(self.memories_dir)
        self.embeddings_dir = Path(self.embeddings_dir)
        self.memory_file = Path(self.memory_file)


# Export a global settings instance
settings = Settings()
