"""
Agent management for NeuroSim.

The ``AgentManager`` class acts as a registry and orchestrator for the
various agents used in the application. It wires up dependencies
between agents and exposes a simple API for processing user input.

When ``process_message`` is called the manager will:

1. Retrieve context from the memory agent.
2. Generate a response via the chat agent.
3. Update emotional state via the emotion agent.
4. Persist the interaction via the memory agent.
"""

from __future__ import annotations

from typing import Optional

from neurosim.core.config import settings, Settings
from neurosim.core.state import SessionState
from neurosim.agents.emotion_agent import EmotionAgent
from neurosim.agents.memory_agent import MemoryAgent
from neurosim.agents.chat_agent import ChatAgent
from neurosim.agents.reasoning_agent import ReasoningAgent
from neurosim.agents.event_agent import EventAgent


class AgentManager:
    """Central coordination of all agents."""

    def __init__(self, config: Optional[Settings] = None) -> None:
        # Use provided settings or fall back to global settings
        self.settings = config or settings

        # Instantiate agents with shared dependencies
        self.memory_agent = MemoryAgent(self.settings)
        self.emotion_agent = EmotionAgent(self.settings)
        self.chat_agent = ChatAgent(
            self.settings, self.memory_agent, self.emotion_agent
        )
        self.reasoning_agent = ReasoningAgent(self.settings)
        self.event_agent = EventAgent(self.settings)

    def process_message(self, message: str, session_state: SessionState) -> str:
        """
        Process a user message and produce an assistant response.

        Args:
            message: The raw text entered by the user.
            session_state: The current session state object which will be
                mutated as part of handling the message.

        Returns:
            The assistant's reply as a string.
        """
        # Pass the message through the chat agent
        reply = self.chat_agent.generate_response(message, session_state)
        return reply