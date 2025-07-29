"""
Visualisation components for NeuroSim.

This module exposes a function that returns a Gradio block showing
the current emotional state of the AI. The visualisation uses
matplotlib to create a simple bar chart representing mood, trust and
energy. It is updated on every interaction.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import gradio as gr

from neurosim.core.state import EmotionState, SessionState


def create_emotion_plot(emotion: EmotionState) -> plt.Figure:
    """Return a matplotlib figure representing the emotional state."""
    labels = ["Mood", "Trust", "Energy"]
    values = [emotion.mood, emotion.trust, emotion.energy]
    fig, ax = plt.subplots(figsize=(4, 3))
    bars = ax.bar(labels, values, color=["#ffa500", "#87ceeb", "#98fb98"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Level")
    ax.set_title("Current Emotional State")
    for bar, value in zip(bars, values):
        ax.annotate(
            f"{value:.2f}",
            xy=(bar.get_x() + bar.get_width() / 2, value),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
        )
    fig.tight_layout()
    return fig


def build_visualisation(session_state: SessionState) -> gr.Blocks:
    """Create a Gradio interface for visualising emotions."""
    with gr.Blocks() as vis:
        gr.Markdown("### Emotion Visualisation")
        plot = gr.Plot(value=create_emotion_plot(session_state.emotion))
        return vis
