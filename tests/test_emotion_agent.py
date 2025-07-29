"""
Tests for the EmotionAgent.

This module tests the emotion state management and sentiment analysis
functionality of the EmotionAgent class.
"""

import pytest
from unittest.mock import Mock, patch

from neurosim.agents.emotion_agent import EmotionAgent
from neurosim.core.state import EmotionState
from neurosim.core.config import Settings


class TestEmotionAgent:
    """Test cases for EmotionAgent."""

    def test_init_with_default_settings(self):
        """Test EmotionAgent initialization with default settings."""
        agent = EmotionAgent()
        assert agent.settings is not None
        assert hasattr(agent, 'settings')

    def test_init_with_custom_settings(self, test_settings: Settings):
        """Test EmotionAgent initialization with custom settings."""
        agent = EmotionAgent(test_settings)
        assert agent.settings == test_settings

    def test_update_on_message_positive_sentiment(self):
        """Test emotion update with positive sentiment message."""
        agent = EmotionAgent()
        emotion = EmotionState(mood=0.5, trust=0.5, energy=0.5)
        
        # Test with a positive message
        updated_emotion = agent.update_on_message("I'm so happy today!", emotion)
        
        # Mood should increase with positive sentiment
        assert updated_emotion.mood > 0.5
        # Trust should have slight positive change minus decay
        assert updated_emotion.trust >= 0.49  # Allow for small decay
        # Energy should decay slightly
        assert updated_emotion.energy < 0.5

    def test_update_on_message_negative_sentiment(self):
        """Test emotion update with negative sentiment message."""
        agent = EmotionAgent()
        emotion = EmotionState(mood=0.5, trust=0.5, energy=0.5)
        
        # Test with a negative message
        updated_emotion = agent.update_on_message("I'm really upset and angry!", emotion)
        
        # Mood should decrease with negative sentiment
        assert updated_emotion.mood < 0.5
        # Trust should decrease more due to negative sentiment + decay
        assert updated_emotion.trust < 0.5
        # Energy should decrease due to negativity
        assert updated_emotion.energy < 0.5

    def test_update_on_message_neutral_sentiment(self):
        """Test emotion update with neutral sentiment message."""
        agent = EmotionAgent()
        emotion = EmotionState(mood=0.5, trust=0.5, energy=0.5)
        
        # Test with a neutral message
        updated_emotion = agent.update_on_message("The weather is okay.", emotion)
        
        # Mood should stay relatively the same
        assert abs(updated_emotion.mood - 0.5) < 0.05
        # Trust should decrease slightly due to decay
        assert updated_emotion.trust < 0.5
        # Energy should decrease slightly due to decay
        assert updated_emotion.energy < 0.5

    def test_emotion_bounds_enforcement(self):
        """Test that emotion values stay within [0, 1] bounds."""
        agent = EmotionAgent()
        
        # Test lower bound
        emotion = EmotionState(mood=0.0, trust=0.0, energy=0.0)
        updated_emotion = agent.update_on_message("I'm extremely sad!", emotion)
        assert updated_emotion.mood >= 0.0
        assert updated_emotion.trust >= 0.0
        assert updated_emotion.energy >= 0.0
        
        # Test upper bound
        emotion = EmotionState(mood=1.0, trust=1.0, energy=1.0)
        updated_emotion = agent.update_on_message("I'm extremely happy!", emotion)
        assert updated_emotion.mood <= 1.0
        assert updated_emotion.trust <= 1.0
        assert updated_emotion.energy <= 1.0

    def test_apply_event(self):
        """Test applying external events to emotion state."""
        agent = EmotionAgent()
        emotion = EmotionState(mood=0.5, trust=0.5, energy=0.5)
        
        # Apply a positive event
        updated_emotion = agent.apply_event("A beautiful sunset appeared", emotion)
        
        # Should behave like update_on_message
        assert updated_emotion.mood > 0.5

    def test_emotion_state_immutability(self):
        """Test that original emotion state is not modified."""
        agent = EmotionAgent()
        original_emotion = EmotionState(mood=0.5, trust=0.5, energy=0.5)
        original_values = (original_emotion.mood, original_emotion.trust, original_emotion.energy)
        
        # Update emotion
        agent.update_on_message("Test message", original_emotion)
        
        # Original should be unchanged
        assert (original_emotion.mood, original_emotion.trust, original_emotion.energy) == original_values

    @patch('neurosim.core.utils.sentiment_score')
    def test_sentiment_score_integration(self, mock_sentiment):
        """Test integration with sentiment scoring function."""
        mock_sentiment.return_value = 0.8  # Positive sentiment
        
        agent = EmotionAgent()
        emotion = EmotionState(mood=0.5, trust=0.5, energy=0.5)
        
        updated_emotion = agent.update_on_message("Test message", emotion)
        
        # Verify sentiment_score was called
        mock_sentiment.assert_called_once_with("Test message")
        # Mood should increase based on positive sentiment
        assert updated_emotion.mood > 0.5
