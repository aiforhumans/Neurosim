"""
Unit tests for the EventAgent.

These tests verify that the time‑based event selection logic in
``EventAgent.generate_event`` chooses events from the appropriate
list depending on the provided time.
"""

import unittest
from datetime import datetime

from neurosim.agents.event_agent import EventAgent


class TestEventAgent(unittest.TestCase):
    def test_day_event_selection(self) -> None:
        agent = EventAgent()
        # 14:00 should be considered daytime
        test_time = datetime(2025, 1, 1, 14, 0)
        event = agent.generate_event(test_time)
        self.assertIn(event, agent.day_events)

    def test_night_event_selection(self) -> None:
        agent = EventAgent()
        # 23:00 should be considered nighttime
        test_time = datetime(2025, 1, 1, 23, 0)
        event = agent.generate_event(test_time)
        self.assertIn(event, agent.night_events)


if __name__ == "__main__":
    unittest.main()