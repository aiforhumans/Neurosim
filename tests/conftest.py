"""
Test configuration and shared fixtures.

This module provides shared pytest fixtures and configuration
used across multiple test modules.
"""

import pytest
import gc
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator

from neurosim.core.config import Settings
from neurosim.core.state import SessionState


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for tests with proper cleanup."""
    with TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)
        # Force garbage collection and wait for Windows file handles to release
        gc.collect()
        time.sleep(0.1)


@pytest.fixture
def test_settings(temp_dir: Path) -> Settings:
    """Provide test settings with temporary directories."""
    return Settings(
        characters_dir=temp_dir / "characters",
        memories_dir=temp_dir / "memories", 
        embeddings_dir=temp_dir / "embeddings",
        memory_file=temp_dir / "memories" / "memory.json",
        vector_store_type="chroma",
        embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
        max_memory_entries=3,
        base_url="http://localhost:1234/v1",
        api_key="test-key",
        model="test-model",
        temperature=0.7
    )


@pytest.fixture
def test_settings_no_vector_store(temp_dir: Path) -> Settings:
    """Provide test settings without vector store to avoid Windows file locking."""
    class MockSettings(Settings):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            # Override vector store to disable it
            self.vector_store_type = "none"
    
    return MockSettings(
        characters_dir=temp_dir / "characters",
        memories_dir=temp_dir / "memories", 
        embeddings_dir=temp_dir / "embeddings",
        memory_file=temp_dir / "memories" / "memory.json",
        max_memory_entries=3,
        base_url="http://localhost:1234/v1",
        api_key="test-key",
        model="test-model",
        temperature=0.7
    )


@pytest.fixture
def session_state() -> SessionState:
    """Provide a fresh session state for tests."""
    return SessionState()


@pytest.fixture
def sample_memories() -> list[dict]:
    """Provide sample memory data for testing."""
    return [
        {
            "text": "User asked about the weather",
            "metadata": {"role": "user"},
            "timestamp": "2024-01-01T10:00:00"
        },
        {
            "text": "I provided weather information",
            "metadata": {"role": "assistant"},
            "timestamp": "2024-01-01T10:00:01"
        },
        {
            "text": "User thanked me for the help",
            "metadata": {"role": "user"},
            "timestamp": "2024-01-01T10:01:00"
        }
    ]
