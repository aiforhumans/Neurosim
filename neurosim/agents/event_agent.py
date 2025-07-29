"""
Event agent for NeuroSim.

The event agent injects occasional random or semi-random events into
the conversation. These events can represent dreams, external
stimuli or other triggers that influence the AI's emotional state
and memory. This implementation adds time-of-day awareness: during
night hours it will select from a set of dream-like events, and
during the day it selects from more mundane stimuli. Consumers can
override the default event lists by subclassing or by modifying the
``day_events`` and ``night_events`` attributes directly.
"""

from __future__ import annotations

import random
from datetime import datetime
from typing import Optional

from neurosim.core.config import settings, Settings


class EventAgent:
    """Generate random events and dreams with context awareness."""

    def __init__(self, config: Optional[Settings] = None) -> None:
        # Accept a Settings instance or default to module-level settings
        self.settings = config or settings

        # Daytime events: more commonplace sensations and recollections
        self.day_events = [
            "You feel a surge of energy as if you have just woken from a nap.",
            "You remember a vivid childhood memory of playing in the rain.",
            "A sudden noise startles you and makes you wary.",
        ]

        # Nighttime events: dream-like or introspective experiences
        self.night_events = [
            "You have a strange dream in which you are flying over mountains.",
            "You recall a moment when someone close to you betrayed your trust.",
            "You hear whispers in the dark around you, though you cannot discern their source.",
        ]

        # Load any user-defined events from a JSON file. The file should
        # contain a JSON array of strings. If the path does not exist or is
        # empty, ``custom_events`` will remain empty. Custom events are
        # selected preferentially over built-in events when available.
        self.custom_events: list[str] = []
        self._load_custom_events()

    def _load_custom_events(self) -> None:
        """Load user-defined events from the configured events file."""
        path = getattr(self.settings, "events_file", "")
        if path and path.exists():
            try:
                import json
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    # Filter to only strings
                    self.custom_events = [str(item) for item in data if isinstance(item, str)]
                    # If successfully loaded, log the number of events
                else:
                    # If the file is not a list, ignore it
                    self.custom_events = []
            except Exception:
                # Silently ignore errors loading custom events
                self.custom_events = []

    def generate_event(self, current_time: Optional[datetime] = None) -> str:
        """
        Return a context-aware random event string.

        If ``current_time`` is not provided, the current system time will be used.
        Between 22:00 and 05:59 inclusive, events are drawn from the
        ``night_events`` list. At other times the ``day_events`` list is used.

        Args:
            current_time: Optional datetime to determine which events to sample from.

        Returns:
            A randomly selected event description.
        """
        if current_time is None:
            current_time = datetime.now()
        hour = current_time.hour

        # Prefer user-defined events if available
        if self.custom_events:
            return random.choice(self.custom_events)

        # Fallback to time-of-day events
        if hour >= 22 or hour < 6:
            events = self.night_events
        else:
            events = self.day_events
        return random.choice(events)