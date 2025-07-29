"""
Memory agent for NeuroSim.

This agent manages both long-term and vector-based memory. A simple
JSON file is used to log every interaction along with associated
metadata. In parallel, a vector store (Chroma by default) keeps
embeddings of past messages to enable semantic search when generating
responses. See ``neurosim/core/config.py`` for configuration
parameters controlling the persistence of memory.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from neurosim.core.config import settings, Settings
from neurosim.core.utils import timestamp
from neurosim.core.logging_config import get_agent_logger

# LangChain imports
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.vectorstores import VectorStore
from langchain_core.documents import Document

try:
    from langchain_chroma import Chroma
except ImportError:  # pragma: no cover - optional dependency
    Chroma = None  # type: ignore

try:
    from langchain_community.vectorstores import Qdrant
    from qdrant_client import QdrantClient  # type: ignore
except ImportError:  # pragma: no cover
    Qdrant = None  # type: ignore
    QdrantClient = None  # type: ignore


class MemoryAgent:
    """Persist and retrieve textual memory using both JSON and a vector store."""

    def __init__(self, config: Optional[Settings] = None) -> None:
        # Accept a Settings instance or fall back to the module-level settings
        self.settings = config or settings
        self.memory_file = Path(self.settings.memory_file)
        self.logger = get_agent_logger("MemoryAgent", "MEMORY")
        
        self.logger.info(f"Initializing MemoryAgent with memory file: {self.memory_file}")
        
        # Ensure directories exist
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        # Initialise empty memory file if necessary
        if not self.memory_file.exists():
            self.memory_file.write_text("[]", encoding="utf-8")
            self.logger.info("Created new memory file")

        # Initialise embedding model
        self.logger.debug(f"Loading embedding model: {self.settings.embedding_model_name}")
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=self.settings.embedding_model_name
        )
        # Initialise vector store
        self.vector_store: Optional[VectorStore]
        if self.settings.vector_store_type == "chroma":
            if Chroma is None:
                raise ImportError(
                    "Chroma is not installed. Please add chromadb to your requirements."
                )
            # Persist directory ensures embeddings are stored on disk between runs
            persist_directory = str(self.settings.embeddings_dir)
            self.settings.embeddings_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Initializing Chroma vector store at: {persist_directory}")
            self.vector_store = Chroma(
                collection_name="neurosim_memory",
                embedding_function=self.embedding_model,
                persist_directory=persist_directory,
            )
        elif self.settings.vector_store_type == "qdrant":
            if Qdrant is None or QdrantClient is None:
                raise ImportError(
                    "Qdrant is not installed. Please add qdrant-client to your requirements."
                )
            self.logger.info(f"Initializing Qdrant vector store at: {self.settings.qdrant_url}")
            client = QdrantClient(
                url=self.settings.qdrant_url,
                api_key=self.settings.qdrant_api_key or None,
            )
            # Qdrant will create the collection on the fly if it doesn't exist
            self.vector_store = Qdrant(
                client=client,
                collection_name="neurosim_memory",
                embeddings=self.embedding_model,
            )
        elif self.settings.vector_store_type == "none":
            self.logger.info("Vector store disabled for testing")
            self.vector_store = None
        else:
            raise ValueError(
                f"Unsupported vector store type: {self.settings.vector_store_type}"
            )

    # ------------------------------------------------------------------
    # JSON memory handling
    #
    def _load_memory(self) -> List[Dict[str, Any]]:
        """Load the entire JSON memory file into memory."""
        with self.memory_file.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _save_memory(self, data: List[Dict[str, Any]]) -> None:
        """Write the in-memory representation back to the JSON file."""
        with self.memory_file.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def store_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Persist a piece of text to both the JSON log and vector store.

        Args:
            text: The raw text to persist.
            metadata: Optional metadata associated with this entry (e.g. role).
        """
        metadata = metadata or {}
        self.logger.debug(f"Storing memory entry with {len(text)} characters")
        # Append to JSON file
        data = self._load_memory()
        data.append({"text": text, "metadata": metadata, "timestamp": timestamp()})
        self._save_memory(data)
        # Persist to vector store
        if self.vector_store:
            # The vector store API expects a list of documents and metadatas
            self.vector_store.add_texts([text], metadatas=[metadata])
            # For persistent stores like Chroma we need to explicitly persist
            persist = getattr(self.vector_store, "persist", None)
            if callable(persist):
                persist()
            self.logger.debug("Memory entry added to vector store")

    def search_memory(self, query: str, top_k: Optional[int] = None) -> List[Document]:
        """Perform a semantic search over the stored memories.

        Args:
            query: The natural language query string.
            top_k: Maximum number of results to return. If not provided
                the value configured in ``settings.max_memory_entries``
                will be used.

        Returns:
            A list of :class:`langchain.docstore.document.Document` objects
            containing the retrieved memory texts and any stored
            metadata.
        """
        if not self.vector_store:
            self.logger.warning("No vector store available for memory search")
            return []
        k = top_k or self.settings.max_memory_entries
        self.logger.debug(f"Searching memory for: '{query}' (top_k={k})")
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            self.logger.debug(f"Found {len(docs)} memory entries")
            return docs
        except Exception as e:
            self.logger.error(f"Memory search failed: {e}")
            return []

    def all_memories(self) -> List[Dict[str, Any]]:
        """Return all stored memories from the JSON file."""
        memories = self._load_memory()
        self.logger.debug(f"Retrieved {len(memories)} memories from JSON file")
        return memories
