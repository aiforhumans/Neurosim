"""
Unit tests for the ReasoningAgent.

These tests focus on error handling. They configure the ReasoningAgent
with an invalid base URL so that calls to the language model fail,
ensuring that the fallback message is returned instead of raising.
"""

import unittest

from neurosim.agents.reasoning_agent import ReasoningAgent
from neurosim.core.config import Settings


class TestReasoningAgent(unittest.TestCase):
    def test_reasoning_agent_handles_errors(self) -> None:
        # Use an obviously invalid URL to force an error when invoking the chain
        config = Settings(base_url="http://invalid.example")
        agent = ReasoningAgent(config)
        plan = agent.analyse("Test task")
        # The agent should return a non-empty string even if analysis fails or is unavailable
        self.assertIsInstance(plan, str)
        self.assertNotEqual(plan, "")


if __name__ == "__main__":
    unittest.main()