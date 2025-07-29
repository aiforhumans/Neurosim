"""
Emotion agent for NeuroSim.

This agent tracks and updates the AI's emotional state based on
incoming messages and other stimuli. A simple sentiment analysis is
used to adjust the mood dimension, while trust and energy are
modified heuristically. The aim of this agent is not to model
psychologically accurate emotions but rather to provide a plausible
feedback loop that affects responses and visualisations.
"""

from __future__ import annotations

from typing import Optional

from neurosim.core.config import settings, Settings
from neurosim.core.state import EmotionState
from neurosim.core.utils import adjust_emotion, sentiment_score
from neurosim.core.logging_config import get_agent_logger


class EmotionAgent:
    """Manage and update emotional state."""

    def __init__(self, config: Optional[Settings] = None) -> None:
        # Accept a Settings instance or default to module-level settings
        self.settings = config or settings
        self.logger = get_agent_logger("EmotionAgent", "EMOTION")
        self.logger.info("EmotionAgent initialized")

    def update_on_message(self, text: str, emotion_state: EmotionState) -> EmotionState:
        """Update the emotional state in response to a message.

        This function analyses the sentiment of the input text and
        adjusts the mood accordingly. It also applies mild decay to
        trust and energy to simulate fatigue over time.

        Args:
            text: The text to analyse.
            emotion_state: The current emotion state to update.

        Returns:
            The updated emotion state.
        """
        # Analyse sentiment and adjust mood
        polarity = sentiment_score(text)
        self.logger.debug(f"Sentiment analysis: polarity={polarity:.3f}")
        
        # Scale sentiment into a gentle adjustment
        mood_change = polarity * 0.1
        old_mood = emotion_state.mood
        emotion_state.mood = adjust_emotion(emotion_state.mood, mood_change)

        # Decay trust slightly with each interaction; more negative
        # messages will erode trust faster. Conversely, positive
        # sentiment will bolster trust a bit.
        trust_change = polarity * 0.05 - 0.01
        old_trust = emotion_state.trust
        emotion_state.trust = adjust_emotion(emotion_state.trust, trust_change)

        # Energy decays very slightly; heavy negativity drains energy
        energy_change = -0.005 + (-polarity * 0.02)
        old_energy = emotion_state.energy
        emotion_state.energy = adjust_emotion(emotion_state.energy, energy_change)
        
        self.logger.debug(f"Emotion state updated: mood {old_mood:.2f}→{emotion_state.mood:.2f}, "
                         f"trust {old_trust:.2f}→{emotion_state.trust:.2f}, "
                         f"energy {old_energy:.2f}→{emotion_state.energy:.2f}")
        
        return emotion_state

    def apply_event(self, event_text: str, emotion_state: EmotionState) -> EmotionState:
        """Apply the emotional impact of an external event.

        External events (dreams, random triggers) can be used to mix
        things up. For now we simply reuse the sentiment analysis and
        treat events similarly to messages, but additional logic could
        be added here to weight the changes differently or respond to
        specific keywords.
        """
        self.logger.info(f"Applying emotional event: {event_text}")
        return self.update_on_message(event_text, emotion_state)
