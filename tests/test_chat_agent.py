"""
Tests for the ChatAgent.

This module tests the LLM orchestration and message processing
functionality of the ChatAgent class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from neurosim.agents.chat_agent import ChatAgent
from neurosim.core.config import Settings
from neurosim.core.state import SessionState, EmotionState
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.documents import Document


class TestChatAgent:
    """Test cases for ChatAgent."""

    @patch('neurosim.agents.chat_agent.ChatOpenAI')
    def test_init_with_custom_config(self, mock_chat_openai, test_settings: Settings):
        """Test ChatAgent initialization with custom settings."""
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        agent = ChatAgent(test_settings)
        
        # Should initialize with correct settings (note: parameter is model_name, not model)
        mock_chat_openai.assert_called_once_with(
            base_url=test_settings.base_url,
            model_name=test_settings.model,
            api_key=test_settings.api_key,
            temperature=test_settings.temperature
        )
        assert agent.llm == mock_llm

    @patch('neurosim.agents.chat_agent.ChatOpenAI')
    def test_generate_response_success(self, mock_chat_openai, test_settings: Settings, session_state: SessionState):
        """Test successful response generation."""
        # Setup mocks
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "I can help you with that!"
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm
        
        mock_memory_agent = Mock()
        mock_memory_agent.search_memory.return_value = [
            Document(page_content="Previous conversation about weather", metadata={"role": "user"})
        ]
        
        mock_emotion_agent = Mock()
        mock_emotion_agent.update_on_message.return_value = EmotionState(mood=0.7, trust=0.8, energy=0.6)
        
        agent = ChatAgent(test_settings)
        
        response = agent.generate_response(
            user_message="How are you today?",
            session_state=session_state
        )
        
        # Verify response
        assert response == "I can help you with that!"
        
        # Verify memory search was called
        mock_memory_agent.search_memory.assert_called_once_with("How are you today?")
        
        # Verify memory storage was called for both messages
        assert mock_memory_agent.store_memory.call_count == 2
        
        # Verify emotion update was called
        mock_emotion_agent.update_on_message.assert_called_once()
        
        # Verify session state was updated
        assert len(session_state.conversation_history) == 2
        assert session_state.conversation_history[0]["role"] == "user"
        assert session_state.conversation_history[1]["role"] == "assistant"

    @patch('neurosim.agents.chat_agent.ChatOpenAI')
    def test_generate_response_with_memory_context(self, mock_chat_openai, test_settings: Settings, session_state: SessionState):
        """Test response generation includes memory context."""
        # Setup mocks
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Based on our previous conversation..."
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm
        
        mock_memory_agent = Mock()
        mock_memory_agent.search_memory.return_value = [
            Document(page_content="User mentioned they like coffee", metadata={"role": "user"}),
            Document(page_content="I recommended a coffee shop", metadata={"role": "assistant"})
        ]
        
        mock_emotion_agent = Mock()
        mock_emotion_agent.update_on_message.return_value = EmotionState()
        
        agent = ChatAgent(test_settings, memory_agent=mock_memory_agent, emotion_agent=mock_emotion_agent)
        
        agent.generate_response(
            user_message="What do you remember about my preferences?",
            session_state=session_state
        )
        
        # Verify LLM was called with memory context
        call_args = mock_llm.invoke.call_args[0][0]  # Get the messages list
        
        # Should have system message with memory context
        system_messages = [msg for msg in call_args if isinstance(msg, SystemMessage)]
        assert len(system_messages) > 0
        
        # Memory context should be included in system message
        system_content = system_messages[0].content
        assert "User mentioned they like coffee" in system_content
        assert "I recommended a coffee shop" in system_content

    @patch('neurosim.agents.chat_agent.ChatOpenAI')
    def test_generate_response_llm_exception(self, mock_chat_openai, test_settings: Settings, session_state: SessionState):
        """Test response generation handles LLM exceptions gracefully."""
        # Setup mocks
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("LLM connection error")
        mock_chat_openai.return_value = mock_llm
        
        mock_memory_agent = Mock()
        mock_memory_agent.search_memory.return_value = []
        
        mock_emotion_agent = Mock()
        mock_emotion_agent.update_on_message.return_value = EmotionState()
        
        agent = ChatAgent(test_settings, memory_agent=mock_memory_agent, emotion_agent=mock_emotion_agent)
        
        response = agent.generate_response(
            user_message="Hello",
            session_state=session_state
        )
        
        # Should return fallback message
        assert response == "Sorry, something went wrong while generating a response."
        
        # Session state should still be updated with user message
        assert len(session_state.conversation_history) == 1
        assert session_state.conversation_history[0]["role"] == "user"

    @patch('neurosim.agents.chat_agent.ChatOpenAI')
    def test_generate_response_character_integration(self, mock_chat_openai, test_settings: Settings, session_state: SessionState):
        """Test response generation integrates character information."""
        # Setup character in session state
        # Create character for testing
        from neurosim.core.state import Character
        session_state.character = Character(
            name="Alice",
            traits={"personality": "friendly", "style": "helpful"},
            baseline_mood=0.8
        )
        
        # Setup mocks
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Hi there! I'm Alice."
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm
        
        mock_memory_agent = Mock()
        mock_memory_agent.search_memory.return_value = []
        
        mock_emotion_agent = Mock()
        mock_emotion_agent.update_on_message.return_value = EmotionState()
        
        agent = ChatAgent(test_settings, memory_agent=mock_memory_agent, emotion_agent=mock_emotion_agent)
        
        agent.generate_response(
            user_message="Hello",
            session_state=session_state
        )
        
        # Verify LLM was called with character context
        call_args = mock_llm.invoke.call_args[0][0]  # Get the messages list
        
        # Should have system message with character information
        system_messages = [msg for msg in call_args if isinstance(msg, SystemMessage)]
        assert len(system_messages) > 0
        
        system_content = system_messages[0].content
        assert "Alice" in system_content
        assert "friendly" in system_content
        assert "helpful" in system_content

    @patch('neurosim.agents.chat_agent.ChatOpenAI')
    def test_generate_response_emotion_integration(self, mock_chat_openai, test_settings: Settings, session_state: SessionState):
        """Test response generation integrates emotional state."""
        # Setup emotional state
        session_state.emotion = EmotionState(mood=0.3, trust=0.2, energy=0.9)
        
        # Setup mocks
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "I'm feeling a bit down today."
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm
        
        mock_memory_agent = Mock()
        mock_memory_agent.search_memory.return_value = []
        
        mock_emotion_agent = Mock()
        mock_emotion_agent.update_on_message.return_value = EmotionState(mood=0.4, trust=0.3, energy=0.8)
        
        agent = ChatAgent(test_settings, memory_agent=mock_memory_agent, emotion_agent=mock_emotion_agent)
        
        agent.generate_response(
            user_message="How are you feeling?",
            session_state=session_state
        )
        
        # Verify emotion state was updated in session
        assert session_state.emotion.mood == 0.4
        assert session_state.emotion.trust == 0.3
        assert session_state.emotion.energy == 0.8

    @patch('neurosim.agents.chat_agent.ChatOpenAI')
    def test_generate_response_message_structure(self, mock_chat_openai, test_settings: Settings, session_state: SessionState):
        """Test that generated messages have correct structure for Gradio."""
        # Setup mocks
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm
        
        mock_memory_agent = Mock()
        mock_memory_agent.search_memory.return_value = []
        
        mock_emotion_agent = Mock()
        mock_emotion_agent.update_on_message.return_value = EmotionState()
        
        agent = ChatAgent(test_settings, memory_agent=mock_memory_agent, emotion_agent=mock_emotion_agent)
        
        agent.generate_response(
            user_message="Hello",
            session_state=session_state
        )
        
        # Verify conversation history has correct Gradio message format
        assert len(session_state.conversation_history) == 2
        
        user_msg = session_state.conversation_history[0]
        assert user_msg["role"] == "user"
        assert user_msg["content"] == "Hello"
        
        assistant_msg = session_state.conversation_history[1]
        assert assistant_msg["role"] == "assistant"
        assert assistant_msg["content"] == "Test response"
