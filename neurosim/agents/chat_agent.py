"""
Chat agent for NeuroSim.

The chat agent is responsible for orchestrating conversations with the
underlying large language model. It pulls in relevant context from
long-term memory, builds a prompt containing past messages and the
current query, and streams the response back to the caller. After
generating a reply the agent updates the memory log and the emotional
state via the emotion agent.
"""

from __future__ import annotations

from typing import List, Optional

from neurosim.core.config import settings, Settings
from neurosim.core.state import SessionState
from neurosim.core.utils import num_tokens_from_string
from neurosim.core.logging_config import get_agent_logger
from neurosim.agents.emotion_agent import EmotionAgent
from neurosim.agents.memory_agent import MemoryAgent

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


class ChatAgent:
    """High-level conversation orchestrator."""

    def __init__(
        self,
        config: Optional[Settings] = None,
        memory_agent: Optional[MemoryAgent] = None,
        emotion_agent: Optional[EmotionAgent] = None,
    ) -> None:
        self.settings = config or settings
        self.logger = get_agent_logger("ChatAgent", "CHAT")
        
        self.logger.info("Initializing ChatAgent")
        
        # Use provided memory/emotion agents or create local ones
        self.memory_agent = memory_agent or MemoryAgent(self.settings)
        self.emotion_agent = emotion_agent or EmotionAgent(self.settings)
        
        # Initialise chat model
        self.logger.debug(f"Initializing LLM: {self.settings.model} at {self.settings.base_url}")
        self.llm = ChatOpenAI(
            base_url=self.settings.base_url,
            api_key=self.settings.api_key,
            model_name=self.settings.model,
            temperature=self.settings.temperature,
        )

    def _build_messages(self, user_message: str, session_state: SessionState) -> List:
        """Construct the list of chat messages to send to the LLM.

        We include a system message that injects relevant past memory
        content followed by alternating human/assistant messages drawn
        from the session history. Finally we append the current user
        message.
        """
        messages: List = []
        # Inject relevant memories as system context
        docs = self.memory_agent.search_memory(user_message, top_k=self.settings.max_memory_entries)
        if docs:
            memory_context = "\n".join([doc.page_content for doc in docs])
            system_prompt = (
                "The following lines are relevant memories from past interactions. "
                "Use them to inform your answer, but do not mention them explicitly.\n"
                f"{memory_context}"
            )
            messages.append(SystemMessage(content=system_prompt))
            self.logger.debug(f"Added {len(docs)} memory contexts to prompt")

        # Rebuild conversation from history
        for entry in session_state.conversation_history:
            role = entry.get("role")
            content = entry.get("content")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        # Append the latest user message
        messages.append(HumanMessage(content=user_message))
        return messages

    def generate_response(self, user_message: str, session_state: SessionState) -> str:
        """Generate a reply to a user message and update state accordingly."""
        # Build messages for the LLM
        messages = self._build_messages(user_message, session_state)
        # Invoke the model
        try:
            response_message = self.llm.invoke(messages)
            assistant_reply: str = response_message.content
        except Exception as e:
            # Fallback on error
            assistant_reply = "Sorry, something went wrong while generating a response."

        # Update conversation history
        session_state.conversation_history.append({"role": "user", "content": user_message})
        session_state.conversation_history.append({"role": "assistant", "content": assistant_reply})

        # Persist to long-term memory
        self.memory_agent.store_memory(user_message, {"role": "user"})
        self.memory_agent.store_memory(assistant_reply, {"role": "assistant"})

        # Update emotional state based on the reply
        session_state.emotion = self.emotion_agent.update_on_message(
            assistant_reply, session_state.emotion
        )
        return assistant_reply
