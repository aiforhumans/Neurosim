"""
State definitions for NeuroSim.

This module defines a number of dataclasses used to encapsulate the
state of the system. A clear separation between state and behaviour
makes it easier to reason about the system and to persist or inspect
these values separately from the logic that manipulates them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class EmotionState:
    """
    Represents the current emotional state of the AI.

    All emotional dimensions are normalised to the range [0, 1] with
    0 indicating the minimum possible level and 1 indicating the
    maximum possible level. A baseline of 0.5 corresponds to a neutral
    state.
    """

    mood: float = 0.5
    trust: float = 0.5
    energy: float = 0.5

    def as_dict(self) -> Dict[str, float]:
        return {"mood": self.mood, "trust": self.trust, "energy": self.energy}


@dataclass
class Character:
    """
    A character definition describing high-level traits.

    Characters are loaded from JSON files located in the ``data/characters``
    directory. See the provided example file for the expected schema.
    """

    name: str
    traits: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    portrait: Optional[str] = None
    baseline_mood: float = 0.5
    baseline_trust: float = 0.5
    baseline_energy: float = 0.5

    @classmethod
    def from_json(cls, path: Path) -> "Character":
        import json
        data = json.loads(path.read_text())
        return cls(
            name=data.get("name", "Unnamed"),
            traits=data.get("traits", {}),
            description=data.get("description", ""),
            portrait=data.get("portrait"),
            baseline_mood=float(data.get("baseline_mood", 0.5)),
            baseline_trust=float(data.get("baseline_trust", 0.5)),
            baseline_energy=float(data.get("baseline_energy", 0.5)),
        )


@dataclass
class SessionState:
    """
    Holds per-session runtime state.

    A new ``SessionState`` should be created at the beginning of each
    Gradio session. It stores the conversation history, any memory
    context fetched on the current turn, the current emotional state
    and the active character. The Gradio UI will mutate this object
    repeatedly as the user interacts with the app.
    """

    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    memory_context: List[str] = field(default_factory=list)
    emotion: EmotionState = field(default_factory=EmotionState)
    character: Optional[Character] = None

    # Track historical emotion states after each update. The most recent state
    # will be appended to this list by the emotion agent. This allows for
    # visualising how emotions change over time.
    emotion_history: List[EmotionState] = field(default_factory=list)