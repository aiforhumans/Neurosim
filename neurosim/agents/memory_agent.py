"""
Simplified memory agent for NeuroSim.

This stubbed implementation provides minimal functionality for
storing conversation history in memory. It deliberately omits
embedding and vector store integration to keep dependencies light for
testing purposes. In a full implementation the memory agent would
manage both long‑term JSON logs and a semantic vector store (e.g.
Chroma or Qdrant) to enable semantic search.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from neurosim.core.config import settings, Settings
from neurosim.core.logging_config import get_agent_logger
from neurosim.core.utils import timestamp


class MemoryAgent:
    """Persist and retrieve textual memory using an in‑memory list."""

    def __init__(self, config: Optional[Settings] = None) -> None:
        self.settings = config or settings
        self.logger = get_agent_logger("MemoryAgent", "MEMORY")
        self.logger.info("Initializing simplified MemoryAgent")
        # In lieu of a persistent JSON file, use an in‑memory list
        self._memories: List[Dict[str, Any]] = []

    def store_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Persist a piece of text to the internal list."""
        metadata = metadata or {}
        self.logger.debug(f"Storing memory entry with {len(text)} characters")
        self._memories.append({"text": text, "metadata": metadata, "timestamp": timestamp()})

    def search_memory(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Perform a naive search over the stored memories.

        This implementation simply returns the most recent ``top_k`` entries
        regardless of the query.
        """
        k = top_k or self.settings.max_memory_entries
        self.logger.debug(f"Searching memory for: '{query}' (top_k={k})")
        return list(reversed(self._memories))[:k]

    def all_memories(self) -> List[Dict[str, Any]]:
        """Return all stored memories."""
        self.logger.debug(f"Retrieved {len(self._memories)} memories from in‑memory store")
        return list(self._memories)