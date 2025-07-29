"""
Character editor UI for NeuroSim.

In the full project this module would expose controls for editing
character definitions stored in JSON files. For this simplified
version we merely provide a placeholder to satisfy imports.
"""

from __future__ import annotations

import gradio as gr
from neurosim.core.state import SessionState


def build_character_editor(session_state: SessionState) -> None:
    """Render a placeholder character editor into the current Gradio Blocks context."""
    gr.Markdown("## Character Editor\nThis feature is under construction.")