"""
Visualisation utilities for NeuroSim.

This module defines functions that produce plots and other visual
representations of the AI's internal state. In the simplified
implementation we provide a dummy emotion plot using matplotlib.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import gradio as gr
from neurosim.core.state import SessionState, EmotionState


def create_emotion_plot(emotion: EmotionState):
    """Return a matplotlib figure representing the current emotional state."""
    fig, ax = plt.subplots(figsize=(4, 2))
    labels = ["Mood", "Trust", "Energy"]
    values = [emotion.mood, emotion.trust, emotion.energy]
    ax.bar(labels, values, color=["tab:blue", "tab:orange", "tab:green"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Level")
    ax.set_title("Emotion State")
    return fig


def build_visualisation(session_state: SessionState) -> None:
    """Render a placeholder visualisation into the current Gradio Blocks context."""
    # Show the current emotion state as a bar plot
    gr.Plot(value=create_emotion_plot(session_state.emotion), label="Emotion State")