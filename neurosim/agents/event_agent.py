"""
Event agent for NeuroSim.

The event agent injects occasional random or semi-random events into
the conversation. These events can represent dreams, external
stimuli or other triggers that influence the AI's emotional state
and memory. The implementation here is intentionally simple; more
complex simulations could take time, world state and character traits
into account.
"""

from __future__ import annotations

import random
from typing import Optional

from neurosim.core.config import settings, Settings


class EventAgent:
    """Generate random events and dreams."""

    def __init__(self, config: Optional[Settings] = None) -> None:
        # Accept a Settings instance or default to module-level settings
        self.settings = config or settings
        # A list of example events; developers are encouraged to
        # customise and expand this list for more interesting behaviour.
        self.events = [
            "You remember a vivid childhood memory of playing in the rain.",
            "A sudden noise startles you and makes you wary.",
            "You feel a surge of energy as if you have just woken from a nap.",
            "You have a strange dream in which you are flying over mountains.",
            "You recall a moment when someone close to you betrayed your trust.",
        ]

    def generate_event(self) -> str:
        """Return a random event string."""
        return random.choice(self.events)
