"""
Tests for the MemoryAgent.

This module tests the dual memory system (JSON + vector store) 
functionality of the MemoryAgent class.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from neurosim.agents.memory_agent import MemoryAgent
from neurosim.core.config import Settings
from langchain_core.documents import Document


class TestMemoryAgent:
    """Test cases for MemoryAgent."""

    def test_init_creates_memory_file(self, test_settings: Settings):
        """Test that MemoryAgent creates memory file if it doesn't exist."""
        # Ensure memory file doesn't exist
        test_settings.memory_file.unlink(missing_ok=True)
        
        agent = MemoryAgent(test_settings)
        
        # Memory file should be created
        assert test_settings.memory_file.exists()
        # Should contain empty list
        content = json.loads(test_settings.memory_file.read_text())
        assert content == []

    def test_init_with_existing_memory_file(self, test_settings: Settings, sample_memories):
        """Test initialization with existing memory file."""
        # Create memory file with sample data
        test_settings.memory_file.parent.mkdir(parents=True, exist_ok=True)
        test_settings.memory_file.write_text(json.dumps(sample_memories))
        
        agent = MemoryAgent(test_settings)
        
        # Should load existing memories
        memories = agent.all_memories()
        assert len(memories) == 3
        assert memories[0]["text"] == "User asked about the weather"

    @patch('neurosim.agents.memory_agent.Chroma')
    def test_init_with_chroma_vector_store(self, mock_chroma, test_settings: Settings):
        """Test initialization with Chroma vector store."""
        mock_vector_store = Mock()
        mock_chroma.return_value = mock_vector_store
        
        agent = MemoryAgent(test_settings)
        
        # Chroma should be initialized
        mock_chroma.assert_called_once()
        assert agent.vector_store == mock_vector_store

    def test_init_with_unsupported_vector_store(self, test_settings: Settings):
        """Test initialization with unsupported vector store type."""
        test_settings.vector_store_type = "unsupported"
        
        with pytest.raises(ValueError, match="Unsupported vector store type"):
            MemoryAgent(test_settings)

    def test_store_memory_json_only(self, test_settings: Settings):
        """Test storing memory to JSON file."""
        # Mock vector store to None to test JSON-only functionality
        with patch('neurosim.agents.memory_agent.Chroma', return_value=None):
            agent = MemoryAgent(test_settings)
            agent.vector_store = None
            
            # Store a memory
            agent.store_memory("Test message", {"role": "user"})
            
            # Check JSON file
            memories = agent.all_memories()
            assert len(memories) == 1
            assert memories[0]["text"] == "Test message"
            assert memories[0]["metadata"]["role"] == "user"
            assert "timestamp" in memories[0]

    @patch('neurosim.agents.memory_agent.Chroma')
    def test_store_memory_with_vector_store(self, mock_chroma, test_settings: Settings):
        """Test storing memory to both JSON and vector store."""
        mock_vector_store = Mock()
        mock_chroma.return_value = mock_vector_store
        
        agent = MemoryAgent(test_settings)
        
        # Store a memory
        agent.store_memory("Test message", {"role": "user"})
        
        # Check vector store was called
        mock_vector_store.add_texts.assert_called_once_with(
            ["Test message"], 
            metadatas=[{"role": "user"}]
        )
        
        # Check JSON file
        memories = agent.all_memories()
        assert len(memories) == 1
        assert memories[0]["text"] == "Test message"

    @patch('neurosim.agents.memory_agent.Chroma')
    def test_store_memory_with_persist(self, mock_chroma, test_settings: Settings):
        """Test that vector store persist is called if available."""
        mock_vector_store = Mock()
        mock_persist = Mock()
        mock_vector_store.persist = mock_persist
        mock_chroma.return_value = mock_vector_store
        
        agent = MemoryAgent(test_settings)
        agent.store_memory("Test message")
        
        # Persist should be called
        mock_persist.assert_called_once()

    @patch('neurosim.agents.memory_agent.Chroma')
    def test_search_memory_success(self, mock_chroma, test_settings: Settings):
        """Test successful memory search."""
        mock_vector_store = Mock()
        mock_docs = [
            Document(page_content="Found memory 1", metadata={"role": "user"}),
            Document(page_content="Found memory 2", metadata={"role": "assistant"})
        ]
        mock_vector_store.similarity_search.return_value = mock_docs
        mock_chroma.return_value = mock_vector_store
        
        agent = MemoryAgent(test_settings)
        
        results = agent.search_memory("weather", top_k=2)
        
        assert len(results) == 2
        assert results[0].page_content == "Found memory 1"
        mock_vector_store.similarity_search.assert_called_once_with("weather", k=2)

    @patch('neurosim.agents.memory_agent.Chroma')
    def test_search_memory_with_default_top_k(self, mock_chroma, test_settings: Settings):
        """Test memory search uses default top_k from settings."""
        mock_vector_store = Mock()
        mock_vector_store.similarity_search.return_value = []
        mock_chroma.return_value = mock_vector_store
        
        agent = MemoryAgent(test_settings)
        agent.search_memory("query")
        
        # Should use settings.max_memory_entries as default
        mock_vector_store.similarity_search.assert_called_once_with("query", k=3)

    @patch('neurosim.agents.memory_agent.Chroma')
    def test_search_memory_exception_handling(self, mock_chroma, test_settings: Settings):
        """Test memory search handles exceptions gracefully."""
        mock_vector_store = Mock()
        mock_vector_store.similarity_search.side_effect = Exception("Vector store error")
        mock_chroma.return_value = mock_vector_store
        
        agent = MemoryAgent(test_settings)
        
        results = agent.search_memory("query")
        
        # Should return empty list on exception
        assert results == []

    def test_search_memory_no_vector_store(self, test_settings: Settings):
        """Test memory search with no vector store returns empty list."""
        with patch('neurosim.agents.memory_agent.Chroma', return_value=None):
            agent = MemoryAgent(test_settings)
            agent.vector_store = None
            
            results = agent.search_memory("query")
            
            assert results == []

    def test_load_and_save_memory_operations(self, test_settings: Settings, sample_memories):
        """Test internal memory loading and saving operations."""
        agent = MemoryAgent(test_settings)
        
        # Save sample memories
        agent._save_memory(sample_memories)
        
        # Load and verify
        loaded_memories = agent._load_memory()
        assert len(loaded_memories) == 3
        assert loaded_memories[0]["text"] == "User asked about the weather"
        
        # Verify file contents
        file_content = json.loads(test_settings.memory_file.read_text())
        assert file_content == sample_memories
