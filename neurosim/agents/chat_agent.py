"""
Simplified chat agent for NeuroSim.

In the full project the chat agent would send prompts to a language model
and incorporate retrieved memories and emotional state into its responses.
This stubbed implementation echoes the user's message and demonstrates
interaction with the memory and emotion agents.
"""

from __future__ import annotations

from typing import Optional

from neurosim.core.config import settings, Settings
from neurosim.core.state import SessionState
from neurosim.core.logging_config import get_agent_logger

from neurosim.agents.memory_agent import MemoryAgent
from neurosim.agents.emotion_agent import EmotionAgent
from neurosim.agents.reasoning_agent import ReasoningAgent
from neurosim.plugins.plugin_manager import PluginManager


class ChatAgent:
    """Generate conversational responses and manage memory/emotion."""

    def __init__(self, config: Optional[Settings] = None,
                 memory_agent: Optional[MemoryAgent] = None,
                 emotion_agent: Optional[EmotionAgent] = None) -> None:
        self.settings = config or settings
        self.logger = get_agent_logger("ChatAgent", "CHAT")
        self.logger.info("Initializing simplified ChatAgent")
        self.memory_agent = memory_agent or MemoryAgent(self.settings)
        self.emotion_agent = emotion_agent or EmotionAgent(self.settings)
        # Initialise plugin manager for extensibility
        self.plugin_manager = PluginManager()

    def generate_response(self, message: str, session_state: SessionState) -> str:
        """
        Produce a response for the given user message.

        This stub implementation simply echoes the user's message with a prefix
        and updates memory and emotion accordingly.
        """
        self.logger.debug(f"Received message: {message}")

        # Allow plugins to intercept the message and provide a response. If a
        # plugin returns a response, it supersedes the default behaviour.
        plugin_response = self.plugin_manager.run_plugins(message, session_state)
        if plugin_response is not None:
            reply = plugin_response
        else:
            # Simple reasoning command: if the message begins with '/plan' or 'plan:'
            msg_lower = message.strip().lower()
            if msg_lower.startswith("/plan") or msg_lower.startswith("plan:"):
                # Extract the task description after the command delimiter
                parts = message.split(maxsplit=1)
                task = parts[1] if len(parts) > 1 else ""
                self.logger.debug(f"Delegating reasoning task: {task}")
                reasoning_agent = ReasoningAgent(self.settings)
                reply = reasoning_agent.analyse(task)
            else:
                reply = f"Echo: {message}"

            # Apply mood-based response styling; high mood yields more positive tone,
            # low mood yields more neutral or subdued tone. This must happen after
            # computing the core reply so that modifications reflect current state.
            mood = session_state.emotion.mood
            if mood > 0.7:
                reply = f"😊 {reply}"
            elif mood < 0.3:
                reply = f"😞 {reply}"

        # Update memory
        self.memory_agent.store_memory(message, metadata={"role": "user"})
        self.memory_agent.store_memory(reply, metadata={"role": "assistant"})
        # Update emotion
        self.emotion_agent.update_emotion(session_state, message, reply)
        return reply