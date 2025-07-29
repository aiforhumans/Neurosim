"""
Reasoning agent for NeuroSim.

The reasoning agent uses a specialised prompt to elicit deeper
analysis or planning from the underlying language model. It is
optional and not invoked during normal chat operations unless
explicitly called. This separation allows the main chat agent to
remain responsive while delegating more complex tasks to a separate
chain when necessary.
"""

from __future__ import annotations

from typing import Optional

from neurosim.core.config import settings, Settings
from neurosim.core.logging_config import get_agent_logger

try:
    # ``langchain_openai`` and ``langchain_core`` are optional dependencies. If they
    # are not available the reasoning agent will gracefully fall back to a
    # disabled state. The import is performed lazily here so that the module
    # itself does not fail to import when dependencies are missing.
    from langchain_openai import ChatOpenAI  # type: ignore
    from langchain_core.prompts import PromptTemplate  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    ChatOpenAI = None  # type: ignore
    PromptTemplate = None  # type: ignore


class ReasoningAgent:
    """Encapsulates structured reasoning prompts."""

    def __init__(self, config: Optional[Settings] = None) -> None:
        # Accept a Settings instance or fall back to the module-level settings
        self.settings = config or settings
        self.logger = get_agent_logger("ReasoningAgent", "REASONING")

        self.logger.info("Initializing ReasoningAgent")
        # If the optional dependencies are missing we cannot initialise the LLM. In that
        # case ``self.chain`` will remain ``None`` and calls to ``analyse`` will
        # immediately return a fallback message.
        if ChatOpenAI is None or PromptTemplate is None:
            self.logger.warning(
                "langchain dependencies not available; ReasoningAgent disabled"
            )
            self.llm = None
            self.prompt = None
            self.chain = None
        else:
            # Instantiate the language model
            self.llm = ChatOpenAI(
                base_url=self.settings.base_url,
                api_key=self.settings.api_key,
                model_name=self.settings.model,
                temperature=self.settings.temperature,
            )
            # Define a prompt that encourages step-by-step reasoning
            self.prompt = PromptTemplate(
                input_variables=["task"],
                template=(
                    "You are a logical reasoning assistant. Your job is to break down complex "
                    "tasks into clear, step-by-step plans. Analyse the following task and "
                    "produce a concise plan using numbered steps.\n\n"
                    "Task: {task}\n\n"
                    "Plan:"
                ),
            )
            # Use the new RunnableSequence pattern instead of deprecated LLMChain
            self.chain = self.prompt | self.llm

    def analyse(self, task: str) -> str:
        """Return a structured plan for the given task."""
        # If the chain is not available due to missing dependencies we return early.
        if self.chain is None:
            return "I'm sorry, reasoning functionality is not available."
        self.logger.debug(f"Analyzing task: {task[:100]}...")
        try:
            response = self.chain.invoke({"task": task})
            result = response.content
            self.logger.debug(f"Generated plan with {len(result)} characters")
            return result
        except Exception as e:
            self.logger.error(f"Reasoning analysis failed: {e}")
            return "I'm sorry, I couldn't analyse that task."