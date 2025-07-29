"""
Global configuration for the NeuroSim project.

This module defines a simple configuration class that reads values
from environment variables and falls back to sensible defaults.
Using a dataclass instead of a Pydantic Settings class avoids
compatibility issues across different Pydantic versions and removes
optional dependencies. Additional validation is performed in
``__post_init__`` to ensure that environment variables are well
formed.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse


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

    # Custom events file. If provided, the ``EventAgent`` will load user-defined
    # events from this JSON file. The file should contain a list of strings.
    events_file: Path = field(
        default_factory=lambda: Path(os.getenv("NEUROSIM_EVENTS_FILE", ""))
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
        """Perform post-initialisation tasks and validate configuration values."""
        # Ensure directory fields are Path objects
        self.characters_dir = Path(self.characters_dir)
        self.memories_dir = Path(self.memories_dir)
        self.embeddings_dir = Path(self.embeddings_dir)
        self.memory_file = Path(self.memory_file)
        self.events_file = Path(self.events_file) if self.events_file else self.events_file

        # Create the directories if they do not exist
        for directory in [self.characters_dir, self.memories_dir, self.embeddings_dir, self.memory_file.parent]:
            directory.mkdir(parents=True, exist_ok=True)

        # Validate base_url is a valid HTTP/S URL
        parsed = urlparse(self.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"Invalid NEUROSIM_BASE_URL '{self.base_url}': must be a valid http or https URL")

        # Validate temperature is in a reasonable range (0–2 is typical for OpenAI APIs)
        if not (0.0 <= self.temperature <= 2.0):
            raise ValueError(
                f"Invalid NEUROSIM_TEMPERATURE '{self.temperature}': must be a float between 0.0 and 2.0"
            )

        # Validate vector store type
        allowed_vector_stores = {"chroma", "qdrant"}
        if self.vector_store_type.lower() not in allowed_vector_stores:
            raise ValueError(
                f"Invalid NEUROSIM_VECTOR_STORE_TYPE '{self.vector_store_type}': must be one of {allowed_vector_stores}"
            )

        # Validate maximum memory entries
        if self.max_memory_entries <= 0:
            raise ValueError(
                f"Invalid NEUROSIM_MAX_MEMORY_ENTRIES '{self.max_memory_entries}': must be a positive integer"
            )


# Export a global settings instance
settings = Settings()