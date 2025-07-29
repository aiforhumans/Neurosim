"""
UI component for editing characters.

This module defines a Gradio-based editor that allows users to view
and modify the JSON definitions for AI characters. Changes are
written directly back to the corresponding file in the
``data/characters`` directory.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple

import gradio as gr

from neurosim.core.config import settings
from neurosim.core.state import Character, SessionState


def build_character_editor(session_state: SessionState) -> gr.Blocks:
    """Create a Gradio interface for editing character definitions."""

    # Gather available character files
    character_files = [p.name for p in settings.characters_dir.glob("*.json")]
    character_files.sort()

    def load_character(file_name: str) -> Tuple[str, str, str, float, float, float]:
        """Load a character file and return its editable fields."""
        path = settings.characters_dir / file_name
        char = Character.from_json(path)
        traits_json = json.dumps(char.traits, indent=2)
        return (
            char.name,
            traits_json,
            char.description,
            char.baseline_mood,
            char.baseline_trust,
            char.baseline_energy,
        )

    def save_character(
        file_name: str,
        name: str,
        traits_str: str,
        description: str,
        baseline_mood: float,
        baseline_trust: float,
        baseline_energy: float,
    ) -> str:
        """Persist the edited character back to disk."""
        try:
            traits = json.loads(traits_str or "{}")
        except json.JSONDecodeError as e:
            return f"Error parsing traits: {e}"
        data = {
            "name": name,
            "traits": traits,
            "description": description,
            "baseline_mood": baseline_mood,
            "baseline_trust": baseline_trust,
            "baseline_energy": baseline_energy,
        }
        path = settings.characters_dir / file_name
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return f"Saved {file_name}"

    with gr.Blocks() as editor:
        gr.Markdown("### Character Editor")
        with gr.Row():
            file_dropdown = gr.Dropdown(
                choices=character_files,
                label="Character File",
                value=character_files[0] if character_files else None,
            )
            status = gr.Markdown("", visible=False)
        with gr.Row():
            name_input = gr.Textbox(label="Name")
            desc_input = gr.Textbox(label="Description")
        traits_input = gr.Textbox(
            label="Traits (JSON)",
            lines=10,
            placeholder="{\n  \"trait_name\": \"value\"\n}",
        )
        with gr.Row():
            mood_slider = gr.Slider(
                minimum=0.0,
                maximum=1.0,
                step=0.01,
                label="Baseline Mood",
            )
            trust_slider = gr.Slider(
                minimum=0.0,
                maximum=1.0,
                step=0.01,
                label="Baseline Trust",
            )
            energy_slider = gr.Slider(
                minimum=0.0,
                maximum=1.0,
                step=0.01,
                label="Baseline Energy",
            )
        save_btn = gr.Button("Save")

        # Wire up callbacks
        def _load(file_name):
            return load_character(file_name)
        file_dropdown.change(
            _load,
            inputs=[file_dropdown],
            outputs=[
                name_input,
                traits_input,
                desc_input,
                mood_slider,
                trust_slider,
                energy_slider,
            ],
        )
        save_btn.click(
            save_character,
            inputs=[
                file_dropdown,
                name_input,
                traits_input,
                desc_input,
                mood_slider,
                trust_slider,
                energy_slider,
            ],
            outputs=[status],
        )
        return editor
