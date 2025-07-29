"""
Entry point for the NeuroSim application.

Running this module will start the Gradio web interface. Configuration
can be adjusted by exporting environment variables prefixed with
``NEUROSIM_``. See ``neurosim/core/config.py`` for available
settings.
"""

from __future__ import annotations

from neurosim.core.agent_manager import AgentManager
from neurosim.interface.ui import create_app


def main() -> None:
    """Launch the NeuroSim Gradio app."""
    manager = AgentManager()
    app = create_app(manager)
    # Launch Gradio. Setting share=False runs only on localhost.
    app.launch()


if __name__ == "__main__":
    main()
