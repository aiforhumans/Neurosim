"""
Simple test runner for core functionality without Chroma.

This script runs key tests without the Windows file locking issues
that occur with Chroma SQLite databases in the test suite.
"""

import sys
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from neurosim.core.config import Settings
from neurosim.core.state import SessionState, EmotionState
from neurosim.agents.memory_agent import MemoryAgent
from neurosim.agents.emotion_agent import EmotionAgent


def test_memory_agent_without_vector_store():
    """Test MemoryAgent with JSON-only storage."""
    print("Testing MemoryAgent without vector store...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create settings without vector store
        settings = Settings(
            memories_dir=temp_path / "memories",
            memory_file=temp_path / "memories" / "memory.json",
            vector_store_type="none"
        )
        
        # Initialize agent
        agent = MemoryAgent(settings)
        
        # Test storing memory
        agent.store_memory("Test message", {"role": "user"})
        
        # Test retrieving all memories
        memories = agent.all_memories()
        assert len(memories) == 1
        assert memories[0]["text"] == "Test message"
        assert memories[0]["metadata"]["role"] == "user"
        
        # Test search (should return empty list without vector store)
        results = agent.search_memory("test query")
        assert results == []
        
        print("✅ MemoryAgent test passed")


def test_emotion_agent():
    """Test EmotionAgent functionality."""
    print("Testing EmotionAgent...")
    
    agent = EmotionAgent()
    
    # Test positive message
    emotion_state = EmotionState()  
    original_mood = emotion_state.mood
    updated_state = agent.update_on_message("I love this!", emotion_state)
    assert updated_state.mood > original_mood
    assert updated_state is emotion_state  # Should be same object (mutated)
    
    # Test negative message  
    negative_state = EmotionState()
    agent.update_on_message("This is terrible!", negative_state)
    assert negative_state.mood < 0.5
    
    # Test event application
    event_state = EmotionState()
    result_state = agent.apply_event("Great news!", event_state)
    assert result_state is event_state  # Should be same object
    assert event_state.mood > 0.5
    
    print("✅ EmotionAgent test passed")


def test_logging_system():
    """Test that logging works properly."""
    print("Testing logging system...")
    
    from neurosim.core.logging_config import get_agent_logger
    
    logger = get_agent_logger("TestAgent", "TEST")
    logger.info("Test log message")
    logger.debug("Debug message")
    logger.warning("Warning message")
    
    print("✅ Logging system test passed")


def test_error_handling():
    """Test error handling utilities."""
    print("Testing error handling...")
    
    from neurosim.core.error_handling import handle_exceptions, safe_call, ValidationError
    
    @handle_exceptions(default_return="fallback")
    def failing_function():
        raise ValueError("Test error")
    
    result = failing_function()
    assert result == "fallback"
    
    # Test safe_call
    def divide(a, b):
        return a / b
    
    result = safe_call(divide, 10, 2)
    assert result == 5.0
    
    result = safe_call(divide, 10, 0, default=-1)
    assert result == -1
    
    print("✅ Error handling test passed")


def test_validation():
    """Test input validation."""
    print("Testing validation...")
    
    from neurosim.core.validation import (
        validate_user_message, validate_model_name, 
        validate_temperature, ValidationError
    )
    
    # Test valid inputs
    msg = validate_user_message("  Hello world!  ")
    assert msg == "Hello world!"
    
    model = validate_model_name("gpt-4")
    assert model == "gpt-4"
    
    temp = validate_temperature(0.7)
    assert temp == 0.7
    
    # Test invalid inputs
    try:
        validate_user_message("")
        assert False, "Should have raised ValidationError"
    except ValidationError:
        pass
    
    try:
        validate_temperature(3.0)
        assert False, "Should have raised ValidationError"  
    except ValidationError:
        pass
    
    print("✅ Validation test passed")


if __name__ == "__main__":
    print("Running NeuroSim core functionality tests...\n")
    
    try:
        test_memory_agent_without_vector_store()
        test_emotion_agent()
        test_logging_system()
        test_error_handling()
        test_validation()
        
        print("\n🎉 All core functionality tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
