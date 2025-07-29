"""
Simplified emotion agent for NeuroSim.

The emotion agent updates the emotional state of the AI based on
incoming messages and context. In this simplified stub we merely
adjust the mood slightly when the assistant responds, to illustrate
state mutation without implementing a full emotion model.
"""

from __future__ import annotations

from typing import Optional

from neurosim.core.config import settings, Settings
from neurosim.core.state import EmotionState, SessionState
from neurosim.core.logging_config import get_agent_logger


class EmotionAgent:
    """Update the emotional state based on conversation content."""

    def __init__(self, config: Optional[Settings] = None) -> None:
        self.settings = config or settings
        self.logger = get_agent_logger("EmotionAgent", "EMOTION")
        self.logger.info("Initializing simplified EmotionAgent")

    def update_emotion(self, session_state: SessionState, message: str, reply: str) -> None:
        """
        Mutate the session state's emotion based on the latest message and reply.

        This implementation uses a very simple keyword‑based sentiment
        analysis to adjust the ``mood``, ``trust`` and ``energy`` fields on
        ``session_state.emotion``. It also appends a copy of the new
        ``EmotionState`` to ``session_state.emotion_history`` so that
        consumers can plot changes over time.

        Args:
            session_state: The per‑session state that contains the current emotion.
            message: The incoming user message.
            reply: The assistant's reply.
        """
        emotion: EmotionState = session_state.emotion

        # Simple sentiment word lists; in a real implementation you might use
        # a proper sentiment analysis model or lexicon. Words are lowercase.
        positive_words = {"love", "great", "happy", "wonderful", "excited", "good", "amazing", "like"}
        negative_words = {"hate", "bad", "sad", "angry", "tired", "upset", "frustrated", "dislike"}

        def score_text(text: str) -> int:
            score = 0
            for word in text.lower().split():
                if word in positive_words:
                    score += 1
                elif word in negative_words:
                    score -= 1
            return score

        # Combine message and reply sentiment scores
        sentiment_score = score_text(message) + score_text(reply)

        # Adjust mood based on sentiment; each point shifts mood by 0.02
        delta = 0.02 * sentiment_score
        new_mood = max(0.0, min(1.0, emotion.mood + delta))
        self.logger.debug(f"Updating mood from {emotion.mood} to {new_mood} based on sentiment score {sentiment_score}")
        emotion.mood = new_mood

        # Trust increases when assistant provides a reply (simulate positive reinforcement)
        new_trust = max(0.0, min(1.0, emotion.trust + 0.005))
        emotion.trust = new_trust

        # Energy decreases slightly after each turn to simulate fatigue
        new_energy = max(0.0, min(1.0, emotion.energy - 0.01))
        emotion.energy = new_energy

        # Append a copy of the new state to the history
        session_state.emotion_history.append(EmotionState(emotion.mood, emotion.trust, emotion.energy))